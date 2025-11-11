from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os, json, sys
from werkzeug.utils import secure_filename
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_simple import *

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = "uploads"
REPORTS_FOLDER = "reports"
AUDIO_FOLDER = "audio"

for folder in [UPLOAD_FOLDER, REPORTS_FOLDER, AUDIO_FOLDER]:
    os.makedirs(folder, exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'fasta', 'fa', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- ROUTE 1: HOME PAGE ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- ROUTE 2: ENHANCED DNA ANALYSIS ----------
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get input data
        investigator_name = request.form.get('investigator_name', 'Unknown')
        sample_name = request.form.get('sample_name', 'Sample')
        input_type = request.form.get('input_type', 'text')
        
        # Get DNA sequence
        if input_type == 'text':
            sequence = request.form.get('dna_sequence', '')
            if not sequence:
                return jsonify({"error": "No DNA sequence provided"}), 400
        else:
            file = request.files.get('file')
            if not file or not allowed_file(file.filename):
                return jsonify({"error": "Invalid file format"}), 400
            
            sequence = parse_dna_input(file.read(), file.filename)
            if not sequence:
                return jsonify({"error": "Could not parse DNA sequence from file"}), 400
        
        # Perform prediction
        prediction_result = predict_sequence(sequence)
        confidence_assessment = assess_confidence(prediction_result['confidence'])
        
        # Create visualizations
        kmer_chart = create_kmer_frequency_chart(sequence)
        confidence_chart = create_confidence_pie_chart(prediction_result['probabilities'])
        
        # Prepare result data
        result_data = {
            'investigator_name': investigator_name,
            'sample_name': sample_name,
            'dna_sequence': sequence[:100] + '...' if len(sequence) > 100 else sequence,
            'prediction': prediction_result['prediction'],
            'confidence': prediction_result['confidence'],
            'confidence_assessment': confidence_assessment,
            'probabilities': prediction_result['probabilities'],
            'kmer_chart': kmer_chart,
            'confidence_chart': confidence_chart
        }
        
        # Save to database
        save_to_database(result_data)
        
        return jsonify(result_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- ROUTE 3: ADVANCED DNA COMPARISON ----------
@app.route('/compare', methods=['POST'])
def compare():
    try:
        # Get sequences from files or text input
        seq1_input = request.form.get('sequence1') or request.files.get('file1')
        seq2_input = request.form.get('sequence2') or request.files.get('file2')
        
        if not seq1_input or not seq2_input:
            return jsonify({"error": "Provide two DNA sequences for comparison"}), 400
        
        # Parse sequences
        if isinstance(seq1_input, str):
            seq1 = seq1_input
        else:
            seq1 = parse_dna_input(seq1_input.read(), seq1_input.filename)
            
        if isinstance(seq2_input, str):
            seq2 = seq2_input
        else:
            seq2 = parse_dna_input(seq2_input.read(), seq2_input.filename)
        
        if not seq1 or not seq2:
            return jsonify({"error": "Could not parse DNA sequences"}), 400
        
        # Perform advanced similarity analysis
        similarity_result = advanced_similarity_analysis(seq1, seq2)
        mutation_info = detect_mutations(seq1, seq2)
        
        # Create similarity visualization
        similarity_chart = create_similarity_chart(similarity_result)
        
        result = {
            **similarity_result,
            **mutation_info,
            'similarity_chart': similarity_chart,
            'sequence1_length': len(seq1),
            'sequence2_length': len(seq2)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- ROUTE 4: GENERATE COMPREHENSIVE REPORT ----------
@app.route('/report', methods=['POST'])
def report():
    try:
        data = request.get_json()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"forensic_report_{timestamp}.pdf"
        pdf_path = os.path.join(REPORTS_FOLDER, pdf_filename)
        
        generate_report(data, output_path=pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- ROUTE 5: DATABASE HISTORY ----------
@app.route('/history')
def analysis_history():
    try:
        history = get_analysis_history()
        return render_template('history.html', history=history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def api_history():
    try:
        history = get_analysis_history()
        # Convert to JSON-friendly format
        history_data = []
        for row in history:
            history_data.append({
                'id': row[0],
                'timestamp': row[1],
                'investigator_name': row[2],
                'sample_name': row[3],
                'prediction': row[5],
                'confidence': row[6]
            })
        return jsonify(history_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- ROUTE 6: DASHBOARD WITH ANALYTICS ----------
@app.route('/dashboard')
def dashboard():
    try:
        # Get recent analysis statistics
        history = get_analysis_history()
        
        # Calculate statistics
        total_analyses = len(history)
        high_confidence_count = sum(1 for row in history if row[6] and row[6] > 0.8)
        
        stats = {
            'total_analyses': total_analyses,
            'high_confidence_analyses': high_confidence_count,
            'confidence_rate': (high_confidence_count / total_analyses * 100) if total_analyses > 0 else 0
        }
        
        return render_template('dashboard.html', stats=stats, recent_history=history[:10])
        
    except Exception as e:
        return render_template('dashboard.html', stats={'total_analyses': 0, 'high_confidence_analyses': 0, 'confidence_rate': 0}, recent_history=[])

# ---------- ROUTE 7: BATCH PROCESSING ----------
@app.route('/batch_process', methods=['POST'])
def batch_process():
    try:
        files = request.files.getlist('batch_files')
        if not files:
            return jsonify({"error": "No files uploaded for batch processing"}), 400
        
        results = []
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    sequence = parse_dna_input(file.read(), file.filename)
                    if sequence:
                        prediction = predict_sequence(sequence)
                        confidence_assessment = assess_confidence(prediction['confidence'])
                        
                        results.append({
                            'filename': file.filename,
                            'prediction': prediction['prediction'],
                            'confidence': prediction['confidence'],
                            'status': confidence_assessment['status'],
                            'success': True
                        })
                    else:
                        results.append({
                            'filename': file.filename,
                            'error': 'Could not parse DNA sequence',
                            'success': False
                        })
                except Exception as e:
                    results.append({
                        'filename': file.filename,
                        'error': str(e),
                        'success': False
                    })
        
        return jsonify({'results': results, 'total_processed': len(results)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- ROUTE 8: API ENDPOINTS FOR EXTERNAL ACCESS ----------
@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for external applications"""
    try:
        data = request.get_json()
        sequence = data.get('sequence', '')
        
        if not sequence:
            return jsonify({"error": "DNA sequence required"}), 400
        
        result = predict_sequence(sequence)
        confidence_assessment = assess_confidence(result['confidence'])
        
        return jsonify({
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'status': confidence_assessment['status'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """API endpoint for sequence comparison"""
    try:
        data = request.get_json()
        seq1 = data.get('sequence1', '')
        seq2 = data.get('sequence2', '')
        
        if not seq1 or not seq2:
            return jsonify({"error": "Two DNA sequences required"}), 400
        
        result = advanced_similarity_analysis(seq1, seq2)
        mutations = detect_mutations(seq1, seq2)
        
        return jsonify({
            **result,
            **mutations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- RUN SERVER ----------
if __name__ == "__main__":
    print("Starting Enhanced DNA Forensic Analysis System...")
    print("Web Interface: http://localhost:5000")
    print("Dashboard: http://localhost:5000/dashboard")
    print("History: http://localhost:5000/history")
    print("API Endpoints: /api/predict, /api/compare, /api/history")
    app.run(debug=True, host='0.0.0.0', port=5000)