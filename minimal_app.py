from flask import Flask, render_template, request, jsonify
import os
import json
import joblib
import numpy as np
from datetime import datetime

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Load model artifacts
MODEL_DIR = "model"
try:
    model = joblib.load(os.path.join(MODEL_DIR, "best_model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    
    with open(os.path.join(MODEL_DIR, "kmer_vocab.json"), "r") as f:
        vocab_data = json.load(f)
    VOCAB = vocab_data["VOCAB"]
    K = vocab_data["K"]
    
    with open(os.path.join(MODEL_DIR, "label_info.json"), "r") as f:
        label_data = json.load(f)
    LABEL_MAP = {int(k): v for k, v in label_data["label_map"].items()}
    
    MODEL_LOADED = True
except Exception as e:
    print(f"Model loading failed: {e}")
    MODEL_LOADED = False

def get_kmers(seq, k=6):
    return [seq[i:i+k] for i in range(len(seq)-k+1)] if len(seq) >= k else []

def seq_to_vector(seq, k=6):
    vocab_index = {kmer: i for i, kmer in enumerate(VOCAB)}
    vec = [0] * len(VOCAB)
    for kmer in get_kmers(seq, k):
        idx = vocab_index.get(kmer)
        if idx is not None:
            vec[idx] += 1
    s = sum(vec)
    return [v/s if s > 0 else 0 for v in vec]

def predict_sequence(sequence):
    if not MODEL_LOADED:
        return {"error": "Model not loaded"}
    
    # Clean sequence
    sequence = sequence.upper().replace(' ', '').replace('\n', '')
    sequence = ''.join(c for c in sequence if c in 'ATGC')
    
    if len(sequence) < K:
        return {"error": f"Sequence too short (minimum {K} bases)"}
    
    # Convert to features
    features = np.array([seq_to_vector(sequence, K)])
    features_scaled = scaler.transform(features)
    
    # Predict
    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]
    
    return {
        "prediction": LABEL_MAP.get(prediction, "Unknown"),
        "confidence": float(max(probabilities)),
        "probabilities": {LABEL_MAP.get(i, f"Class_{i}"): float(prob) for i, prob in enumerate(probabilities)}
    }

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DNA Forensics System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            textarea { width: 100%; height: 200px; margin: 10px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .result { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DNA Forensics Analysis System</h1>
            <form id="dnaForm">
                <h3>Enter DNA Sequence:</h3>
                <textarea id="sequence" placeholder="Enter DNA sequence (ATGC)..."></textarea>
                <br>
                <button type="submit">Analyze DNA</button>
            </form>
            <div id="result" class="result" style="display:none;"></div>
        </div>
        
        <script>
            document.getElementById('dnaForm').onsubmit = function(e) {
                e.preventDefault();
                const sequence = document.getElementById('sequence').value;
                
                fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({sequence: sequence})
                })
                .then(response => response.json())
                .then(data => {
                    const resultDiv = document.getElementById('result');
                    if (data.error) {
                        resultDiv.innerHTML = '<h3>Error:</h3><p>' + data.error + '</p>';
                    } else {
                        resultDiv.innerHTML = 
                            '<h3>Analysis Results:</h3>' +
                            '<p><strong>Prediction:</strong> ' + data.prediction + '</p>' +
                            '<p><strong>Confidence:</strong> ' + (data.confidence * 100).toFixed(2) + '%</p>' +
                            '<p><strong>Sequence Length:</strong> ' + sequence.length + ' bases</p>';
                    }
                    resultDiv.style.display = 'block';
                });
            };
        </script>
    </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        sequence = data.get('sequence', '')
        
        if not sequence:
            return jsonify({"error": "No DNA sequence provided"}), 400
        
        result = predict_sequence(sequence)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("DNA Forensics System - Minimal Version")
    print(f"Model Status: {'Loaded' if MODEL_LOADED else 'Not Loaded'}")
    print("Starting server at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)