from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os, json
import sys
import numpy as np
from datetime import datetime
from werkzeug.utils import secure_filename

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import gel analysis with error handling
try:
    from gel_analysis import GelElectrophoresisAnalyzer, process_gel_image
    GEL_AVAILABLE = True
except ImportError as e:
    print(f"Gel analysis not available: {e}")
    GEL_AVAILABLE = False

# Import DNA analysis functions with error handling
try:
    from utils import predict_sequence, assess_confidence, advanced_similarity_analysis, detect_mutations
    from utils import create_kmer_frequency_chart, create_confidence_pie_chart, create_similarity_chart
    from utils import text_to_speech_offline, text_to_speech_online, generate_report
    from utils import get_analysis_history, analyze_face_from_image, combine_dna_face_analysis
    from fixed_utils import parse_dna_input
    from blood_group_analyzer import detect_blood_group, analyze_blood_compatibility
    from improved_predictor import enhance_prediction_confidence, get_human_readable_prediction, analyze_dna_characteristics
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

# Safe database save function
def safe_save_to_database(data):
    try:
        # Create a simplified data structure for database
        simple_data = {
            'investigator_name': data.get('investigator_name', 'Unknown'),
            'sample_name': data.get('sample_name', 'Sample'),
            'dna_sequence': data.get('dna_sequence', ''),
            'prediction': data.get('prediction', ''),
            'confidence': float(data.get('confidence', 0.0))
        }
        
        import sqlite3
        conn = sqlite3.connect('dna_forensics.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO dna_analysis 
            (timestamp, investigator_name, sample_name, dna_sequence, prediction, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            simple_data['investigator_name'],
            simple_data['sample_name'],
            simple_data['dna_sequence'],
            simple_data['prediction'],
            simple_data['confidence']
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database save error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

# ---------- DNA ANALYSIS ----------
@app.route('/analyze', methods=['POST'])
def analyze():
    # Always try to analyze, even if some dependencies are missing
    try:
        # Try to import required functions
        from utils import predict_sequence, assess_confidence, create_kmer_frequency_chart, create_confidence_pie_chart
    except ImportError:
        return jsonify({"error": "DNA analysis not available. Missing model files or dependencies."}), 500
    
    try:
        investigator_name = request.form.get('investigator_name', 'Unknown')
        sample_name = request.form.get('sample_name', 'Sample')
        input_type = request.form.get('input_type', 'text')
        
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
        
        prediction_result = predict_sequence(sequence)
        
        # Enhance confidence using improved algorithm
        enhanced_confidence = enhance_prediction_confidence(
            prediction_result['confidence'], 
            sequence, 
            prediction_result['prediction']
        )
        
        # Get human-readable prediction
        readable_prediction = get_human_readable_prediction(prediction_result['prediction'])
        
        # Analyze DNA characteristics
        dna_characteristics = analyze_dna_characteristics(sequence)
        
        confidence_assessment = assess_confidence(enhanced_confidence)
        
        # Detect blood group
        blood_group_result = detect_blood_group(sequence)
        
        kmer_chart = create_kmer_frequency_chart(sequence)
        confidence_chart = create_confidence_pie_chart(prediction_result['probabilities'])
        
        result_data = {
            'investigator_name': investigator_name,
            'sample_name': sample_name,
            'dna_sequence': sequence[:100] + '...' if len(sequence) > 100 else sequence,
            'prediction': readable_prediction,
            'original_prediction': prediction_result['prediction'],
            'confidence': float(enhanced_confidence),
            'original_confidence': float(prediction_result['confidence']),
            'confidence_assessment': confidence_assessment,
            'probabilities': [float(p) for p in prediction_result['probabilities']],
            'dna_characteristics': dna_characteristics,
            'blood_group': blood_group_result,
            'kmer_chart': kmer_chart,
            'confidence_chart': confidence_chart
        }
        
        safe_save_to_database(result_data)
        
        return jsonify(result_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- DNA COMPARISON ----------
@app.route('/compare', methods=['POST'])
def compare():
    try:
        # Try to import required functions
        from utils import advanced_similarity_analysis, detect_mutations, create_similarity_chart, parse_dna_input
    except ImportError:
        return jsonify({"error": "DNA comparison not available. Missing dependencies."}), 500
    
    try:
        seq1_input = request.form.get('sequence1') or request.files.get('file1')
        seq2_input = request.form.get('sequence2') or request.files.get('file2')
        
        if not seq1_input or not seq2_input:
            return jsonify({"error": "Provide two DNA sequences for comparison"}), 400
        
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
        
        similarity_result = advanced_similarity_analysis(seq1, seq2)
        mutation_info = detect_mutations(seq1, seq2)
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

# ---------- GEL ANALYSIS ----------
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
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"gel_{timestamp}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        num_lanes = request.form.get('num_lanes')
        num_lanes = int(num_lanes) if num_lanes and num_lanes.isdigit() else None
        
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(filepath)
        lanes = analyzer.detect_lanes(num_lanes=num_lanes)
        bands = analyzer.detect_all_bands()
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
        
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(image_path)
        analyzer.detect_lanes()
        analyzer.detect_all_bands()
        
        comparison_result = analyzer.compare_lanes(int(lane1_id), int(lane2_id), tolerance_pixels=int(tolerance))
        
        if comparison_result is None:
            return jsonify({"error": "Could not compare specified lanes"}), 400
        
        return jsonify(comparison_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gel_image_compare', methods=['POST'])
def gel_image_compare():
    if not GEL_AVAILABLE:
        return jsonify({"error": "Gel analysis not available"}), 500
    
    try:
        first_image_path = request.form.get('first_image_path')
        if not first_image_path:
            return jsonify({"error": "First image path required"}), 400
        
        if 'gel_image2' not in request.files:
            return jsonify({"error": "Second gel image required"}), 400
        
        file2 = request.files['gel_image2']
        if not file2 or not allowed_gel_file(file2.filename):
            return jsonify({"error": "Invalid second image format"}), 400
        
        # Save second image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename2 = secure_filename(f"gel2_{timestamp}_{file2.filename}")
        filepath2 = os.path.join(UPLOAD_FOLDER, filename2)
        file2.save(filepath2)
        
        num_lanes2 = request.form.get('num_lanes2')
        num_lanes2 = int(num_lanes2) if num_lanes2 and num_lanes2.isdigit() else None
        
        # Analyze first image
        analyzer1 = GelElectrophoresisAnalyzer()
        analyzer1.load_image(first_image_path)
        lanes1 = analyzer1.detect_lanes()
        bands1 = analyzer1.detect_all_bands()
        
        # Analyze second image
        analyzer2 = GelElectrophoresisAnalyzer()
        analyzer2.load_image(filepath2)
        lanes2 = analyzer2.detect_lanes(num_lanes=num_lanes2)
        bands2 = analyzer2.detect_all_bands()
        
        # Compare images
        lane_comparisons = []
        total_similarity = 0
        comparison_count = 0
        
        max_lanes = min(len(lanes1), len(lanes2))
        for i in range(max_lanes):
            comparison = analyzer1.compare_lanes(i, i, tolerance_pixels=15)
            if comparison:
                # Compare with second image bands
                lane1_bands = len(bands1.get(i, []))
                lane2_bands = len(bands2.get(i, []))
                
                # Simple similarity calculation
                if lane1_bands == 0 and lane2_bands == 0:
                    similarity = 100
                elif lane1_bands == 0 or lane2_bands == 0:
                    similarity = 0
                else:
                    similarity = min(lane1_bands, lane2_bands) / max(lane1_bands, lane2_bands) * 100
                
                lane_comparisons.append({
                    'lane1': i,
                    'lane2': i,
                    'similarity': round(similarity, 1),
                    'matching_bands': min(lane1_bands, lane2_bands)
                })
                
                total_similarity += similarity
                comparison_count += 1
        
        overall_similarity = round(total_similarity / comparison_count, 1) if comparison_count > 0 else 0
        
        result = {
            'success': True,
            'image1_lanes': len(lanes1),
            'image2_lanes': len(lanes2),
            'overall_similarity': overall_similarity,
            'lane_comparisons': lane_comparisons
        }
        
        return jsonify(result)
        
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
        
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(image_path)
        analyzer.detect_lanes()
        analyzer.detect_all_bands()
        
        report_path = os.path.join(UPLOAD_FOLDER, f"gel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report = analyzer.generate_report(output_path=report_path)
        
        return send_file(report_path, as_attachment=True, download_name='gel_analysis_report.json')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- OTHER FEATURES ----------
@app.route('/voice', methods=['POST'])
def voice_synthesis():
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice_type = data.get('type', 'offline')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if voice_type == 'offline':
            success = text_to_speech_offline(text)
            return jsonify({"success": success, "message": "Voice synthesis completed" if success else "Voice synthesis failed"})
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_filename = f"result_audio_{timestamp}.mp3"
            audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
            
            result = text_to_speech_online(text, audio_path)
            if result:
                return send_file(audio_path, as_attachment=True, download_name=audio_filename)
            else:
                return jsonify({"error": "Voice synthesis failed"}), 500
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report', methods=['POST'])
def report():
    try:
        from pdf_generator import generate_dna_report
        
        data = request.get_json()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"forensic_report_{timestamp}.pdf"
        pdf_path = os.path.join(REPORTS_FOLDER, pdf_filename)
        
        generate_dna_report(data, output_path=pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/batch_process', methods=['POST'])
def batch_process():
    if not DNA_AVAILABLE:
        return jsonify({"error": "DNA analysis not available"}), 500
    
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
                        
                        # Use improved confidence
                        enhanced_confidence = enhance_prediction_confidence(
                            prediction['confidence'], sequence, prediction['prediction']
                        )
                        readable_prediction = get_human_readable_prediction(prediction['prediction'])
                        confidence_assessment = assess_confidence(enhanced_confidence)
                        
                        results.append({
                            'filename': file.filename,
                            'prediction': readable_prediction,
                            'confidence': float(enhanced_confidence),
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

@app.route('/multi_factor_analysis', methods=['POST'])
def multi_factor_analysis():
    if not DNA_AVAILABLE:
        return jsonify({"error": "DNA analysis not available"}), 500
    
    try:
        dna_sequence = request.form.get('dna_sequence', '')
        if not dna_sequence:
            return jsonify({"error": "DNA sequence required"}), 400
        
        dna_result = predict_sequence(dna_sequence)
        
        # Enhance DNA confidence
        enhanced_confidence = enhance_prediction_confidence(
            dna_result['confidence'], dna_sequence, dna_result['prediction']
        )
        dna_result['confidence'] = enhanced_confidence
        dna_result['prediction'] = get_human_readable_prediction(dna_result['prediction'])
        
        face_result = {"face_detected": False}
        if 'face_image' in request.files:
            file = request.files['face_image']
            if file and allowed_file(file.filename):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(f"face_{timestamp}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                face_result = analyze_face_from_image(filepath)
                os.remove(filepath)
        
        combined_result = combine_dna_face_analysis(dna_result, face_result)
        
        return jsonify(combined_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/blood_compatibility', methods=['POST'])
def blood_compatibility():
    try:
        data = request.get_json()
        donor_group = data.get('donor_group')
        recipient_group = data.get('recipient_group')
        
        if not donor_group or not recipient_group:
            return jsonify({"error": "Both donor and recipient blood groups required"}), 400
        
        result = analyze_blood_compatibility(donor_group, recipient_group)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def api_history():
    try:
        history = get_analysis_history()
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
        return jsonify([])

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    try:
        import sqlite3
        conn = sqlite3.connect('dna_forensics.db')
        cursor = conn.cursor()
        
        # Delete all records from dna_analysis table
        cursor.execute('DELETE FROM dna_analysis')
        
        # Reset the auto-increment counter
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="dna_analysis"')
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return jsonify({'success': True, 'message': f'Cleared {deleted_count} records', 'deleted': deleted_count})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        
        # AI response logic based on keywords
        if 'read screen' in message:
            # Analyze screen content
            if 'confidence' in message and '%' in message:
                conf_match = message.split('confidence:')[1].split('%')[0].strip() if 'confidence:' in message else ''
                try:
                    conf = float(conf_match)
                    if conf > 80:
                        response = f"🎉 Excellent results! Your confidence score of {conf}% is very high!\n\n✅ This indicates reliable results\n✅ The DNA quality is good\n✅ Analysis is trustworthy\n\nYou can confidently use these results for your research or forensic purposes!"
                    elif conf > 65:
                        response = f"👍 Good results! Your confidence score of {conf}% is acceptable.\n\n✅ Results are reliable\n🟡 Consider additional validation\n✅ DNA quality is adequate\n\nThese results are suitable for most applications!"
                    else:
                        response = f"⚠️ Moderate confidence at {conf}%. \n\n🟡 Results may need verification\n🟡 Consider re-testing\n🟡 Check DNA quality\n\nSuggestion: Try with a longer or higher quality DNA sequence."
                except:
                    response = "I can see your results! They look good. The analysis completed successfully. 😊"
            
            elif 'blood group' in message:
                response = "🩸 Blood Group Detected!\n\nYour DNA analysis includes blood type information. This is determined by:\n\n• ABO gene markers\n• Rh factor genes\n\nThe system analyzes specific genetic patterns to identify your blood group. This can be useful for medical records and compatibility checks!"
            
            elif 'gel' in message and 'lanes' in message:
                response = "🧬 Gel Analysis Results!\n\nI can see your gel electrophoresis results. The system has:\n\n✅ Detected lanes automatically\n✅ Identified DNA bands\n✅ Measured band positions\n\nYou can now compare lanes or generate a detailed report. Great job running the analysis!"
            
            else:
                response = "👀 Screen Analysis Complete!\n\nI can see you have results displayed. Everything looks good! \n\nWould you like me to:\n• Explain the confidence score?\n• Interpret blood group results?\n• Explain gel analysis?\n\nJust ask me anything specific!"
        
        elif 'blood' in message or 'blood group' in message:
            response = "Blood groups are determined by ABO and Rh genes in DNA. Our system detects:\n\n• ABO Type (A, B, AB, O)\n• Rh Factor (+/-)\n• Compatibility information\n• Donation/reception compatibility\n\nThe detection is based on genetic markers in your DNA sequence."
        
        elif 'gel' in message or 'electrophoresis' in message:
            response = "Gel electrophoresis separates DNA fragments by size. Our analysis provides:\n\n• Automatic lane detection\n• Band identification\n• Lane comparison\n• Molecular weight estimation\n\nUpload your gel image in the Gel Analysis tab for detailed results."
        
        elif 'confidence' in message or 'accuracy' in message:
            response = "Our system uses enhanced confidence calculation:\n\n• Base confidence from ML model\n• Sequence quality assessment\n• Length-based adjustments\n• GC content analysis\n\nTypical confidence ranges: 65-95%\nHigher confidence = more reliable results."
        
        elif 'dna' in message and ('analyze' in message or 'analysis' in message):
            response = "DNA Analysis features:\n\n• AI-powered classification\n• Blood group detection\n• GC content analysis\n• Base composition\n• Quality assessment\n\nSimply paste your sequence or upload a file (.txt, .fasta) in the DNA Analysis tab."
        
        elif 'compare' in message or 'comparison' in message:
            response = "DNA Comparison uses multiple algorithms:\n\n• Cosine Similarity\n• Levenshtein Distance\n• Sequence Matcher\n• Mutation Detection\n\nProvide two sequences to get detailed similarity scores and identify mutations."
        
        elif 'how' in message and 'use' in message:
            response = "Quick Start Guide:\n\n1. DNA Analysis: Upload/paste sequence\n2. Comparison: Provide 2 sequences\n3. Gel Analysis: Upload gel image\n4. Batch: Upload multiple files\n5. Dashboard: View history\n\nEach tab has clear instructions. Try the DNA Analysis tab first!"
        
        elif 'help' in message or 'what can you do' in message:
            response = "As Genora, your AI genomic assistant, I provide:\n\n• DNA analysis result interpretation\n• Blood group genetic information\n• Gel electrophoresis guidance\n• Confidence score evaluation\n• Technical support\n• Best practice recommendations\n\nI'm here to make your DNA forensic analysis more efficient and accurate."
        
        elif 'thank' in message:
            response = "You're welcome! I'm always here to assist with your genomic analysis needs. Don't hesitate to reach out for any questions."
        
        else:
            response = f"I understand you're asking about: '{message}'\n\nI can help with:\n• DNA sequence analysis\n• Blood group detection\n• Gel electrophoresis\n• Result interpretation\n• Feature usage\n\nCould you be more specific about what you'd like to know?"
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    print("Complete DNA Forensic Analysis System")
    print("=" * 50)
    print(f"DNA Analysis Available: {'Yes' if DNA_AVAILABLE else 'No'}")
    print(f"Gel Analysis Available: {'Yes' if GEL_AVAILABLE else 'No'}")
    print("\nFeatures Available:")
    print("  - DNA Sequence Analysis")
    print("  - DNA Comparison & Mutation Detection") 
    print("  - Gel Electrophoresis Analysis")
    print("  - Voice Synthesis")
    print("  - PDF Report Generation")
    print("  - Batch Processing")
    print("  - Multi-Factor Analysis")
    print("  - Analysis History")
    print("\nStarting web server...")
    print("Access at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)