import pandas as pd
from app.models import ETLLog
from datetime import datetime
import re
import json

def clean_column_name(col):
    """Clean a column name: lowercase, replace spaces with underscores, remove special chars"""
    # Convert to lowercase
    col = str(col).lower()
    # Replace spaces and hyphens with underscores
    col = re.sub(r'[\s\-]+', '_', col)
    # Remove special characters except underscores
    col = re.sub(r'[^\w]', '', col)
    # Remove leading/trailing underscores
    col = col.strip('_')
    # Replace multiple underscores with single
    col = re.sub(r'_+', '_', col)
    return col


def flatten_nested_data(df):
    """Flatten nested dictionaries and lists in DataFrame columns"""
    flattened_df = df.copy()
    
    for col in df.columns:
        # Check if column contains dict or list objects
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            try:
                # Convert dicts/lists to JSON strings
                flattened_df[col] = df[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
                )
            except Exception:
                # If JSON conversion fails, convert to string
                flattened_df[col] = df[col].astype(str)
    
    return flattened_df


def transform_data(df, etl_run, db):
    """Transform the extracted data"""
    try:
        # Log transformation start
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='transform',
            message='Starting data transformation',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        initial_rows = len(df)
        
        # Clean column names
        original_columns = df.columns.tolist()
        df.columns = [clean_column_name(col) for col in df.columns]
        cleaned_columns = df.columns.tolist()
        
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='transform',
            message=f'Cleaned column names: {len(original_columns)} columns processed',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        # Flatten nested data structures (dicts, lists) to JSON strings
        nested_cols = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, (dict, list))).any()]
        if nested_cols:
            df = flatten_nested_data(df)
            log = ETLLog(
                etl_run_id=etl_run.id,
                stage='transform',
                message=f'Flattened {len(nested_cols)} nested columns to JSON strings: {", ".join(nested_cols)}',
                log_level='info',
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        
        # Drop rows that are completely empty
        df_before_drop = len(df)
        df = df.dropna(how='all')
        rows_dropped = df_before_drop - len(df)
        
        if rows_dropped > 0:
            log = ETLLog(
                etl_run_id=etl_run.id,
                stage='transform',
                message=f'Dropped {rows_dropped} completely empty rows',
                log_level='info',
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        
        # Reset index after dropping rows
        df = df.reset_index(drop=True)
        
        final_rows = len(df)
        
        # Log success
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='transform',
            message=f'Transformation completed: {initial_rows} -> {final_rows} rows',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        etl_run.rows_transformed = final_rows
        db.session.commit()
        
        return df, None
    
    except Exception as e:
        error_msg = f'Transformation failed: {str(e)}'
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='transform',
            message=error_msg,
            log_level='error',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return None, error_msg
