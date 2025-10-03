"""
Database Update Script
Run this to add new tables: UserProfile, ResumeAnalysis, and SavedJob
"""

from app import app, db

with app.app_context():
    print("Creating new database tables...")
    db.create_all()
    print("Database tables created successfully!")
    print("\nNew tables added:")
    print("  - UserProfile: Stores user profile information")
    print("  - ResumeAnalysis: Stores resume analysis history")
    print("  - SavedJob: Stores saved/bookmarked jobs")
