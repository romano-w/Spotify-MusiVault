from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>🎵 Spotify MusiVault - Server Test</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #1DB954, #191414); 
                color: white; 
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 40px; 
                border-radius: 20px; 
            }
            h1 { font-size: 2.5em; margin-bottom: 30px; }
            .status { background: #1DB954; padding: 20px; border-radius: 10px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Spotify MusiVault</h1>
            <div class="status">
                <h2>✅ Server is Running!</h2>
                <p>Flask server is working correctly</p>
            </div>
            <p>This confirms that:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>✅ Poetry environment is working</li>
                <li>✅ Flask is installed and running</li>
                <li>✅ Server can accept connections</li>
                <li>✅ Port 5000 is available</li>
            </ul>
            <p><strong>Next step:</strong> Fix the import issues in the main app</p>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return {
        'status': 'success',
        'message': 'Flask server is working',
        'server': 'Spotify MusiVault Test Server'
    }

if __name__ == '__main__':
    print("🎵 Starting Spotify MusiVault Test Server...")
    print("🌐 Visit: http://127.0.0.1:5000")
    print("📝 Press Ctrl+C to stop")
    app.run(debug=True, host='127.0.0.1', port=5000)
