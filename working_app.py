from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os, json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *
from Bio import SeqIO
from werkzeug.utils import secure_filename
from gel_analysis import GelElectrophoresisAnalyzer, process_gel_image

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = "app/uploads"
REPORTS_FOLDER = "app/reports"
AUDIO_FOLDER = "app/audio"

for folder in [UPLOAD_FOLDER, REPORTS_FOLDER, AUDIO_FOLDER]:
    os.makedirs(folder, exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'fasta', 'fa', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
GEL_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_gel_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in GEL_EXTENSIONS

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

# ---------- GEL ELECTROPHORESIS ANALYSIS ----------
@app.route('/gel_upload', methods=['POST'])
def gel_upload():
    """Upload and analyze gel electrophoresis image"""
    try:
        if 'gel_image' not in request.files:
            return jsonify({"error": "No gel image uploaded"}), 400
        
        file = request.files['gel_image']
        if not file or not allowed_gel_file(file.filename):
            return jsonify({"error": "Invalid image format. Use JPG, PNG, BMP, or TIFF"}), 400
        
        # Save uploaded image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"gel_{timestamp}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get parameters
        num_lanes = request.form.get('num_lanes')
        num_lanes = int(num_lanes) if num_lanes and num_lanes.isdigit() else None
        
        # Initialize analyzer
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(filepath)
        
        # Detect lanes
        lanes = analyzer.detect_lanes(num_lanes=num_lanes)
        
        # Detect bands
        bands = analyzer.detect_all_bands()
        
        # Generate measurements
        measurements = analyzer.measure_bands()
        
        result = {
            'success': True,
            'image_path': filepath,
            'lanes_detected': len(lanes),
            'lanes': lanes,
            'bands': bands,
            'measurements': measurements,
            'total_bands': sum(len(lane_bands) for lane_bands in bands.values())
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gel_compare', methods=['POST'])
def gel_compare():
    """Compare two lanes in gel electrophoresis"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        lane1_id = data.get('lane1_id')
        lane2_id = data.get('lane2_id')
        tolerance = data.get('tolerance', 10)
        
        if not all([image_path, lane1_id is not None, lane2_id is not None]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Initialize analyzer
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(image_path)
        analyzer.detect_lanes()
        analyzer.detect_all_bands()
        
        # Perform comparison
        comparison_result = analyzer.compare_lanes(int(lane1_id), int(lane2_id), tolerance_pixels=int(tolerance))
        
        if comparison_result is None:
            return jsonify({"error": "Could not compare specified lanes"}), 400
        
        return jsonify(comparison_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gel_report', methods=['POST'])
def gel_report():
    """Generate comprehensive gel analysis report"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({"error": "Image path required"}), 400
        
        # Process gel image
        result = process_gel_image(
            image_path, 
            compare_lanes=data.get('compare_lanes'),
            output_dir=UPLOAD_FOLDER
        )
        
        return send_file(result['report_path'], as_attachment=True, download_name=os.path.basename(result['report_path']))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Placeholder routes for missing features
@app.route('/report', methods=['POST'])
def report():
    return jsonify({"error": "PDF report generation not implemented yet"}), 501

@app.route('/voice', methods=['POST'])
def voice():
    return jsonify({"error": "Voice synthesis not implemented yet"}), 501

@app.route('/batch_process', methods=['POST'])
def batch_process():
    return jsonify({"error": "Batch processing not implemented yet"}), 501

@app.route('/multi_factor_analysis', methods=['POST'])
def multi_factor_analysis():
    return jsonify({"error": "Multi-factor analysis not implemented yet"}), 501

@app.route('/api/history')
def api_history():
    return jsonify([])

if __name__ == '__main__':
    print("Complete DNA Forensic Analysis System")
    print("=" * 50)
    print("Features Available:")
    print("  - Gel Electrophoresis Analysis")
    print("  - DNA Sequence Analysis (if utils available)")
    print("  - Lane Comparison")
    print("  - Report Generation")
    print("\nStarting web server...")
    print("Access at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)