"""
BillPro - Enterprise Billing & Accounting System
Entry point for the Flask application
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("BillPro - Billing & Accounting Software")
    print("=" * 50)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    app.run(host='127.0.0.1', port=5000, debug=True)
