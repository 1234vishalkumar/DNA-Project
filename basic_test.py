#!/usr/bin/env python3
"""
Basic test for DNA analysis functionality
"""

import os
import sys
import json
from datetime import datetime

def test_imports():
    """Test required imports"""
    print("Checking imports...")
    
    try:
        import numpy as np
        print("OK: NumPy imported successfully")
    except ImportError as e:
        print(f"ERROR: NumPy import failed: {e}")

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        print("OK: Scikit-learn imported successfully")
    except ImportError as e:
        print(f"ERROR: Scikit-learn import failed: {e}")

    try:
        from Bio import SeqIO
        print("OK: BioPython imported successfully")
    except ImportError as e:
        print(f"ERROR: BioPython import failed: {e}")

    try:
        import joblib
        print("OK: Joblib imported successfully")
    except ImportError as e:
        print(f"ERROR: Joblib import failed: {e}")

    try:
        from fpdf import FPDF
        print("OK: FPDF imported successfully")
    except ImportError as e:
        print(f"ERROR: FPDF import failed: {e}")

    try:
        import sqlite3
        print("OK: SQLite3 imported successfully")
    except ImportError as e:
        print(f"ERROR: SQLite3 import failed: {e}")

    try:
        from flask import Flask
        print("OK: Flask imported successfully")
    except ImportError as e:
        print(f"ERROR: Flask import failed: {e}")

def test_basic_functions():
    """Test basic DNA processing"""
    print("\nTesting basic DNA functions...")
    
    # Test sequence cleaning
    def clean_sequence(seq):
        return ''.join([s for s in seq.upper() if s in "ACGT"])
    
    test_seq = "ATCGATCGATCG123XYZ"
    cleaned = clean_sequence(test_seq)
    print(f"Sequence cleaning: {test_seq} -> {cleaned}")
    
    # Test k-mer generation
    def get_kmers(seq, k=3):
        return [seq[i:i+k] for i in range(len(seq)-k+1)]
    
    kmers = get_kmers(cleaned, 3)
    print(f"K-mer generation: {kmers[:5]}...")
    
    # Test database
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')  # In-memory database
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE test_analysis (
                id INTEGER PRIMARY KEY,
                sequence TEXT,
                timestamp TEXT
            )
        ''')
        cursor.execute("INSERT INTO test_analysis (sequence, timestamp) VALUES (?, ?)", 
                      (cleaned, datetime.now().isoformat()))
        conn.commit()
        
        # Test retrieval
        cursor.execute("SELECT * FROM test_analysis")
        result = cursor.fetchone()
        conn.close()
        
        print(f"Database test: Stored and retrieved sequence: {result[1]}")
        
    except Exception as e:
        print(f"Database test error: {e}")

def check_model_files():
    """Check if model files exist"""
    print("\nChecking model files...")
    
    model_files = [
        "model/best_model.pkl",
        "model/scaler.pkl", 
        "model/kmer_vocab.json"
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            print(f"OK: {file_path} exists")
        else:
            print(f"WARNING: {file_path} not found")

def main():
    """Run all tests"""
    print("DNA FORENSIC SYSTEM - BASIC TEST")
    print("=" * 40)
    
    test_imports()
    test_basic_functions()
    check_model_files()
    
    print("\n" + "=" * 40)
    print("Basic tests completed!")
    print("\nTo run the full system:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run: cd app && python app.py")

if __name__ == "__main__":
    main()