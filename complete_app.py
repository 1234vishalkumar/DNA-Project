from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import sys
import base64
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

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'txt', 'fasta', 'fa'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# Gel Analysis Routes
@app.route('/gel_upload', methods=['POST'])
def gel_upload():
    if not GEL_AVAILABLE:
        return jsonify({"error": "Gel analysis not available. Missing dependencies."}), 500
    
    try:
        if 'gel_image' not in request.files:
            return jsonify({"error": "No gel image uploaded"}), 400
        
        file = request.files['gel_image']
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid image format"}), 400
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"gel_{timestamp}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Analyze
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(filepath)
        
        num_lanes = request.form.get('num_lanes')
        num_lanes = int(num_lanes) if num_lanes and num_lanes.isdigit() else None
        
        lanes = analyzer.detect_lanes(num_lanes=num_lanes)
        bands = analyzer.detect_all_bands()
        measurements = analyzer.measure_bands()
        
        return jsonify({
            'success': True,
            'image_path': filepath,
            'lanes_detected': len(lanes),
            'lanes': lanes,
            'bands': bands,
            'measurements': measurements,
            'total_bands': sum(len(lane_bands) for lane_bands in bands.values())
        })
        
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
        
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(image_path)
        analyzer.detect_lanes()
        analyzer.detect_all_bands()
        
        comparison_result = analyzer.compare_lanes(int(lane1_id), int(lane2_id), tolerance_pixels=int(tolerance))
        
        return jsonify(comparison_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gel_report', methods=['POST'])
def gel_report():
    if not GEL_AVAILABLE:
        return jsonify({"error": "Gel analysis not available"}), 500
    
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
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
@app.route('/analyze', methods=['POST'])
def analyze():
    return jsonify({"error": "DNA sequence analysis not implemented yet"}), 501

@app.route('/compare', methods=['POST'])
def compare():
    return jsonify({"error": "DNA comparison not implemented yet"}), 501

@app.route('/batch_process', methods=['POST'])
def batch_process():
    return jsonify({"error": "Batch processing not implemented yet"}), 501

@app.route('/multi_factor_analysis', methods=['POST'])
def multi_factor_analysis():
    return jsonify({"error": "Multi-factor analysis not implemented yet"}), 501

@app.route('/voice', methods=['POST'])
def voice():
    return jsonify({"error": "Voice synthesis not implemented yet"}), 501

@app.route('/report', methods=['POST'])
def report():
    return jsonify({"error": "PDF report generation not implemented yet"}), 501

@app.route('/api/history')
def api_history():
    return jsonify([])

if __name__ == '__main__':
    print("Complete DNA Forensic Analysis System")
    print("=" * 50)
    print(f"Gel Analysis Available: {'Yes' if GEL_AVAILABLE else 'No'}")
    if not GEL_AVAILABLE:
        print("To enable gel analysis, install: pip install opencv-python scipy matplotlib")
    print("\nStarting web server...")
    print("Access at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)