"""
Trading Dashboard Launcher with SSL Fix
Run this instead of streamlit directly
"""
import os
import sys

# Must set these BEFORE any imports
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['SSL_CERT_FILE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

# Patch SSL before any other imports
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Now safe to import streamlit
print("Starting Trading Dashboard...")
print("Dashboard will open in your browser at http://localhost:8501")
print()

import subprocess
result = subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    "trading_dashboard.py",
    "--server.headless", "true"
], env=os.environ)

sys.exit(result.returncode)
