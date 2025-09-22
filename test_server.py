import requests
import time

print("🔍 Testing Spotify MusiVault Server...")

# Wait a moment for server to fully start
time.sleep(3)

try:
    # Test the /test endpoint
    response = requests.get("http://127.0.0.1:5000/test", timeout=5)
    
    if response.status_code == 200:
        print("✅ Server is responding!")
        print(f"📊 Response: {response.json()}")
        
        # Test the main page
        main_response = requests.get("http://127.0.0.1:5000/", timeout=5)
        if main_response.status_code == 200:
            print("✅ Main page is working!")
            print("🎯 Server is ready for Spotify data collection!")
        else:
            print(f"⚠️ Main page returned status: {main_response.status_code}")
            
    else:
        print(f"❌ Server returned status: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server on port 5000")
    print("💡 Make sure the Flask server is running")
    
except requests.exceptions.Timeout:
    print("❌ Server response timeout")
    
except Exception as e:
    print(f"❌ Error testing server: {e}")

print("\n🌐 If server is working, visit: http://127.0.0.1:5000")
print("🎵 Ready to test with real Spotify data!")
