import sys
import os

print("Testing basic imports...")

try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except Exception as e:
    print(f"❌ Flask error: {e}")
    sys.exit(1)

try:
    import spotipy  # noqa: F401
    print("✅ Spotipy import ok")
except Exception as e:
    print(f"❌ Spotipy error: {e}")
    sys.exit(1)

print("\nEnvironment looks good! 🎉")
print("Let's try to start a minimal Flask app...")

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "🎵 Spotify MusiVault is working! 🎵"

if __name__ == '__main__':
    print("Starting minimal Flask server on http://127.0.0.1:5000")
    print("Visit the URL to test if Flask is working")
    app.run(debug=True, port=5000)
