#!/usr/bin/env python3
"""
ETL System Verification Script
This script verifies that all components of the ETL system are working correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("✓ Testing imports...")
    try:
        from app import create_app, db
        from app.models import User, Job, DataSource, ETLRun, ETLLog
        from app.etl import extract_data, transform_data, load_data
        from app.utils import allowed_file, generate_table_name, validate_url
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_app_creation():
    """Test Flask app creation"""
    print("✓ Testing Flask app creation...")
    try:
        from app import create_app
        app = create_app()
        assert app is not None
        print("  ✓ Flask app created successfully")
        return True, app
    except Exception as e:
        print(f"  ✗ App creation failed: {e}")
        return False, None


def test_database_models(app):
    """Test database model creation"""
    print("✓ Testing database models...")
    try:
        from app import db
        from app.models import User, Job, DataSource, ETLRun, ETLLog
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Test user creation
            test_user = User(username='testuser', email='test@test.com')
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()
            
            # Verify user
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.check_password('testpass123')
            
            print("  ✓ Database models working correctly")
            return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        return False


def test_utility_functions():
    """Test utility functions"""
    print("✓ Testing utility functions...")
    try:
        from app.utils import allowed_file, generate_table_name, validate_url
        
        # Test file validation
        assert allowed_file('test.csv') == True
        assert allowed_file('test.txt') == True
        assert allowed_file('test.exe') == False
        
        # Test table name generation
        table_name = generate_table_name('My Test Job', 123)
        assert 'my_test_job' in table_name
        assert '123' in table_name
        
        # Test URL validation
        assert validate_url('https://api.example.com/data') == True
        assert validate_url('http://localhost:5000') == True
        assert validate_url('not-a-url') == False
        
        print("  ✓ All utility functions working correctly")
        return True
    except Exception as e:
        print(f"  ✗ Utility test failed: {e}")
        return False


def test_etl_modules():
    """Test ETL module imports and basic structure"""
    print("✓ Testing ETL modules...")
    try:
        from app.etl import extract_data, transform_data, load_data
        from app.etl.extract import extract_from_csv, extract_from_api
        from app.etl.transform import clean_column_name
        from app.etl.load import load_data
        
        # Test column name cleaning
        assert clean_column_name('First Name') == 'first_name'
        assert clean_column_name('Email-Address') == 'email_address'
        assert clean_column_name('AGE (years)') == 'age_years'
        
        print("  ✓ ETL modules loaded successfully")
        return True
    except Exception as e:
        print(f"  ✗ ETL module test failed: {e}")
        return False


def test_routes():
    """Test that all routes are registered"""
    print("✓ Testing route registration...")
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Get all routes
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            
            # Check critical routes exist
            required_routes = [
                '/auth/login',
                '/auth/register',
                '/auth/logout',
                '/jobs/',
                '/jobs/create',
                '/etl/run/<int:job_id>',
                '/etl/data/<int:job_id>',
                '/etl/logs/<int:run_id>'
            ]
            
            for route in required_routes:
                # Check if route pattern exists
                found = any(route.replace('<int:job_id>', '<job_id>').replace('<int:run_id>', '<run_id>') in r for r in routes)
                if not found:
                    print(f"  ✗ Route not found: {route}")
                    return False
            
            print(f"  ✓ All {len(required_routes)} required routes registered")
            return True
    except Exception as e:
        print(f"  ✗ Route test failed: {e}")
        return False


def test_templates():
    """Test that all templates exist"""
    print("✓ Testing template files...")
    try:
        template_dir = 'app/templates'
        required_templates = [
            'base.html',
            'index.html',
            'dashboard.html',
            'auth/login.html',
            'auth/register.html',
            'jobs/create.html',
            'jobs/list.html',
            'jobs/view.html',
            'etl/view_data.html',
            'etl/view_logs.html'
        ]
        
        missing = []
        for template in required_templates:
            path = os.path.join(template_dir, template)
            if not os.path.exists(path):
                missing.append(template)
        
        if missing:
            print(f"  ✗ Missing templates: {missing}")
            return False
        
        print(f"  ✓ All {len(required_templates)} templates exist")
        return True
    except Exception as e:
        print(f"  ✗ Template test failed: {e}")
        return False


def test_configuration():
    """Test configuration"""
    print("✓ Testing configuration...")
    try:
        from config import Config
        
        assert hasattr(Config, 'SECRET_KEY')
        assert hasattr(Config, 'SQLALCHEMY_DATABASE_URI')
        assert hasattr(Config, 'UPLOAD_FOLDER')
        assert Config.UPLOAD_FOLDER == 'uploads'
        
        print("  ✓ Configuration loaded correctly")
        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ETL MANAGEMENT SYSTEM - VERIFICATION SCRIPT")
    print("="*60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_configuration()))
    
    success, app = test_app_creation()
    results.append(("App Creation", success))
    
    if success and app:
        results.append(("Database Models", test_database_models(app)))
    else:
        results.append(("Database Models", False))
    
    results.append(("Utility Functions", test_utility_functions()))
    results.append(("ETL Modules", test_etl_modules()))
    results.append(("Route Registration", test_routes()))
    results.append(("Templates", test_templates()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The ETL system is fully functional.")
        print("\nYou can now:")
        print("  1. Run: python3 run.py")
        print("  2. Visit: http://localhost:5000")
        print("  3. Register and start creating ETL jobs!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
