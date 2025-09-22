import sys
import os

# Add the app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.insert(0, app_dir)

print(f"Current directory: {current_dir}")
print(f"App directory: {app_dir}")
print(f"App directory exists: {os.path.exists(app_dir)}")

# Test basic imports
print("\n🔍 Testing imports...")

try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except Exception as e:
    print(f"❌ Flask: {e}")

try:
    import spotipy
    print(f"✅ Spotipy: {spotipy.__version__}")
except Exception as e:
    print(f"❌ Spotipy: {e}")

# Test app module imports
print("\n🔍 Testing app modules...")

try:
    os.chdir(app_dir)  # Change to app directory
    import database
    print("✅ database imported")
except Exception as e:
    print(f"❌ database: {e}")

try:
    import models
    print("✅ models imported")  
except Exception as e:
    print(f"❌ models: {e}")

try:
    import data_access
    print("✅ data_access imported")
except Exception as e:
    print(f"❌ data_access: {e}")

try:
    import data_collector
    print("✅ data_collector imported")
except Exception as e:
    print(f"❌ data_collector: {e}")

# Test simple Flask app
print("\n🚀 Testing minimal Flask setup...")

try:
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "🎵 Hello from Spotify MusiVault! 🎵"
    
    print("✅ Flask app created successfully")
    print("🌐 Starting server on http://127.0.0.1:5000")
    print("📝 Open browser to http://127.0.0.1:5000 to test")
    print("📝 Press Ctrl+C to stop")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
    
except Exception as e:
    print(f"❌ Flask setup error: {e}")
    import traceback
    traceback.print_exc()
