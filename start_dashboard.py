"""
Wrapper script to launch Streamlit dashboard with SSL fix
"""
import os
import sys
import ssl

# Disable SSL verification for Windows certificate store issues
ssl._create_default_https_context = ssl._create_unverified_context

# Clear SSL environment variables
os.environ['SSL_CERT_FILE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

# Now import streamlit
from streamlit.web import cli as stcli

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "trading_dashboard.py"]
    sys.exit(stcli.main())
