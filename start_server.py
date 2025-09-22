#!/usr/bin/env python3
"""
Simple test to verify environment and start Flask app
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

print("🔍 Environment Test")
print("=" * 40)

# Test imports
try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask: {e}")
    sys.exit(1)

try:
    import spotipy
    print(f"✅ Spotipy: {spotipy.__version__}")
except ImportError as e:
    print(f"❌ Spotipy: {e}")
    sys.exit(1)

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ SQLAlchemy: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv: imported")
    load_dotenv()
except ImportError as e:
    print(f"❌ python-dotenv: {e}")
    sys.exit(1)

try:
    from authlib.integrations.flask_client import OAuth
    print("✅ Authlib: imported")
except ImportError as e:
    print(f"❌ Authlib: {e}")
    sys.exit(1)

print("\n🔧 Testing App Imports")
print("=" * 40)

# Change to app directory for imports
os.chdir(os.path.join(os.path.dirname(__file__), 'app'))

try:
    import database
    print("✅ database module imported")
except ImportError as e:
    print(f"❌ database module: {e}")

try:
    import models
    print("✅ models module imported")
except ImportError as e:
    print(f"❌ models module: {e}")

try:
    import data_access
    print("✅ data_access module imported")
except ImportError as e:
    print(f"❌ data_access module: {e}")

try:
    import data_collector
    print("✅ data_collector module imported")
except ImportError as e:
    print(f"❌ data_collector module: {e}")

try:
    import spotify_api_services
    print("✅ spotify_api_services module imported")
except ImportError as e:
    print(f"❌ spotify_api_services module: {e}")

try:
    import spotify_utils
    print("✅ spotify_utils module imported")
except ImportError as e:
    print(f"❌ spotify_utils module: {e}")

print("\n🚀 Starting Flask App")
print("=" * 40)

try:
    # Import and run the Flask app
    from app import app
    print("✅ Flask app imported successfully")
    print("🌐 Starting server on http://127.0.0.1:5000")
    print("📝 Press Ctrl+C to stop the server")
    app.run(debug=True, host='127.0.0.1', port=5000)
except Exception as e:
    print(f"❌ Error starting Flask app: {e}")
    import traceback
    traceback.print_exc()
