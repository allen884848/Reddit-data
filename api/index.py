"""
Vercel API Entry Point for Reddit Data Collector
===============================================

This file serves as the entry point for Vercel deployment.
It imports and exposes the Flask application for serverless deployment.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask application
from app import app

# Vercel expects the application to be named 'app'
# This is the WSGI application that Vercel will use
if __name__ == "__main__":
    app.run(debug=False) 