@echo off
echo Starting Trading Dashboard...
echo.

set SSL_CERT_FILE=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=

cd /d C:\Trading
python -c "import ssl; ssl._create_default_https_context = ssl._create_unverified_context"
streamlit run trading_dashboard.py

pause
