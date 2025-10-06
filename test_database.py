#!/usr/bin/env python3
"""
Test script to verify database setup
"""
import os
import sys

# Add src/web_app to path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WEB_APP_DIR = os.path.join(BASE_DIR, 'src', 'web_app')
sys.path.insert(0, WEB_APP_DIR)

from flask import Flask
from models import db, Analysis

# Create Flask app
app = Flask(__name__)

# Configure database
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'resume_analyzer.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"📁 Database will be created at: {DATABASE_PATH}")

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    # Drop all tables (for clean testing)
    print("🗑️  Dropping existing tables...")
    db.drop_all()
    
    # Create all tables
    print("📊 Creating database tables...")
    db.create_all()
    
    # Verify tables were created
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n✅ Database setup successful!")
    print(f"📋 Tables created: {tables}")
    
    # Get column information
    if 'analyses' in tables:
        columns = inspector.get_columns('analyses')
        print(f"\n📊 'analyses' table columns:")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
    
    # Test statistics method
    stats = Analysis.get_statistics()
    print(f"\n📈 Initial Statistics:")
    print(f"   Total analyses: {stats['total_analyses']}")
    print(f"   Quality check count: {stats['quality_check_count']}")
    print(f"   Full analysis count: {stats['full_analysis_count']}")
    
    print(f"\n🎉 Database is ready to use!")
    print(f"📍 Location: {DATABASE_PATH}")
