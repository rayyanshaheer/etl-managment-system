import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from app.models import ETLLog
from datetime import datetime
import time

def extract_from_csv(file_path, etl_run, db):
    """Extract data from a CSV file"""
    try:
        # Log extraction start
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=f'Starting CSV extraction from {file_path}',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        # Read CSV file
        df = pd.read_csv(file_path)
        row_count = len(df)
        
        # Log success
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=f'Successfully extracted {row_count} rows from CSV',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        etl_run.rows_extracted = row_count
        db.session.commit()
        
        return df, None
    
    except Exception as e:
        error_msg = f'CSV extraction failed: {str(e)}'
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=error_msg,
            log_level='error',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return None, error_msg


def extract_from_api(api_url, api_format, etl_run, db):
    """Extract data from an API endpoint with retry logic"""
    try:
        # Log extraction start
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=f'Starting API extraction from {api_url}',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        # Setup session with retry strategy
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
            allowed_methods=["GET"]  # Only retry GET requests
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Log retry attempt
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message='Attempting API request with retry strategy (3 retries, 10s timeout)',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        # Fetch data from API with reduced timeout
        response = session.get(api_url, timeout=10)
        response.raise_for_status()
        
        # Parse based on format
        if api_format == 'json':
            data = response.json()
            
            # If single dict is returned (not a list), wrap it in a list
            if isinstance(data, dict) and not any(isinstance(v, list) for v in data.values()):
                # Check if it's a single record (not containing array fields)
                data = [data]
                log = ETLLog(
                    etl_run_id=etl_run.id,
                    stage='extract',
                    message='API returned single object, converted to list with 1 record',
                    log_level='info',
                    timestamp=datetime.utcnow()
                )
                db.session.add(log)
                db.session.commit()
            elif isinstance(data, dict):
                # Try common keys for data arrays
                for key in ['data', 'results', 'items', 'records']:
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        log = ETLLog(
                            etl_run_id=etl_run.id,
                            stage='extract',
                            message=f'Extracted data from "{key}" field in response',
                            log_level='info',
                            timestamp=datetime.utcnow()
                        )
                        db.session.add(log)
                        db.session.commit()
                        break
            
            df = pd.DataFrame(data)
        elif api_format == 'csv':
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
        else:
            raise ValueError(f'Unsupported API format: {api_format}')
        
        row_count = len(df)
        
        # Log success
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=f'Successfully extracted {row_count} rows from API',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        etl_run.rows_extracted = row_count
        db.session.commit()
        
        return df, None
    
    except requests.RequestException as e:
        error_msg = f'API request failed: {str(e)}'
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=error_msg,
            log_level='error',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return None, error_msg
    
    except Exception as e:
        error_msg = f'API extraction failed: {str(e)}'
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=error_msg,
            log_level='error',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return None, error_msg


def extract_data(data_source, etl_run, db):
    """Main extraction function that routes to the appropriate extractor"""
    if data_source.source_type == 'csv':
        return extract_from_csv(data_source.file_path, etl_run, db)
    elif data_source.source_type == 'api':
        return extract_from_api(data_source.api_url, data_source.api_format, etl_run, db)
    else:
        error_msg = f'Unknown source type: {data_source.source_type}'
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='extract',
            message=error_msg,
            log_level='error',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return None, error_msg
