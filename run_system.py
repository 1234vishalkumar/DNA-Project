#!/usr/bin/env python3
"""
Enhanced DNA Forensic Analysis System - Main Runner
This script sets up and runs the complete DNA forensic analysis system
"""

import os
import sys
import subprocess
import webbrowser
from datetime import datetime

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'biopython', 'scikit-learn', 'numpy', 'pandas',
        'matplotlib', 'seaborn', 'joblib', 'xgboost', 'fpdf2',
        'plotly', 'pyttsx3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"   ✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {package}")
    
    print("✅ Dependency check complete!")

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        'uploads',
        'reports',
        'audio',
        'app/static',
        'app/templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ Directory setup complete!")

def initialize_database():
    """Initialize the SQLite database"""
    print("\n💾 Initializing database...")
    
    try:
        from utils import init_database
        init_database()
        print("   ✅ Database initialized successfully!")
    except Exception as e:
        print(f"   ⚠️ Database initialization warning: {e}")

def run_tests():
    """Run system tests"""
    print("\n🧪 Running system tests...")
    
    try:
        from test_enhanced_features import run_comprehensive_test
        run_comprehensive_test()
    except Exception as e:
        print(f"   ⚠️ Test warning: {e}")

def start_flask_app():
    """Start the Flask web application"""
    print("\n🚀 Starting DNA Forensic Analysis System...")
    print("=" * 60)
    
    # Change to app directory
    os.chdir('app')
    
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    print("🌐 Web application will be available at: http://localhost:5000")
    print("📊 Dashboard available at: http://localhost:5000/dashboard")
    print("📋 Analysis history at: http://localhost:5000/history")
    print("\n🔧 Available API endpoints:")
    print("   • POST /api/predict - DNA prediction API")
    print("   • POST /api/compare - DNA comparison API")
    print("   • GET /api/history - Analysis history API")
    
    print("\n" + "=" * 60)
    print("🧬 ENHANCED DNA FORENSIC ANALYSIS SYSTEM")
    print("   Features: AI Analysis | Voice Synthesis | Multi-Modal")
    print("   Database: SQLite | Visualization: Plotly | Reports: PDF")
    print("=" * 60)
    
    # Open browser automatically
    try:
        webbrowser.open('http://localhost:5000')
    except:
        pass
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 DNA Forensic Analysis System stopped.")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")

def main():
    """Main function to set up and run the system"""
    print("🧬 ENHANCED DNA FORENSIC ANALYSIS SYSTEM")
    print("=" * 50)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("👩‍💻 Developed by: Venika")
    print("🔬 Features: 10+ Advanced DNA Analysis Tools")
    print("=" * 50)
    
    try:
        # Setup steps
        check_dependencies()
        setup_directories()
        initialize_database()
        
        # Optional: Run tests
        run_tests_choice = input("\n🧪 Run system tests? (y/N): ").lower().strip()
        if run_tests_choice == 'y':
            run_tests()
        
        # Start the application
        print("\n🚀 Ready to start the web application!")
        start_choice = input("Press Enter to start or 'q' to quit: ").lower().strip()
        
        if start_choice != 'q':
            start_flask_app()
        else:
            print("👋 Goodbye!")
    
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()