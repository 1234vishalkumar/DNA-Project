#!/usr/bin/env python3
"""
Create test samples for DNA forensic analysis system
"""

import os
import numpy as np
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

def create_synthetic_gel_image(filename="test_gel.png", width=800, height=600, num_lanes=6):
    """Create a synthetic gel electrophoresis image"""
    if not CV2_AVAILABLE:
        print("OpenCV not available - creating text-based sample instead")
        return create_text_sample(filename.replace('.png', '.txt'))
    
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
    print(f"Created synthetic gel image: {filename}")
    return filename

def create_text_sample(filename="sample_dna.txt"):
    """Create DNA sequence sample"""
    # Generate random DNA sequence
    bases = ['A', 'T', 'G', 'C']
    sequence = ''.join(np.random.choice(bases, 500))
    
    with open(filename, 'w') as f:
        f.write(f">Sample DNA Sequence\n{sequence}\n")
    
    print(f"Created DNA sequence sample: {filename}")
    return filename

def create_all_samples():
    """Create all test samples"""
    print("Creating test samples...")
    
    # Create sample directory
    os.makedirs("test_samples", exist_ok=True)
    
    samples = []
    
    # Create gel images if OpenCV available
    if CV2_AVAILABLE:
        samples.append(create_synthetic_gel_image("test_samples/gel_sample_1.png", num_lanes=4))
        samples.append(create_synthetic_gel_image("test_samples/gel_sample_2.png", num_lanes=6))
        samples.append(create_synthetic_gel_image("test_samples/gel_comparison.png", num_lanes=8))
    
    # Create DNA sequence samples
    samples.append(create_text_sample("test_samples/dna_sample_1.txt"))
    samples.append(create_text_sample("test_samples/dna_sample_2.txt"))
    
    # Create FASTA samples
    with open("test_samples/sample.fasta", 'w') as f:
        f.write(">Sample_1\nATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG\n")
        f.write(">Sample_2\nATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCC\n")
    samples.append("test_samples/sample.fasta")
    
    print(f"\nCreated {len(samples)} test samples:")
    for sample in samples:
        print(f"  - {sample}")
    
    return samples

if __name__ == "__main__":
    create_all_samples()
    print("\nTest samples ready! Use these with the web interface.")