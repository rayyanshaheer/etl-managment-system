from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Job, ETLRun, ETLLog
from app.etl import extract_data, transform_data, load_data
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from flask import current_app

bp = Blueprint('etl', __name__, url_prefix='/etl')

@bp.route('/run/<int:job_id>', methods=['POST'])
@login_required
def run_etl(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    # Create ETL run record
    etl_run = ETLRun(
        job_id=job.id,
        status='running',
        started_at=datetime.utcnow()
    )
    db.session.add(etl_run)
    db.session.commit()
    
    try:
        # Extract
        df, error = extract_data(job.data_source, etl_run, db)
        if error:
            etl_run.status = 'failed'
            etl_run.error_message = error
            etl_run.completed_at = datetime.utcnow()
            db.session.commit()
            flash(f'ETL failed during extraction: {error}', 'danger')
            return redirect(url_for('jobs.view_job', job_id=job.id))
        
        # Transform
        df, error = transform_data(df, etl_run, db)
        if error:
            etl_run.status = 'failed'
            etl_run.error_message = error
            etl_run.completed_at = datetime.utcnow()
            db.session.commit()
            flash(f'ETL failed during transformation: {error}', 'danger')
            return redirect(url_for('jobs.view_job', job_id=job.id))
        
        # Load
        error = load_data(df, job.table_name, etl_run, db, job.load_mode)
        if error:
            etl_run.status = 'failed'
            etl_run.error_message = error
            etl_run.completed_at = datetime.utcnow()
            db.session.commit()
            flash(f'ETL failed during loading: {error}', 'danger')
            return redirect(url_for('jobs.view_job', job_id=job.id))
        
        # Success
        etl_run.status = 'success'
        etl_run.completed_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'ETL pipeline completed successfully! Processed {etl_run.rows_loaded} rows.', 'success')
        return redirect(url_for('etl.view_data', job_id=job.id))
    
    except Exception as e:
        etl_run.status = 'failed'
        etl_run.error_message = str(e)
        etl_run.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Log the error
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='general',
            message=f'Unexpected error: {str(e)}',
            log_level='error',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'ETL pipeline failed: {str(e)}', 'danger')
        return redirect(url_for('jobs.view_job', job_id=job.id))


@bp.route('/data/<int:job_id>')
@login_required
def view_data(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    if not job.table_name:
        flash('No data table exists for this job', 'warning')
        return redirect(url_for('jobs.view_job', job_id=job.id))
    
    try:
        # Read data from the job's table
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{job.table_name}'"
            ))
            if not result.fetchone():
                flash('Data table does not exist. Please run the ETL pipeline first.', 'warning')
                return redirect(url_for('jobs.view_job', job_id=job.id))
        
        # Read data with limit for display
        df = pd.read_sql_table(job.table_name, engine)
        
        # Convert to HTML table
        if len(df) > 0:
            # Limit to first 100 rows for display
            display_df = df.head(100)
            table_html = display_df.to_html(classes='table table-striped table-bordered table-hover', 
                                           index=False, 
                                           escape=False)
            total_rows = len(df)
            columns = df.columns.tolist()
        else:
            table_html = None
            total_rows = 0
            columns = []
        
        return render_template('etl/view_data.html', 
                             job=job, 
                             table_html=table_html,
                             total_rows=total_rows,
                             columns=columns)
    
    except Exception as e:
        flash(f'Error reading data: {str(e)}', 'danger')
        return redirect(url_for('jobs.view_job', job_id=job.id))


@bp.route('/logs/<int:run_id>')
@login_required
def view_logs(run_id):
    etl_run = ETLRun.query.get_or_404(run_id)
    
    # Verify user owns this job
    if etl_run.job.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    logs = ETLLog.query.filter_by(etl_run_id=run_id).order_by(ETLLog.timestamp.asc()).all()
    
    return render_template('etl/view_logs.html', etl_run=etl_run, logs=logs)


@bp.route('/logs')
@login_required
def logs_overview():
    # Get filter parameters
    job_id = request.args.get('job_id', type=int)
    status = request.args.get('status')
    stage = request.args.get('stage')
    
    # Get all user's jobs for filter dropdown
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.name.asc()).all()
    
    # Base query - only get runs for current user's jobs
    query = ETLRun.query.join(Job).filter(Job.user_id == current_user.id)
    
    # Apply filters
    if job_id:
        query = query.filter(ETLRun.job_id == job_id)
    if status:
        query = query.filter(ETLRun.status == status)
    
    # Get ETL runs
    etl_runs = query.order_by(ETLRun.started_at.desc()).all()
    
    # Get statistics
    total_runs = len(etl_runs)
    successful_runs = sum(1 for run in etl_runs if run.status == 'success')
    failed_runs = sum(1 for run in etl_runs if run.status == 'failed')
    
    # Get recent logs
    logs_query = ETLLog.query.join(ETLRun).join(Job).filter(Job.user_id == current_user.id)
    
    # Apply stage filter to logs
    if stage:
        logs_query = logs_query.filter(ETLLog.stage == stage)
    
    # Get recent logs (last 50)
    recent_logs = logs_query.order_by(ETLLog.timestamp.desc()).limit(50).all()
    total_logs = logs_query.count()
    
    return render_template('etl/logs_overview.html',
                         jobs=jobs,
                         etl_runs=etl_runs,
                         recent_logs=recent_logs,
                         total_runs=total_runs,
                         successful_runs=successful_runs,
                         failed_runs=failed_runs,
                         total_logs=total_logs)
