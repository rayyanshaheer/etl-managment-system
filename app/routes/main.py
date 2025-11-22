from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Job

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template('index.html', jobs=jobs)


@bp.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.created_at.desc()).all()
    total_jobs = len(jobs)
    
    # Count successful runs
    from app.models import ETLRun
    successful_runs = ETLRun.query.join(Job).filter(
        Job.user_id == current_user.id,
        ETLRun.status == 'success'
    ).count()
    
    return render_template('dashboard.html', 
                         jobs=jobs, 
                         total_jobs=total_jobs,
                         successful_runs=successful_runs)
