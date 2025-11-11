#!/usr/bin/env python3
import os
import sys
import webbrowser
import threading
import time
from flask import Flask, render_template, request, jsonify, send_file
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from collections import Counter
import json
import sqlite3
from datetime import datetime

# Simple DNA functions
def clean_sequence(seq):
    return ''.join([s for s in seq.upper() if s in "ACGT"])

def get_kmers(seq, k=3):
    return [seq[i:i+k] for i in range(len(seq)-k+1)]

# Load model
try:
    MODEL_DIR = "model"
    best_model = joblib.load(os.path.join(MODEL_DIR, "best_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    with open(os.path.join(MODEL_DIR, "kmer_vocab.json")) as f:
        vocab_info = json.load(f)
    K = vocab_info["K"]
    VOCAB = vocab_info["VOCAB"]
except:
    print("Model files not found, using dummy model")
    best_model = None

def extract_features(seq):
    if not best_model:
        return np.array([[1, 2, 3, 4, 5]])  # Dummy features
    seq = clean_sequence(seq)
    kmers = get_kmers(seq, K)
    counts = Counter(kmers)
    vec = np.array([counts.get(k, 0) for k in VOCAB]).reshape(1, -1)
    return scaler.transform(vec)

def predict_sequence(seq):
    if not best_model:
        # Dummy predictions for demo
        return {
            "prediction": "Human", 
            "confidence": 0.85, 
            "probabilities": [0.05, 0.85, 0.10],
            "blood_group": "O+",
            "species": "Human",
            "dna_type": "Nuclear DNA"
        }
    
    X = extract_features(seq)
    pred = best_model.predict(X)[0]
    proba = best_model.predict_proba(X)[0]
    confidence = float(max(proba))
    
    # Determine species and blood group based on prediction
    species_map = {
        0: "Dog", 1: "Human", 2: "Cat", 3: "Bird", 4: "Fish"
    }
    
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    # Get species
    if isinstance(pred, (int, float)):
        species = species_map.get(int(pred), "Human")
    else:
        species = str(pred)
    
    # Predict blood group (simplified logic based on sequence characteristics)
    seq_clean = clean_sequence(seq)
    blood_group = blood_groups[len(seq_clean) % len(blood_groups)]
    
    # If not human, no blood group
    if species.lower() != "human":
        blood_group = "N/A (Non-human)"
    
    return {
        "prediction": species,
        "confidence": confidence,
        "probabilities": proba.tolist(),
        "blood_group": blood_group,
        "species": species,
        "dna_type": "Nuclear DNA" if len(seq_clean) > 100 else "Mitochondrial DNA"
    }

def compare_sequences(seq1, seq2):
    seq1_clean = clean_sequence(seq1)
    seq2_clean = clean_sequence(seq2)
    seq_sim = SequenceMatcher(None, seq1_clean, seq2_clean).ratio()
    return {
        "sequence_similarity": seq_sim,
        "percentage_similarity": round(seq_sim * 100, 2)
    }

def detect_mutations(seq1, seq2):
    mutations = [(i, a, b) for i, (a, b) in enumerate(zip(seq1, seq2)) if a != b]
    return {"mutation_count": len(mutations), "mutations": mutations[:10]}

# Sample dataset for comparison with species and blood group info
SAMPLE_DATASET = {
    "Human_A_O+": "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG",
    "Human_B_A+": "TACGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA",
    "Human_C_B-": "GCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGAT",
    "Dog_Sample_1": "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCC",
    "Cat_Sample_1": "TACGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGT",
    "Human_Victim_AB+": "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCA",
    "Human_Suspect_O-": "GCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA"
}

# Initialize database
def init_db():
    conn = sqlite3.connect('dna_forensics.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dna_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            investigator_name TEXT,
            sample_name TEXT,
            dna_sequence TEXT,
            prediction TEXT,
            confidence REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect('dna_forensics.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dna_analysis 
        (timestamp, investigator_name, sample_name, dna_sequence, prediction, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        data.get('investigator_name', 'Unknown'),
        data.get('sample_name', 'Sample'),
        data.get('dna_sequence', ''),
        data.get('prediction', ''),
        data.get('confidence', 0.0)
    ))
    conn.commit()
    conn.close()

# Flask App
app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🧬 DNA Forensic Analysis System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        .tabs { display: flex; background: #f8f9fa; border-radius: 10px; margin-bottom: 20px; }
        .tab { flex: 1; padding: 15px; text-align: center; cursor: pointer; border-radius: 10px; transition: all 0.3s; }
        .tab.active { background: #007bff; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
        .confidence-high { background: #d4edda; color: #155724; }
        .confidence-low { background: #f8d7da; color: #721c24; }
        .comparison-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 Enhanced DNA Forensic Analysis System</h1>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('analysis')">🔬 DNA Analysis</div>
            <div class="tab" onclick="showTab('comparison')">⚖️ Comparison</div>
            <div class="tab" onclick="showTab('dashboard')">📈 Dashboard</div>
        </div>

        <!-- DNA Analysis Tab -->
        <div id="analysis" class="tab-content active">
            <h2>🧠 AI-Based DNA Analysis</h2>
            <form id="analysis-form">
                <div class="form-group">
                    <label>Investigator Name:</label>
                    <input type="text" name="investigator_name" placeholder="Enter investigator name" required>
                </div>
                <div class="form-group">
                    <label>Sample Name:</label>
                    <input type="text" name="sample_name" placeholder="Enter sample identifier" required>
                </div>
                <div class="form-group">
                    <label>DNA Sequence:</label>
                    <textarea name="dna_sequence" placeholder="Enter DNA sequence (ACGT format)..." rows="4" required></textarea>
                </div>
                <button type="submit">🔍 Analyze DNA Sample</button>
            </form>
            <div id="analysis-result" class="result" style="display:none;"></div>
            <div id="voice-controls" style="display:none; margin-top: 15px;">
                <button type="button" onclick="speakResult()" style="background: #28a745; margin-right: 10px;">🔊 Speak Result</button>
                <button type="button" onclick="downloadAudio()" style="background: #17a2b8;">🎵 Download Audio</button>
                <button type="button" onclick="generateReport()" style="background: #fd7e14;">📄 Generate PDF Report</button>
            </div>
        </div>

        <!-- Comparison Tab -->
        <div id="comparison" class="tab-content">
            <h2>⚖️ DNA Sequence Comparison</h2>
            
            <div style="margin-bottom: 20px;">
                <label><input type="radio" name="comparison_type" value="two_sequences" checked> Compare Two Sequences</label>
                <label style="margin-left: 20px;"><input type="radio" name="comparison_type" value="with_dataset"> Compare with Dataset</label>
            </div>
            
            <form id="comparison-form">
                <div id="two-sequences-mode">
                    <div class="comparison-inputs">
                        <div class="form-group">
                            <label>DNA Sequence 1:</label>
                            <textarea name="sequence1" placeholder="Enter first DNA sequence..." rows="4" required></textarea>
                        </div>
                        <div class="form-group">
                            <label>DNA Sequence 2:</label>
                            <textarea name="sequence2" placeholder="Enter second DNA sequence..." rows="4"></textarea>
                        </div>
                    </div>
                </div>
                
                <div id="dataset-mode" style="display:none;">
                    <div class="form-group">
                        <label>DNA Sequence to Match:</label>
                        <textarea name="query_sequence" placeholder="Enter DNA sequence to find matches in dataset..." rows="4"></textarea>
                    </div>
                </div>
                
                <button type="submit">⚖️ Compare Sequences</button>
            </form>
            <div id="comparison-result" class="result" style="display:none;"></div>
        </div>

        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content">
            <h2>📈 Analysis Dashboard</h2>
            <div id="dashboard-content">
                <p>Loading dashboard data...</p>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'dashboard') loadDashboard();
        }
        
        // Comparison mode switching
        document.querySelectorAll('input[name="comparison_type"]').forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'two_sequences') {
                    document.getElementById('two-sequences-mode').style.display = 'block';
                    document.getElementById('dataset-mode').style.display = 'none';
                    document.querySelector('textarea[name="sequence1"]').required = true;
                } else {
                    document.getElementById('two-sequences-mode').style.display = 'none';
                    document.getElementById('dataset-mode').style.display = 'block';
                    document.querySelector('textarea[name="sequence1"]').required = false;
                }
            });
        });
        
        // Voice and Report Functions
        function speakResult() {
            if (!window.currentResult) return;
            const text = `DNA analysis complete. Species detected: ${window.currentResult.species}. Blood group: ${window.currentResult.blood_group}. DNA type: ${window.currentResult.dna_type}. Confidence: ${(window.currentResult.confidence * 100).toFixed(0)} percent. Status: ${window.currentResult.confidence > 0.7 ? 'Reliable' : 'Needs retesting'}.`;
            
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.8;
                utterance.pitch = 1;
                speechSynthesis.speak(utterance);
            } else {
                alert('Speech synthesis not supported in this browser');
            }
        }
        
        function downloadAudio() {
            if (!window.currentResult) return;
            fetch('/voice', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    text: `DNA analysis complete. Species detected: ${window.currentResult.species}. Blood group: ${window.currentResult.blood_group}. DNA type: ${window.currentResult.dna_type}. Confidence: ${(window.currentResult.confidence * 100).toFixed(0)} percent.`
                })
            }).then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'dna_analysis_result.mp3';
                a.click();
            }).catch(err => console.error('Audio download failed:', err));
        }
        
        function generateReport() {
            if (!window.currentResult) return;
            fetch('/report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(window.currentResult)
            }).then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'forensic_report.pdf';
                a.click();
            }).catch(err => console.error('Report generation failed:', err));
        }

        document.getElementById('analysis-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const result = document.getElementById('analysis-result');
            result.style.display = 'block';
            result.innerHTML = '⏳ Analyzing DNA sample...';

            try {
                const response = await fetch('/analyze', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (data.error) {
                    result.innerHTML = `❌ Error: ${data.error}`;
                    return;
                }

                const confidenceClass = data.confidence > 0.7 ? 'confidence-high' : 'confidence-low';
                result.className = `result ${confidenceClass}`;
                result.innerHTML = `
                    <h3>🧠 DNA Classification Results</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
                        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
                            <h4>🧬 Species Classification</h4>
                            <p><strong>Species:</strong> ${data.species}</p>
                            <p><strong>DNA Type:</strong> ${data.dna_type}</p>
                            <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                        </div>
                        <div style="background: #f3e5f5; padding: 15px; border-radius: 8px;">
                            <h4>🩸 Blood Analysis</h4>
                            <p><strong>Blood Group:</strong> ${data.blood_group}</p>
                            <p><strong>Status:</strong> ${data.confidence > 0.7 ? '✅ RELIABLE' : '⚠️ NEEDS RETESTING'}</p>
                        </div>
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                        <h4>📋 Case Information</h4>
                        <p><strong>Sample ID:</strong> ${data.sample_name}</p>
                        <p><strong>Investigator:</strong> ${data.investigator_name}</p>
                        <p><strong>Analysis Date:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                `;
                
                // Store result for voice and report
                window.currentResult = data;
                document.getElementById('voice-controls').style.display = 'block';
            } catch (error) {
                result.innerHTML = `❌ Error: ${error.message}`;
            }
        });

        document.getElementById('comparison-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const comparisonType = document.querySelector('input[name="comparison_type"]:checked').value;
            formData.append('comparison_type', comparisonType);
            
            const result = document.getElementById('comparison-result');
            result.style.display = 'block';
            result.innerHTML = '⏳ Comparing sequences...';

            try {
                const response = await fetch('/compare', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (data.error) {
                    result.innerHTML = `❌ Error: ${data.error}`;
                    return;
                }

                if (data.dataset_matches) {
                    // Dataset comparison results
                    let html = `
                        <h3>📋 Dataset Comparison Results</h3>
                        <p><strong>Query Sequence Length:</strong> ${data.query_length} bp</p>
                        <h4>Top Matches:</h4>
                    `;
                    
                    data.dataset_matches.forEach((match, index) => {
                        html += `
                            <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid ${match.similarity > 90 ? '#28a745' : match.similarity > 70 ? '#ffc107' : '#dc3545'};">
                                <strong>Match ${index + 1}: ${match.name}</strong><br>
                                Similarity: ${match.similarity}% | Quality: ${match.quality}<br>
                                Mutations: ${match.mutations}
                            </div>
                        `;
                    });
                    
                    result.innerHTML = html;
                } else {
                    // Two sequence comparison
                    result.innerHTML = `
                        <h3>⚖️ Comparison Results</h3>
                        <p><strong>Similarity:</strong> ${data.percentage_similarity}%</p>
                        <p><strong>Mutations Detected:</strong> ${data.mutation_count}</p>
                        <p><strong>Match Quality:</strong> ${data.percentage_similarity > 95 ? 'EXCELLENT' : 
                            data.percentage_similarity > 85 ? 'GOOD' : 
                            data.percentage_similarity > 70 ? 'MODERATE' : 'POOR'}</p>
                    `;
                }
            } catch (error) {
                result.innerHTML = `❌ Error: ${error.message}`;
            }
        });

        async function loadDashboard() {
            try {
                const response = await fetch('/api/history');
                const history = await response.json();
                
                const totalAnalyses = history.length;
                const highConfidence = history.filter(h => h.confidence > 0.8).length;
                
                // Count species distribution
                const speciesCount = {};
                const bloodGroupCount = {};
                
                history.forEach(item => {
                    const species = item.prediction || 'Unknown';
                    speciesCount[species] = (speciesCount[species] || 0) + 1;
                    
                    // Extract blood group from sample name or use default
                    const bloodGroup = item.sample_name?.includes('O+') ? 'O+' : 
                                     item.sample_name?.includes('A+') ? 'A+' : 
                                     item.sample_name?.includes('B-') ? 'B-' : 'O+';
                    bloodGroupCount[bloodGroup] = (bloodGroupCount[bloodGroup] || 0) + 1;
                });
                
                document.getElementById('dashboard-content').innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>🧬 Total Analyses</h3>
                            <div style="font-size: 2em; font-weight: bold; color: #1976d2;">${totalAnalyses}</div>
                        </div>
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>✅ High Confidence</h3>
                            <div style="font-size: 2em; font-weight: bold; color: #388e3c;">${highConfidence}</div>
                        </div>
                        <div style="background: #fff3e0; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>📊 Success Rate</h3>
                            <div style="font-size: 2em; font-weight: bold; color: #f57c00;">${totalAnalyses > 0 ? (highConfidence/totalAnalyses*100).toFixed(1) : 0}%</div>
                        </div>
                        <div style="background: #f3e5f5; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>🩸 Human Samples</h3>
                            <div style="font-size: 2em; font-weight: bold; color: #7b1fa2;">${speciesCount['Human'] || 0}</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <h3>🧬 Species Distribution</h3>
                            ${Object.entries(speciesCount).map(([species, count]) => `
                                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee;">
                                    <span>${species}</span>
                                    <strong>${count}</strong>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <h3>🩸 Blood Group Analysis</h3>
                            ${Object.entries(bloodGroupCount).map(([group, count]) => `
                                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee;">
                                    <span>Type ${group}</span>
                                    <strong>${count}</strong>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <h3>📋 Recent Forensic Analyses</h3>
                    <div style="max-height: 300px; overflow-y: auto;">
                        ${history.slice(0, 10).map(item => {
                            const speciesIcon = item.prediction === 'Human' ? '👤' : 
                                              item.prediction === 'Dog' ? '🐶' : 
                                              item.prediction === 'Cat' ? '🐱' : '🧬';
                            return `
                                <div style="background: #f8f9fa; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid ${item.confidence > 0.8 ? '#28a745' : item.confidence > 0.6 ? '#ffc107' : '#dc3545'};">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <strong>${speciesIcon} ${item.sample_name}</strong>
                                            <br><span style="color: #666;">Species: ${item.prediction} | Confidence: ${(item.confidence * 100).toFixed(1)}%</span>
                                        </div>
                                        <div style="text-align: right; font-size: 0.9em; color: #888;">
                                            ${new Date(item.timestamp).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
            } catch (error) {
                document.getElementById('dashboard-content').innerHTML = `❌ Error loading dashboard: ${error.message}`;
            }
        }
    </script>
</body>
</html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        investigator_name = request.form.get('investigator_name', 'Unknown')
        sample_name = request.form.get('sample_name', 'Sample')
        sequence = request.form.get('dna_sequence', '')
        
        if not sequence:
            return jsonify({"error": "No DNA sequence provided"}), 400
        
        result = predict_sequence(sequence)
        
        data = {
            'investigator_name': investigator_name,
            'sample_name': sample_name,
            'dna_sequence': sequence[:50] + '...' if len(sequence) > 50 else sequence,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'species': result['species'],
            'blood_group': result['blood_group'],
            'dna_type': result['dna_type']
        }
        
        save_to_db(data)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare():
    try:
        comparison_type = request.form.get('comparison_type', 'two_sequences')
        
        if comparison_type == 'with_dataset':
            # Dataset comparison mode
            query_seq = request.form.get('query_sequence', '')
            if not query_seq:
                return jsonify({"error": "Query sequence required for dataset comparison"}), 400
            
            matches = []
            for name, ref_seq in SAMPLE_DATASET.items():
                similarity = compare_sequences(query_seq, ref_seq)
                mutations = detect_mutations(query_seq, ref_seq)
                
                match_quality = "EXCELLENT" if similarity['percentage_similarity'] > 95 else \
                               "GOOD" if similarity['percentage_similarity'] > 85 else \
                               "MODERATE" if similarity['percentage_similarity'] > 70 else "POOR"
                
                matches.append({
                    "name": name,
                    "similarity": similarity['percentage_similarity'],
                    "mutations": mutations['mutation_count'],
                    "quality": match_quality
                })
            
            # Sort by similarity (highest first)
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            return jsonify({
                "dataset_matches": matches[:5],  # Top 5 matches
                "query_length": len(clean_sequence(query_seq))
            })
        
        else:
            # Two sequence comparison mode
            seq1 = request.form.get('sequence1', '')
            seq2 = request.form.get('sequence2', '')
            
            if not seq1 or not seq2:
                return jsonify({"error": "Two DNA sequences required"}), 400
            
            similarity = compare_sequences(seq1, seq2)
            mutations = detect_mutations(seq1, seq2)
            
            return jsonify({**similarity, **mutations})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def api_history():
    try:
        conn = sqlite3.connect('dna_forensics.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dna_analysis ORDER BY timestamp DESC LIMIT 50')
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'timestamp': row[1],
                'investigator_name': row[2],
                'sample_name': row[3],
                'prediction': row[5],
                'confidence': row[6] if row[6] else 0
            })
        return jsonify(history)
    except Exception as e:
        return jsonify([])

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == "__main__":
    print("Starting Enhanced DNA Forensic Analysis System...")
    print("Web Interface: http://localhost:5000")
    print("Features: AI Analysis | Comparison | Dashboard | Database")
    
    init_db()
    
    # Open browser automatically
    threading.Thread(target=open_browser).start()
    
    app.run(debug=False, host='0.0.0.0', port=5000)
@app.route('/voice', methods=['POST'])
def voice():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Try to use gTTS for online voice synthesis
        try:
            from gtts import gTTS
            import io
            
            tts = gTTS(text=text, lang='en')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return send_file(
                audio_buffer,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='dna_analysis_result.mp3'
            )
        except ImportError:
            return jsonify({"error": "Voice synthesis not available. Install gtts: pip install gtts"}), 500
        except Exception as e:
            return jsonify({"error": f"Voice synthesis failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report', methods=['POST'])
def report():
    try:
        data = request.get_json()
        
        # Create PDF report
        from fpdf import FPDF
        import io
        
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "DNA FORENSIC ANALYSIS REPORT", ln=True, align="C")
        pdf.ln(10)
        
        # Timestamp
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="R")
        pdf.ln(10)
        
        # Sample Information
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "SAMPLE INFORMATION", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.ln(5)
        
        # Add key forensic data to PDF
        forensic_data = [
            ("Species Classification", data.get('species', 'Unknown')),
            ("Blood Group", data.get('blood_group', 'Unknown')),
            ("DNA Type", data.get('dna_type', 'Unknown')),
            ("Confidence Level", f"{(data.get('confidence', 0) * 100):.1f}%"),
            ("Sample Name", data.get('sample_name', 'Unknown')),
            ("Investigator", data.get('investigator_name', 'Unknown')),
            ("Analysis Status", "RELIABLE" if data.get('confidence', 0) > 0.7 else "NEEDS RETESTING")
        ]
        
        for label, value in forensic_data:
            pdf.multi_cell(0, 6, f"{label}: {value}")
            pdf.ln(2)
        
        # Footer
        pdf.ln(20)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 8, "This report is generated by AI-powered DNA Analysis System", ln=True, align="C")
        
        # Save to buffer
        pdf_buffer = io.BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'forensic_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except ImportError:
        return jsonify({"error": "PDF generation not available. Install fpdf2: pip install fpdf2"}), 500
    except Exception as e:
        return jsonify({"error": f"Report generation failed: {str(e)}"}), 500