# launcher.py
import os
import sys
import time
import threading
import webbrowser
from waitress import serve
from app import create_app, db

class AttendifyLauncher:
    def __init__(self):
        self.app = None
        self.server_ready = False
        self.host = '127.0.0.1'
        self.port = 5000
        
    def setup_app(self):
        """Initialize the Flask app"""
        try:
            # Set production config for packaged app
            os.environ['FLASK_CONFIG'] = 'production'
            
            # Create app instance
            self.app = create_app(config_name='production')
            
            with self.app.app_context():
                # Create database and tables if they don't exist
                db.create_all()
                print(f"✓ Database initialized at {self.app.config['SQLALCHEMY_DATABASE_URI']}")
                
            return True
        except Exception as e:
            print(f"✗ Error setting up app: {e}")
            return False
    
    def start_server(self):
        """Start the Flask server in a separate thread"""
        try:
            print(f"🚀 Starting Attendify Server...")
            print(f"   Server: http://{self.host}:{self.port}")
            
            # Start server
            serve(self.app, host=self.host, port=self.port, threads=8)
            
        except Exception as e:
            print(f"✗ Server error: {e}")
    
    def wait_for_server(self):
        """Wait for server to be ready"""
        import socket
        max_attempts = 30
        attempts = 0
        
        while attempts < max_attempts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.host, self.port))
                sock.close()
                
                if result == 0:
                    self.server_ready = True
                    print("✓ Server is ready!")
                    return True
                    
            except Exception:
                pass
            
            attempts += 1
            time.sleep(1)
            print(f"⏳ Waiting for server... ({attempts}/{max_attempts})")
        
        return False
    
    def open_browser(self):
        """Open the default web browser"""
        if self.server_ready:
            url = f"http://{self.host}:{self.port}"
            print(f"🌐 Opening browser: {url}")
            time.sleep(2)  # Give server a moment
            webbrowser.open(url)
        else:
            print("✗ Server not ready, cannot open browser")
    
    def run(self):
        """Main execution method"""
        print("=" * 50)
        print("🏢 ATTENDIFY LAUNCHER")
        print("=" * 50)
        
        # Setup app
        if not self.setup_app():
            print("✗ Failed to setup application")
            input("Press Enter to exit...")
            return
        
        # Start server in background thread
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()
        
        # Wait for server to be ready
        if self.wait_for_server():
            # Open browser
            browser_thread = threading.Thread(target=self.open_browser, daemon=True)
            browser_thread.start()
            
            print("\n" + "=" * 50)
            print("✅ ATTENDIFY IS RUNNING!")
            print(f"   🌐 Access: http://{self.host}:{self.port}")
            print("   📝 Close this window to stop the system")
            print("=" * 50)
            
            try:
                # Keep main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
        else:
            print("✗ Failed to start server")
            input("Press Enter to exit...")

if __name__ == '__main__':
    launcher = AttendifyLauncher()
    launcher.run()