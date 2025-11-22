from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    jobs = db.relationship('Job', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    table_name = db.Column(db.String(100), unique=True)  # Name of the table where data is loaded
    
    data_source = db.relationship('DataSource', backref='job', uselist=False, cascade='all, delete-orphan')
    etl_runs = db.relationship('ETLRun', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Job {self.name}>'


class DataSource(db.Model):
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    source_type = db.Column(db.String(20), nullable=False)  # 'csv' or 'api'
    
    # For CSV uploads
    file_path = db.Column(db.String(500))
    
    # For API sources
    api_url = db.Column(db.String(500))
    api_format = db.Column(db.String(20))  # 'json' or 'csv'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataSource {self.source_type} for Job {self.job_id}>'


class ETLRun(db.Model):
    __tablename__ = 'etl_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'running', 'success', 'failed'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    rows_extracted = db.Column(db.Integer, default=0)
    rows_transformed = db.Column(db.Integer, default=0)
    rows_loaded = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    
    logs = db.relationship('ETLLog', backref='etl_run', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ETLRun {self.id} - {self.status}>'


class ETLLog(db.Model):
    __tablename__ = 'etl_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    etl_run_id = db.Column(db.Integer, db.ForeignKey('etl_runs.id'), nullable=False)
    stage = db.Column(db.String(20), nullable=False)  # 'extract', 'transform', 'load'
    message = db.Column(db.Text, nullable=False)
    log_level = db.Column(db.String(20), default='info')  # 'info', 'warning', 'error'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ETLLog {self.stage} - {self.log_level}>'
