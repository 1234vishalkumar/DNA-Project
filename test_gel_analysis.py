#!/usr/bin/env python3
"""
Test script for Gel Electrophoresis Analysis System
Tests the new gel analysis features
"""

import os
import sys
import numpy as np
import cv2
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gel_analysis import GelElectrophoresisAnalyzer, process_gel_image

def create_synthetic_gel_image(width=800, height=600, num_lanes=6, filename="test_gel.png"):
    """Create a synthetic gel electrophoresis image for testing"""
    
    # Create base image (dark background)
    img = np.ones((height, width, 3), dtype=np.uint8) * 30
    
    # Calculate lane positions
    lane_width = width // num_lanes
    
    # Add lanes with bands
    for lane_idx in range(num_lanes):
        x_start = lane_idx * lane_width + 10
        x_end = (lane_idx + 1) * lane_width - 10
        
        # Add some random bands in each lane
        num_bands = np.random.randint(3, 8)
        band_positions = np.random.randint(50, height-50, num_bands)
        band_positions = np.sort(band_positions)
        
        for band_pos in band_positions:
            # Create band (bright horizontal line)
            band_intensity = np.random.randint(150, 255)
            band_thickness = np.random.randint(3, 8)
            
            cv2.rectangle(img, 
                         (x_start, band_pos - band_thickness//2), 
                         (x_end, band_pos + band_thickness//2), 
                         (band_intensity, band_intensity, band_intensity), 
                         -1)
    
    # Add some noise
    noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)
    
    # Save image
    cv2.imwrite(filename, img)
    print(f"✅ Created synthetic gel image: {filename}")
    return filename

def test_gel_analysis_basic():
    """Test basic gel analysis functionality"""
    print("🧪 Testing Basic Gel Analysis...")
    
    # Create test image
    test_image = create_synthetic_gel_image()
    
    try:
        # Initialize analyzer
        analyzer = GelElectrophoresisAnalyzer()
        
        # Load image
        analyzer.load_image(test_image)
        print("✅ Image loaded successfully")
        
        # Detect lanes
        lanes = analyzer.detect_lanes(num_lanes=6)
        print(f"✅ Detected {len(lanes)} lanes")
        
        # Detect bands
        bands = analyzer.detect_all_bands()
        total_bands = sum(len(lane_bands) for lane_bands in bands.values())
        print(f"✅ Detected {total_bands} total bands")
        
        # Measure bands
        measurements = analyzer.measure_bands()
        print("✅ Band measurements completed")
        
        # Clean up
        if os.path.exists(test_image):
            os.remove(test_image)
        
        return True
        
    except Exception as e:
        print(f"❌ Basic gel analysis failed: {e}")
        return False

def test_lane_comparison():
    """Test lane comparison functionality"""
    print("\n⚖️ Testing Lane Comparison...")
    
    # Create test image
    test_image = create_synthetic_gel_image(num_lanes=4)
    
    try:
        # Initialize analyzer
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(test_image)
        analyzer.detect_lanes(num_lanes=4)
        analyzer.detect_all_bands()
        
        # Compare lanes 0 and 1
        comparison_result = analyzer.compare_lanes(0, 1, tolerance_pixels=15)
        
        if comparison_result:
            print(f"✅ Lane comparison completed")
            print(f"   Similarity: {comparison_result['similarity_score']:.1f}%")
            print(f"   Matched bands: {comparison_result['matched_bands']}")
            print(f"   Lane 0 bands: {comparison_result['total_bands_lane1']}")
            print(f"   Lane 1 bands: {comparison_result['total_bands_lane2']}")
        else:
            print("❌ Lane comparison failed")
            return False
        
        # Clean up
        if os.path.exists(test_image):
            os.remove(test_image)
        
        return True
        
    except Exception as e:
        print(f"❌ Lane comparison failed: {e}")
        return False

def test_visualization():
    """Test visualization functionality"""
    print("\n📊 Testing Visualization...")
    
    # Create test image
    test_image = create_synthetic_gel_image()
    
    try:
        # Initialize analyzer
        analyzer = GelElectrophoresisAnalyzer()
        analyzer.load_image(test_image)
        analyzer.detect_lanes()
        analyzer.detect_all_bands()
        
        # Perform comparison
        comparison_result = analyzer.compare_lanes(0, 1)
        
        # Generate visualization
        viz_filename = f"test_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig = analyzer.visualize_analysis(comparison_result, save_path=viz_filename)
        
        if os.path.exists(viz_filename):
            print(f"✅ Visualization saved: {viz_filename}")
            os.remove(viz_filename)  # Clean up
        else:
            print("❌ Visualization file not created")
            return False
        
        # Clean up
        if os.path.exists(test_image):
            os.remove(test_image)
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False

def test_report_generation():
    """Test report generation functionality"""
    print("\n📄 Testing Report Generation...")
    
    # Create test image
    test_image = create_synthetic_gel_image()
    
    try:
        # Process gel image
        result = process_gel_image(
            test_image,
            num_lanes=6,
            compare_lanes=[0, 1],
            output_dir="test_output"
        )
        
        # Check if report was generated
        if os.path.exists(result['report_path']):
            print(f"✅ Report generated: {result['report_path']}")
            
            # Clean up
            os.remove(result['report_path'])
            if os.path.exists(result['visualization_path']):
                os.remove(result['visualization_path'])
            
            # Remove test output directory if empty
            try:
                os.rmdir("test_output")
            except:
                pass
        else:
            print("❌ Report file not created")
            return False
        
        # Clean up
        if os.path.exists(test_image):
            os.remove(test_image)
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n🛡️ Testing Error Handling...")
    
    try:
        analyzer = GelElectrophoresisAnalyzer()
        
        # Test with non-existent image
        try:
            analyzer.load_image("nonexistent_image.jpg")
            print("❌ Should have failed with non-existent image")
            return False
        except:
            print("✅ Properly handled non-existent image")
        
        # Test comparison without lanes
        try:
            result = analyzer.compare_lanes(0, 1)
            if result is None:
                print("✅ Properly handled comparison without lanes")
            else:
                print("❌ Should have returned None for invalid comparison")
                return False
        except:
            print("✅ Properly handled invalid comparison")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_comprehensive_gel_test():
    """Run all gel analysis tests"""
    print("🚀 Starting Comprehensive Gel Electrophoresis Analysis Test")
    print("=" * 70)
    
    tests = [
        ("Basic Gel Analysis", test_gel_analysis_basic),
        ("Lane Comparison", test_lane_comparison),
        ("Visualization", test_visualization),
        ("Report Generation", test_report_generation),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All gel analysis tests passed! System is ready.")
        print("\n📋 Gel Analysis Features Successfully Tested:")
        print("   ✅ Image Upload & Processing")
        print("   ✅ Lane Detection")
        print("   ✅ Band Detection")
        print("   ✅ Band Measurement")
        print("   ✅ Lane Comparison")
        print("   ✅ Visualization & Output")
        print("   ✅ Report Generation")
        print("   ✅ Error Handling")
        
        print("\n🌐 To test the web interface:")
        print("   1. cd app")
        print("   2. python app.py")
        print("   3. Go to http://localhost:5000")
        print("   4. Click on 'Gel Analysis' tab")
        
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the implementation.")

if __name__ == "__main__":
    run_comprehensive_gel_test()