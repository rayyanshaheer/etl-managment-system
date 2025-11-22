from app import create_app, db
from app.models import User, Job, DataSource, ETLRun, ETLLog

app = create_app()

with app.app_context():
    db.create_all()
    print("All tables created successfully!")