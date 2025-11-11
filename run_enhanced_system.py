#!/usr/bin/env python3
"""
Enhanced DNA Forensic Analysis System Launcher
Now includes Gel Electrophoresis Analysis
"""

import os
import sys
import subprocess
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'opencv-python', 'numpy', 'scipy', 'matplotlib', 
        'scikit-learn', 'biopython', 'plotly', 'fpdf2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def run_tests():
    """Run system tests"""
    print("🧪 Running Enhanced System Tests...")
    
    # Test gel analysis
    try:
        from test_gel_analysis import run_comprehensive_gel_test
        run_comprehensive_gel_test()
    except Exception as e:
        print(f"⚠️ Gel analysis test failed: {e}")
    
    # Test original DNA analysis
    try:
        from test_enhanced_features import run_comprehensive_test
        run_comprehensive_test()
    except Exception as e:
        print(f"⚠️ DNA analysis test failed: {e}")

def start_web_server():
    """Start the Flask web server"""
    print("🌐 Starting Enhanced DNA Forensic Analysis System...")
    print("📊 Features Available:")
    print("   🧬 DNA Sequence Analysis")
    print("   ⚖️ DNA Comparison & Mutation Detection")
    print("   🧪 Gel Electrophoresis Analysis")
    print("   📊 Batch Processing")
    print("   🤖 Multi-Modal Analysis")
    print("   📈 Analytics Dashboard")
    print("   🔊 Voice Synthesis")
    print("   📄 PDF Report Generation")
    
    # Change to app directory
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    os.chdir(app_dir)
    
    # Start Flask app
    try:
        from app import app
        print(f"\n🚀 Server starting at: http://localhost:5000")
        print("📱 Access the Gel Analysis tab for new features!")
        print("⏹️ Press Ctrl+C to stop the server")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main launcher function"""
    print("🧬 Enhanced DNA Forensic Analysis System")
    print("=" * 50)
    print("🆕 NEW: Gel Electrophoresis Analysis Features!")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("✅ All dependencies are installed")
    
    # Ask user what to do
    while True:
        print("\n🎯 What would you like to do?")
        print("1. 🧪 Run Tests")
        print("2. 🌐 Start Web Server")
        print("3. 📊 Test Gel Analysis Only")
        print("4. ❌ Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            run_tests()
        elif choice == '2':
            start_web_server()
            break
        elif choice == '3':
            try:
                from test_gel_analysis import run_comprehensive_gel_test
                run_comprehensive_gel_test()
            except Exception as e:
                print(f"❌ Gel test failed: {e}")
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()