"""
WSGI Configuration for PythonAnywhere
Copy this content to your WSGI configuration file in PythonAnywhere Web tab
"""

import sys
import os

# Add Python packages path
sys.path.insert(0, '/home/sapandesai/.local/lib/python3.13/site-packages')
sys.path.insert(0, '/home/sapandesai/Resume_Analyzer')

# Set working directory
os.chdir('/home/sapandesai/Resume_Analyzer')

# Import Flask application
from app import app as application

# Configure static files
application.static_folder = '/home/sapandesai/Resume_Analyzer/static'
application.template_folder = '/home/sapandesai/Resume_Analyzer/templates'
