from flask import Flask, render_template, request, jsonify, send_file
import os
import base64
from io import BytesIO
from gel_analysis import GelElectrophoresisAnalyzer
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        # Save uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Analyze gel
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(filepath)
        
        num_lanes = request.form.get('num_lanes')
        num_lanes = int(num_lanes) if num_lanes else None
        
        lanes = analyzer.detect_lanes(num_lanes=num_lanes)
        bands = analyzer.detect_all_bands()
        measurements = analyzer.measure_bands()
        
        # Generate visualization
        viz_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.png')
        analyzer.visualize_analysis(save_path=viz_path)
        
        # Convert image to base64 for display
        with open(viz_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
        
        return jsonify({
            'success': True,
            'lanes': len(lanes),
            'total_bands': sum(len(lane_bands) for lane_bands in bands.values()),
            'measurements': measurements,
            'image': img_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)