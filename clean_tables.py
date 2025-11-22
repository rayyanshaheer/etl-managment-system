from app import create_app, db
from app.models import User, Job, DataSource, ETLRun, ETLLog

app = create_app()

with app.app_context():
    # Delete in reverse order of dependencies to avoid foreign key constraints
    try:
        # Delete ETL logs first
        db.session.query(ETLLog).delete()
        print("ETL logs cleared.")

        # Delete ETL runs
        db.session.query(ETLRun).delete()
        print("ETL runs cleared.")

        # Delete data sources
        db.session.query(DataSource).delete()
        print("Data sources cleared.")

        # Delete jobs
        db.session.query(Job).delete()
        print("Jobs cleared.")

        # Delete users last
        db.session.query(User).delete()
        print("Users cleared.")

        # Commit the changes
        db.session.commit()
        print("All tables cleaned successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"Error cleaning tables: {e}")