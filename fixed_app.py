from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import sys
import numpy as np
from datetime import datetime
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import gel analysis
try:
    from gel_analysis import GelElectrophoresisAnalyzer, process_gel_image
    GEL_AVAILABLE = True
except ImportError as e:
    print(f"Gel analysis not available: {e}")
    GEL_AVAILABLE = False

# Import DNA analysis functions (with error handling)
try:
    from utils import predict_sequence, assess_confidence, advanced_similarity_analysis, detect_mutations
    from utils import create_kmer_frequency_chart, create_confidence_pie_chart, create_similarity_chart
    from utils import parse_dna_input, save_to_database
    DNA_AVAILABLE = True
except ImportError as e:
    print(f"DNA analysis not available: {e}")
    DNA_AVAILABLE = False

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

@app.route('/')
def index():
    return render_template('index.html')

# DNA Analysis Routes
@app.route('/analyze', methods=['POST'])
def analyze():
    if not DNA_AVAILABLE:
        return jsonify({"error": "DNA analysis not available. Missing model files or dependencies."}), 500
    
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
            'confidence': float(prediction_result['confidence']),  # Ensure float
            'confidence_assessment': confidence_assessment,
            'probabilities': [float(p) for p in prediction_result['probabilities']],  # Convert to float
            'kmer_chart': kmer_chart,
            'confidence_chart': confidence_chart
        }
        
        # Save to database (simplified to avoid column issues)
        try:
            save_to_database(result_data)
        except Exception as db_error:
            print(f"Database save error: {db_error}")
            # Continue without saving to database
        
        return json.dumps(result_data, cls=NumpyEncoder), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare():
    if not DNA_AVAILABLE:
        return jsonify({"error": "DNA analysis not available"}), 500
    
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
        
        return json.dumps(result, cls=NumpyEncoder), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Gel Analysis Routes
@app.route('/gel_upload', methods=['POST'])
def gel_upload():
    if not GEL_AVAILABLE:
        return jsonify({"error": "Gel analysis not available. Missing dependencies."}), 500
    
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
        
        return json.dumps(result, cls=NumpyEncoder), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gel_compare', methods=['POST'])
def gel_compare():
    if not GEL_AVAILABLE:
        return jsonify({"error": "Gel analysis not available"}), 500
    
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
        
        return json.dumps(comparison_result, cls=NumpyEncoder), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gel_report', methods=['POST'])
def gel_report():
    if not GEL_AVAILABLE:
        return jsonify({"error": "Gel analysis not available"}), 500
    
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({"error": "Image path required"}), 400
        
        # Generate report using the analyzer
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(image_path)
        analyzer.detect_lanes()
        analyzer.detect_all_bands()
        
        # Generate report
        report_path = os.path.join(UPLOAD_FOLDER, f"gel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report = analyzer.generate_report(output_path=report_path)
        
        return send_file(report_path, as_attachment=True, download_name='gel_analysis_report.json')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Placeholder routes for other features
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
    print(f"DNA Analysis Available: {'Yes' if DNA_AVAILABLE else 'No'}")
    print(f"Gel Analysis Available: {'Yes' if GEL_AVAILABLE else 'No'}")
    if not DNA_AVAILABLE:
        print("To enable DNA analysis, ensure model files are in 'model/' directory")
    if not GEL_AVAILABLE:
        print("To enable gel analysis, install: pip install opencv-python scipy matplotlib")
    print("\nStarting web server...")
    print("Access at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)