# PythonAnywhere Deployment Fix Guide

## Problem
PythonAnywhere is showing README.md instead of running the Flask application.

## Root Cause
Static file mapping is configured incorrectly, causing PythonAnywhere to serve files instead of running the Flask app.

---

## Solution Steps

### Step 1: Remove Incorrect Static File Mappings

1. Go to PythonAnywhere Dashboard
2. Click **"Web"** tab
3. Scroll to **"Static files"** section
4. **DELETE** any mapping that has:
   - URL: `/` or empty
   - Directory pointing to project root

### Step 2: Configure Correct Static Files

Keep ONLY this mapping:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/sapandesai/Resume_Analyzer/static` |

### Step 3: Verify WSGI Configuration

1. In Web tab, under **"Code"** section
2. Click on **WSGI configuration file** link
3. Replace ALL content with:

```python
import sys
import os

# Add Python packages path
sys.path.insert(0, '/home/sapandesai/.local/lib/python3.13/site-packages')
sys.path.insert(0, '/home/sapandesai/Resume_Analyzer')

# Import Flask application
from app import app as application
```

4. Click **Save**

### Step 4: Verify Paths

In Web tab, under **"Code"** section:

- **Source code**: `/home/sapandesai/Resume_Analyzer`
- **Working directory**: `/home/sapandesai/Resume_Analyzer`
- **WSGI configuration file**: (should be auto-filled)

### Step 5: Reload Application

1. Scroll to top of Web tab
2. Click big green **"Reload sapandesai.pythonanywhere.com"** button
3. Wait 10 seconds
4. Visit: http://sapandesai.pythonanywhere.com

---

## Verification Checklist

✅ Static files section has ONLY `/static/` mapping
✅ WSGI file imports `from app import app as application`
✅ Working directory is set correctly
✅ Reload button clicked
✅ Wait 10 seconds before testing

---

## If Still Not Working

### Check Error Log

1. In Web tab, scroll to **"Log files"**
2. Click **"Error log"**
3. Look at the last 10-20 lines
4. Share the error message

### Common Issues

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'PyPDF2'` | Run: `pip3 install --user PyPDF2` |
| `ModuleNotFoundError: No module named 'app'` | Check WSGI file path is correct |
| Still showing README | Clear browser cache (Ctrl+Shift+R) |

---

## Emergency Reset

If nothing works:

1. Delete the web app in PythonAnywhere
2. Create new web app:
   - Choose Flask
   - Choose Python 3.10
   - Path: `/home/sapandesai/Resume_Analyzer/app.py`
3. Follow Steps 1-5 above

---

## Contact Support

If issue persists after following all steps:
1. Take screenshot of Web tab configuration
2. Copy last 20 lines from error log
3. Share both for troubleshooting
