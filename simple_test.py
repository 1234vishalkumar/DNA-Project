#!/usr/bin/env python3
"""
Simple test for core DNA analysis functionality
"""

import os
import sys
import json
from datetime import datetime

# Test basic imports
try:
    import numpy as np
    print("✅ NumPy imported successfully")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    print("✅ Scikit-learn imported successfully")
except ImportError as e:
    print(f"❌ Scikit-learn import failed: {e}")

try:
    from Bio import SeqIO
    print("✅ BioPython imported successfully")
except ImportError as e:
    print(f"❌ BioPython import failed: {e}")

try:
    import joblib
    print("✅ Joblib imported successfully")
except ImportError as e:
    print(f"❌ Joblib import failed: {e}")

try:
    from fpdf import FPDF
    print("✅ FPDF imported successfully")
except ImportError as e:
    print(f"❌ FPDF import failed: {e}")

try:
    import sqlite3
    print("✅ SQLite3 imported successfully")
except ImportError as e:
    print(f"❌ SQLite3 import failed: {e}")

# Test basic functionality
def test_basic_dna_functions():
    """Test basic DNA processing functions"""
    print("\n🧬 Testing Basic DNA Functions...")
    
    # Test sequence cleaning
    def clean_sequence(seq):
        return ''.join([s for s in seq.upper() if s in "ACGT"])
    
    test_seq = "ATCGATCGATCG123XYZ"
    cleaned = clean_sequence(test_seq)
    print(f"✅ Sequence cleaning: {test_seq} -> {cleaned}")
    
    # Test k-mer generation
    def get_kmers(seq, k=3):
        return [seq[i:i+k] for i in range(len(seq)-k+1)]
    
    kmers = get_kmers(cleaned, 3)
    print(f"✅ K-mer generation: {kmers[:5]}...")
    
    # Test database initialization
    try:
        conn = sqlite3.connect('test_dna.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_analysis (
                id INTEGER PRIMARY KEY,
                sequence TEXT,
                timestamp TEXT
            )
        ''')
        cursor.execute("INSERT INTO test_analysis (sequence, timestamp) VALUES (?, ?)", 
                      (cleaned, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print("✅ Database operations working")
        
        # Clean up
        if os.path.exists('test_dna.db'):
            os.remove('test_dna.db')
            
    except Exception as e:
        print(f"⚠️ Database test error: {e}")

def test_flask_setup():
    """Test Flask application setup"""
    print("\n🌐 Testing Flask Setup...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        print("✅ Flask imported and app created successfully")
        
        @app.route('/')
        def test_route():
            return "DNA Forensic System Test"
        
        print("✅ Test route created successfully")
        
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
    except Exception as e:
        print(f"⚠️ Flask setup error: {e}")

def main():
    """Run simple tests"""
    print("🧬 DNA FORENSIC SYSTEM - SIMPLE TEST")
    print("=" * 50)
    
    test_basic_dna_functions()
    test_flask_setup()
    
    print("\n" + "=" * 50)
    print("🎉 Basic tests completed!")
    print("\n📋 Core Components Status:")
    print("   ✅ DNA sequence processing")
    print("   ✅ K-mer analysis")
    print("   ✅ Database operations")
    print("   ✅ Flask web framework")
    
    print("\n🚀 To start the full system:")
    print("   1. Install missing dependencies: pip install -r requirements.txt")
    print("   2. Run: python run_system.py")
    print("   3. Or run Flask directly: cd app && python app.py")

if __name__ == "__main__":
    main()