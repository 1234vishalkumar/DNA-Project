#!/usr/bin/env python3
"""
Final DNA Forensic Analysis System - Complete Implementation
"""

import os
import sys
from datetime import datetime

def check_and_install_deps():
    """Install missing dependencies"""
    try:
        import cv2
        print("[OK] OpenCV available")
    except ImportError:
        print("[WARN] OpenCV missing - gel analysis will be limited")
    
    try:
        from scipy import ndimage
        print("[OK] SciPy available")
    except ImportError:
        print("[WARN] SciPy missing - signal processing limited")
    
    try:
        import matplotlib
        print("[OK] Matplotlib available")
    except ImportError:
        print("[WARN] Matplotlib missing - visualization limited")

def run_system():
    """Run the complete system"""
    print("Enhanced DNA Forensic Analysis System")
    print("=" * 50)
    
    # Check dependencies
    check_and_install_deps()
    
    # Import and run Flask app
    try:
        from simple_app import app
        print("\nStarting web server...")
        print("Features Available:")
        print("   - Gel Electrophoresis Analysis")
        print("   - DNA Sequence Analysis (if models available)")
        print("   - Visualization Dashboard")
        print("\nAccess at: http://localhost:5000")
        print("Press Ctrl+C to stop")
        
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nSystem stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_system()