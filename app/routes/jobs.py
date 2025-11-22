from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Job, DataSource, ETLRun
from app.utils import save_uploaded_file, generate_table_name, validate_url
from datetime import datetime, timedelta

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@bp.route('/')
@login_required
def list_jobs():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template('jobs/list.html', jobs=jobs)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_job():
    if request.method == 'POST':
        job_name = request.form.get('job_name')
        description = request.form.get('description')
        source_type = request.form.get('source_type')
        
        # Validation
        if not job_name or not source_type:
            flash('Job name and source type are required', 'danger')
            return render_template('jobs/create.html')
        
        if source_type not in ['csv', 'api']:
            flash('Invalid source type', 'danger')
            return render_template('jobs/create.html')
        
        # Get load mode
        load_mode = request.form.get('load_mode', 'replace')
        
        # Create job
        job = Job(
            name=job_name,
            description=description,
            user_id=current_user.id,
            load_mode=load_mode
        )
        db.session.add(job)
        db.session.flush()  # Get job.id without committing
        
        # Generate table name
        job.table_name = generate_table_name(job_name, job.id)
        
        # Create data source
        data_source = DataSource(job_id=job.id, source_type=source_type)
        
        if source_type == 'csv':
            # Handle CSV upload
            if 'csv_file' not in request.files:
                db.session.rollback()
                flash('No file uploaded', 'danger')
                return render_template('jobs/create.html')
            
            file = request.files['csv_file']
            if file.filename == '':
                db.session.rollback()
                flash('No file selected', 'danger')
                return render_template('jobs/create.html')
            
            filepath = save_uploaded_file(file, job.id)
            if not filepath:
                db.session.rollback()
                flash('Invalid file type. Only CSV files are allowed.', 'danger')
                return render_template('jobs/create.html')
            
            data_source.file_path = filepath
        
        elif source_type == 'api':
            # Handle API source
            api_url = request.form.get('api_url')
            api_format = request.form.get('api_format')
            
            if not api_url or not api_format:
                db.session.rollback()
                flash('API URL and format are required', 'danger')
                return render_template('jobs/create.html')
            
            if not validate_url(api_url):
                db.session.rollback()
                flash('Invalid API URL', 'danger')
                return render_template('jobs/create.html')
            
            if api_format not in ['json', 'csv']:
                db.session.rollback()
                flash('Invalid API format', 'danger')
                return render_template('jobs/create.html')
            
            data_source.api_url = api_url
            data_source.api_format = api_format
        
        db.session.add(data_source)
        db.session.commit()
        
        flash(f'Job "{job_name}" created successfully!', 'success')
        return redirect(url_for('jobs.view_job', job_id=job.id))
    
    return render_template('jobs/create.html')


@bp.route('/<int:job_id>')
@login_required
def view_job(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    # Clean up stuck "running" jobs (running for more than 5 minutes)
    stuck_threshold = datetime.utcnow() - timedelta(minutes=5)
    stuck_runs = ETLRun.query.filter(
        ETLRun.job_id == job.id,
        ETLRun.status == 'running',
        ETLRun.started_at < stuck_threshold
    ).all()
    
    if stuck_runs:
        from app.models import ETLLog
        for run in stuck_runs:
            run.status = 'failed'
            run.completed_at = datetime.utcnow()
            run.error_message = 'Job timed out after 5 minutes (auto-cancelled)'
            
            # Add log entry
            log = ETLLog(
                etl_run_id=run.id,
                stage='general',
                message='Job automatically cancelled due to timeout (exceeded 5 minutes)',
                log_level='error',
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
        
        db.session.commit()
        flash(f'Cleaned up {len(stuck_runs)} stuck job(s)', 'info')
    
    etl_runs = ETLRun.query.filter_by(job_id=job.id).order_by(ETLRun.started_at.desc()).all()
    return render_template('jobs/view.html', job=job, etl_runs=etl_runs)


@bp.route('/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    job_name = job.name
    
    # Delete associated file if exists
    if job.data_source and job.data_source.file_path:
        import os
        try:
            if os.path.exists(job.data_source.file_path):
                os.remove(job.data_source.file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    db.session.delete(job)
    db.session.commit()
    
    flash(f'Job "{job_name}" deleted successfully', 'success')
    return redirect(url_for('jobs.list_jobs'))


@bp.route('/cleanup-stuck', methods=['POST'])
@login_required
def cleanup_stuck_jobs():
    """Clean up all stuck 'running' jobs for the current user"""
    from app.models import ETLLog
    
    # Find stuck jobs (running for more than 5 minutes)
    stuck_threshold = datetime.utcnow() - timedelta(minutes=5)
    stuck_runs = ETLRun.query.join(Job).filter(
        Job.user_id == current_user.id,
        ETLRun.status == 'running',
        ETLRun.started_at < stuck_threshold
    ).all()
    
    if stuck_runs:
        for run in stuck_runs:
            run.status = 'failed'
            run.completed_at = datetime.utcnow()
            run.error_message = 'Job timed out after 5 minutes (auto-cancelled)'
            
            # Add log entry
            log = ETLLog(
                etl_run_id=run.id,
                stage='general',
                message='Job automatically cancelled due to timeout (exceeded 5 minutes)',
                log_level='error',
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
        
        db.session.commit()
        flash(f'Successfully cleaned up {len(stuck_runs)} stuck job(s)', 'success')
    else:
        flash('No stuck jobs found', 'info')
    
    return redirect(request.referrer or url_for('jobs.list_jobs'))
