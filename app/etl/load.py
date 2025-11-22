import pandas as pd
from sqlalchemy import create_engine, inspect, text
from app.models import ETLLog
from datetime import datetime
from flask import current_app

def load_data(df, table_name, etl_run, db):
    """Load transformed data into SQLite database"""
    try:
        # Log load start
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='load',
            message=f'Starting data load to table: {table_name}',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        # Create SQLAlchemy engine
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        
        # Check if table exists and drop it (replace mode)
        inspector = inspect(engine)
        if table_name in inspector.get_table_names():
            with engine.connect() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
                conn.commit()
            
            log = ETLLog(
                etl_run_id=etl_run.id,
                stage='load',
                message=f'Dropped existing table: {table_name}',
                log_level='info',
                timestamp=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        
        # Load data to SQLite
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        rows_loaded = len(df)
        
        # Log success
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='load',
            message=f'Successfully loaded {rows_loaded} rows to table: {table_name}',
            log_level='info',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        etl_run.rows_loaded = rows_loaded
        db.session.commit()
        
        return None
    
    except Exception as e:
        error_msg = f'Load failed: {str(e)}'
        log = ETLLog(
            etl_run_id=etl_run.id,
            stage='load',
            message=error_msg,
            log_level='error',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return error_msg
