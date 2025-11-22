import os
from werkzeug.utils import secure_filename
from flask import current_app
import re

ALLOWED_EXTENSIONS = {'csv', 'txt'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, job_id):
    """Save an uploaded file and return the file path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add job_id prefix to avoid conflicts
        filename = f'job_{job_id}_{filename}'
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None


def generate_table_name(job_name, job_id):
    """Generate a safe table name from job name and ID"""
    # Clean the job name
    table_name = re.sub(r'[^\w\s]', '', job_name)
    table_name = re.sub(r'\s+', '_', table_name)
    table_name = table_name.lower().strip('_')
    # Add job ID to ensure uniqueness
    table_name = f'etl_data_{table_name}_{job_id}'
    return table_name


def validate_url(url):
    """Basic URL validation"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None
