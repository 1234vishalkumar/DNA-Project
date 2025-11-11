from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import sys
import numpy as np
from datetime import datetime
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import only essential functions
try:
    from gel_analysis import GelElectrophoresisAnalyzer, process_gel_image
    GEL_AVAILABLE = True
except ImportError:
    GEL_AVAILABLE = False

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gel_upload', methods=['POST'])
def gel_upload():
    if not GEL_AVAILABLE:
        return jsonify({"error": "Gel analysis not available"}), 500
    
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

if __name__ == '__main__':
    print("DNA Gel Analysis System")
    print(f"Gel Analysis Available: {GEL_AVAILABLE}")
    print("Starting server at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)