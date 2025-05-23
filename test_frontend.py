#!/usr/bin/env python3
"""
Frontend Test Script
====================

This script tests the frontend components of the Reddit data collection website
to ensure templates, static files, and basic functionality work correctly.

Author: Reddit Data Collector Team
Version: 1.0
Last Updated: 2024
"""

import sys
import os
import requests
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_frontend_files():
    """Test that all frontend files exist and are properly structured."""
    print("🔍 Testing Frontend File Structure...")
    
    required_files = [
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({file_size:,} bytes)")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    
    print("  ✅ All frontend files present")
    return True

def test_template_syntax():
    """Test that the HTML template has valid syntax."""
    print("\n🔍 Testing Template Syntax...")
    
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic syntax checks
        if '<!DOCTYPE html>' not in content:
            print("  ❌ Missing DOCTYPE declaration")
            return False
        
        if '<html lang="en">' not in content:
            print("  ❌ Missing or incorrect HTML lang attribute")
            return False
        
        # Check for required sections
        required_sections = [
            'navbar',
            'hero-section',
            'search-form',
            'results-section',
            'status-section'
        ]
        
        missing_sections = []
        for section in required_sections:
            if f'id="{section}"' not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"  ❌ Missing sections: {missing_sections}")
            return False
        
        # Check for Bootstrap and custom CSS/JS
        if 'bootstrap@5.3.2' not in content:
            print("  ❌ Bootstrap 5 not found")
            return False
        
        if 'bootstrap-icons' not in content:
            print("  ❌ Bootstrap Icons not found")
            return False
        
        if "url_for('static', filename='css/style.css')" not in content:
            print("  ❌ Custom CSS not linked")
            return False
        
        if "url_for('static', filename='js/app.js')" not in content:
            print("  ❌ Custom JS not linked")
            return False
        
        print("  ✅ Template syntax is valid")
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading template: {e}")
        return False

def test_css_structure():
    """Test that the CSS file has proper structure."""
    print("\n🔍 Testing CSS Structure...")
    
    try:
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for CSS variables
        if ':root {' not in content:
            print("  ❌ CSS variables not found")
            return False
        
        # Check for key CSS classes
        required_classes = [
            '.hero-section',
            '.search-container',
            '.results-grid',
            '.result-item',
            '.status-bar'
        ]
        
        missing_classes = []
        for css_class in required_classes:
            if css_class not in content:
                missing_classes.append(css_class)
        
        if missing_classes:
            print(f"  ❌ Missing CSS classes: {missing_classes}")
            return False
        
        # Check for responsive design
        if '@media (max-width: 768px)' not in content:
            print("  ❌ Mobile responsive styles not found")
            return False
        
        print("  ✅ CSS structure is valid")
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading CSS: {e}")
        return False

def test_javascript_structure():
    """Test that the JavaScript file has proper structure."""
    print("\n🔍 Testing JavaScript Structure...")
    
    try:
        with open('static/js/app.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for main application components
        required_functions = [
            'performSearch',
            'collectPromotionalPosts',
            'displayResults',
            'loadSystemStatus',
            'showToast'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f'function {func}' not in content and f'{func} =' not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"  ❌ Missing JavaScript functions: {missing_functions}")
            return False
        
        # Check for API endpoints
        if 'const API = {' not in content:
            print("  ❌ API endpoints configuration not found")
            return False
        
        # Check for application state
        if 'const AppState = {' not in content:
            print("  ❌ Application state management not found")
            return False
        
        print("  ✅ JavaScript structure is valid")
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading JavaScript: {e}")
        return False

def test_flask_integration():
    """Test that Flask can render the template without errors."""
    print("\n🔍 Testing Flask Integration...")
    
    try:
        # Import Flask app
        from app import app, db_manager
        
        # Test template rendering
        with app.test_client() as client:
            with app.app_context():
                # Get database stats for template
                stats = db_manager.get_database_stats()
                
                # Test home page rendering
                response = client.get('/')
                
                if response.status_code != 200:
                    print(f"  ❌ Home page returned status {response.status_code}")
                    return False
                
                # Check response content
                content = response.get_data(as_text=True)
                
                if 'Reddit Data Collector' not in content:
                    print("  ❌ Page title not found in response")
                    return False
                
                if 'bootstrap@5.3.2' not in content:
                    print("  ❌ Bootstrap not loaded in response")
                    return False
                
                print("  ✅ Flask template rendering works")
                return True
                
    except Exception as e:
        print(f"  ❌ Flask integration error: {e}")
        return False

def run_all_tests():
    """Run all frontend tests."""
    print(f"🚀 Reddit Data Collector - Frontend Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Frontend Files", test_frontend_files),
        ("Template Syntax", test_template_syntax),
        ("CSS Structure", test_css_structure),
        ("JavaScript Structure", test_javascript_structure),
        ("Flask Integration", test_flask_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Critical error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All frontend tests passed! The interface is ready to use.")
        print("\n📋 Next Steps:")
        print("1. Start the Flask application: python app.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Test the search functionality")
        return True
    else:
        print("⚠️  Some frontend tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Frontend tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical error during frontend testing: {e}")
        sys.exit(1) 