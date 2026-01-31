"""
BillPro - Enterprise Billing & Accounting System
Entry point for the Flask application
"""
import os
import sys
import webbrowser
import threading
import time

# Handle PyInstaller frozen mode
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
    os.chdir(BASE_DIR)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the project root to Python path
sys.path.insert(0, BASE_DIR)

from app import create_app

app = create_app()


def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    print("=" * 50)
    print("  BillPro - Billing & Accounting Software")
    print("=" * 50)
    print()
    print("  Starting server at http://localhost:5000")
    print()
    print("  The application will open in your browser...")
    print("  Press Ctrl+C to stop the server")
    print()
    print("=" * 50)
    
    # Auto-open browser in exe mode
    if getattr(sys, 'frozen', False):
        threading.Thread(target=open_browser, daemon=True).start()
    
    # Run without debug mode in production/exe
    debug_mode = not getattr(sys, 'frozen', False)
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)
