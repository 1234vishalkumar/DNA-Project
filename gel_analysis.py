try:
    import cv2
except ImportError:
    cv2 = None
import numpy as np
try:
    from scipy import ndimage
    from scipy.signal import find_peaks
except ImportError:
    ndimage = None
    find_peaks = None
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
except ImportError:
    plt = None
    Rectangle = None
import json
from datetime import datetime
import os

class GelElectrophoresisAnalyzer:
    def __init__(self):
        self.image = None
        self.processed_image = None
        self.lanes = []
        self.bands = {}
        self.lane_width = 0
        
    def load_image(self, image_path):
        """Load and preprocess gel electrophoresis image"""
        if cv2 is None:
            raise ImportError("OpenCV not installed. Run: pip install opencv-python")
        
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Validate image dimensions
        if self.image.shape[0] < 100 or self.image.shape[1] < 100:
            raise ValueError("Image too small for analysis")
        
        # Convert to grayscale for processing
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        self.processed_image = cv2.GaussianBlur(self.gray, (5, 5), 0)
        
        return True
    
    def detect_lanes(self, num_lanes=None, manual_lanes=None):
        """Detect vertical lanes in the gel image"""
        if ndimage is None or find_peaks is None:
            raise ImportError("SciPy not installed. Run: pip install scipy")
            
        if manual_lanes:
            self.lanes = manual_lanes
            return self.lanes
            
        height, width = self.processed_image.shape
        
        # Calculate vertical intensity profile
        vertical_profile = np.mean(self.processed_image, axis=0)
        
        # Smooth the profile
        vertical_profile = ndimage.gaussian_filter1d(vertical_profile, sigma=2)
        
        # Find valleys (dark regions between lanes)
        inverted_profile = np.max(vertical_profile) - vertical_profile
        peaks, _ = find_peaks(inverted_profile, height=np.mean(inverted_profile), distance=width//20)
        
        # If no lanes specified, estimate from peaks
        if num_lanes is None:
            num_lanes = len(peaks) + 1 if len(peaks) > 0 else 6
        
        # Create lane boundaries
        if len(peaks) > 0:
            lane_boundaries = [0] + peaks.tolist() + [width]
        else:
            # Equal division if no clear boundaries found
            lane_boundaries = [int(i * width / num_lanes) for i in range(num_lanes + 1)]
        
        # Create lane rectangles
        self.lanes = []
        for i in range(len(lane_boundaries) - 1):
            x1 = lane_boundaries[i]
            x2 = lane_boundaries[i + 1]
            self.lanes.append({
                'id': int(i),
                'x1': int(x1),
                'x2': int(x2),
                'y1': int(0),
                'y2': int(height),
                'width': int(x2 - x1)
            })
        
        self.lane_width = np.mean([lane['width'] for lane in self.lanes]) if self.lanes else 0
        return self.lanes
    
    def detect_bands_in_lane(self, lane_id):
        """Detect horizontal bands within a specific lane"""
        if ndimage is None or find_peaks is None:
            raise ImportError("SciPy not installed. Run: pip install scipy")
            
        if lane_id >= len(self.lanes):
            return []
        
        lane = self.lanes[lane_id]
        
        # Extract lane region
        lane_region = self.processed_image[lane['y1']:lane['y2'], lane['x1']:lane['x2']]
        
        if lane_region.size == 0:
            return []
        
        # Calculate horizontal intensity profile
        horizontal_profile = np.mean(lane_region, axis=1)
        
        # Smooth the profile
        horizontal_profile = ndimage.gaussian_filter1d(horizontal_profile, sigma=1)
        
        # Find peaks (dark bands are typical in gels)
        inverted_profile = np.max(horizontal_profile) - horizontal_profile
        
        # Improved adaptive threshold
        threshold = np.percentile(inverted_profile, 75)  # Use 75th percentile
        
        peaks, properties = find_peaks(
            inverted_profile, 
            height=threshold,
            distance=10,  # Minimum distance between bands
            width=3       # Minimum band width
        )
        
        # Extract band information
        bands = []
        for i, peak in enumerate(peaks):
            intensity = inverted_profile[peak]
            
            # Calculate band boundaries
            left_bound = peak
            right_bound = peak
            
            # Find band edges
            while left_bound > 0 and inverted_profile[left_bound] > threshold * 0.5:
                left_bound -= 1
            while right_bound < len(inverted_profile) - 1 and inverted_profile[right_bound] > threshold * 0.5:
                right_bound += 1
            
            bands.append({
                'id': int(i),
                'position': int(peak + lane['y1']),  # Global position
                'intensity': float(intensity),
                'width': int(right_bound - left_bound),
                'top': int(left_bound + lane['y1']),
                'bottom': int(right_bound + lane['y1']),
                'lane_id': int(lane_id)
            })
        
        return bands
    
    def detect_all_bands(self):
        """Detect bands in all lanes"""
        self.bands = {}
        for lane in self.lanes:
            lane_bands = self.detect_bands_in_lane(lane['id'])
            self.bands[lane['id']] = lane_bands
        
        return self.bands
    
    def measure_bands(self, ladder_lane_id=None):
        """Measure band positions and estimate sizes"""
        measurements = {}
        
        for lane_id, bands in self.bands.items():
            lane_measurements = []
            
            for band in bands:
                measurement = {
                    'band_id': band['id'],
                    'position_pixels': band['position'],
                    'intensity': band['intensity'],
                    'width_pixels': band['width'],
                    'estimated_size_bp': None  # Will be calculated if ladder provided
                }
                
                # If ladder lane provided, estimate molecular weight
                if ladder_lane_id is not None and ladder_lane_id in self.bands:
                    measurement['estimated_size_bp'] = self._estimate_molecular_weight(
                        band['position'], ladder_lane_id
                    )
                
                lane_measurements.append(measurement)
            
            measurements[lane_id] = lane_measurements
        
        return measurements
    
    def _estimate_molecular_weight(self, position, ladder_lane_id):
        """Estimate molecular weight based on ladder lane (simplified)"""
        # Standard DNA ladder sizes (example)
        standard_sizes = [10000, 8000, 6000, 5000, 4000, 3000, 2500, 2000, 1500, 1000, 750, 500, 250]
        
        ladder_bands = self.bands.get(ladder_lane_id, [])
        if len(ladder_bands) == 0:
            return None
        
        # Simple linear interpolation based on position
        ladder_positions = [band['position'] for band in ladder_bands]
        
        if len(ladder_positions) >= 2:
            # Use first and last bands for calibration
            pos_range = max(ladder_positions) - min(ladder_positions)
            size_range = max(standard_sizes[:len(ladder_positions)]) - min(standard_sizes[:len(ladder_positions)])
            
            # Linear interpolation
            relative_pos = (position - min(ladder_positions)) / pos_range if pos_range > 0 else 0
            estimated_size = max(standard_sizes[:len(ladder_positions)]) - (relative_pos * size_range)
            
            return max(100, int(estimated_size))  # Minimum 100 bp
        
        return None
    
    def compare_lanes(self, lane1_id, lane2_id, tolerance_pixels=10):
        """Compare two lanes and calculate similarity"""
        if lane1_id not in self.bands or lane2_id not in self.bands:
            return None
        
        bands1 = self.bands[lane1_id]
        bands2 = self.bands[lane2_id]
        
        matches = []
        unique_lane1 = []
        unique_lane2 = []
        
        # Find matching bands
        used_bands2 = set()
        
        for band1 in bands1:
            best_match = None
            best_distance = float('inf')
            
            for i, band2 in enumerate(bands2):
                if i in used_bands2:
                    continue
                
                distance = abs(band1['position'] - band2['position'])
                if distance <= tolerance_pixels and distance < best_distance:
                    best_match = i
                    best_distance = distance
            
            if best_match is not None:
                matches.append({
                    'band1': band1,
                    'band2': bands2[best_match],
                    'distance': best_distance
                })
                used_bands2.add(best_match)
            else:
                unique_lane1.append(band1)
        
        # Remaining bands in lane2 are unique
        for i, band2 in enumerate(bands2):
            if i not in used_bands2:
                unique_lane2.append(band2)
        
        # Calculate similarity score
        total_bands = len(bands1) + len(bands2)
        matched_bands = len(matches) * 2  # Each match counts for both lanes
        
        similarity_score = (matched_bands / total_bands * 100) if total_bands > 0 else 0
        
        return {
            'lane1_id': int(lane1_id),
            'lane2_id': int(lane2_id),
            'similarity_score': float(round(similarity_score, 2)),
            'matches': matches,
            'unique_lane1': unique_lane1,
            'unique_lane2': unique_lane2,
            'total_bands_lane1': int(len(bands1)),
            'total_bands_lane2': int(len(bands2)),
            'matched_bands': int(len(matches))
        }
    
    def visualize_analysis(self, comparison_result=None, save_path=None):
        """Create visualization of the analysis"""
        if plt is None or Rectangle is None:
            raise ImportError("Matplotlib not installed. Run: pip install matplotlib")
            
        fig, axes = plt.subplots(1, 2, figsize=(15, 8))
        
        # Original image with lanes and bands
        ax1 = axes[0]
        ax1.imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        ax1.set_title("Detected Lanes and Bands")
        
        # Draw lane boundaries
        for lane in self.lanes:
            rect = Rectangle((lane['x1'], lane['y1']), 
                           lane['x2'] - lane['x1'], 
                           lane['y2'] - lane['y1'],
                           linewidth=2, edgecolor='blue', facecolor='none')
            ax1.add_patch(rect)
            
            # Add lane number
            ax1.text(lane['x1'] + 5, lane['y1'] + 20, f"Lane {lane['id']}", 
                    color='blue', fontweight='bold')
        
        # Draw bands
        colors = ['red', 'green', 'yellow', 'cyan', 'magenta', 'orange']
        for lane_id, bands in self.bands.items():
            color = colors[lane_id % len(colors)]
            for band in bands:
                lane = self.lanes[lane_id]
                # Draw horizontal line for band
                ax1.axhline(y=band['position'], 
                           xmin=lane['x1']/self.image.shape[1], 
                           xmax=lane['x2']/self.image.shape[1],
                           color=color, linewidth=3, alpha=0.7)
        
        ax1.set_xlim(0, self.image.shape[1])
        ax1.set_ylim(self.image.shape[0], 0)
        
        # Comparison visualization
        ax2 = axes[1]
        if comparison_result:
            self._plot_comparison(ax2, comparison_result)
        else:
            ax2.text(0.5, 0.5, "No comparison selected", 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title("Lane Comparison")
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)  # Close to free memory
        
        return save_path if save_path else fig
    
    def _plot_comparison(self, ax, comparison_result):
        """Plot lane comparison results"""
        lane1_id = comparison_result['lane1_id']
        lane2_id = comparison_result['lane2_id']
        
        # Get band positions
        bands1 = self.bands[lane1_id]
        bands2 = self.bands[lane2_id]
        
        # Plot bands as horizontal bars
        y_offset = 0.1
        bar_height = 0.3
        
        # Lane 1 bands
        for band in bands1:
            color = 'green' if any(m['band1']['id'] == band['id'] for m in comparison_result['matches']) else 'red'
            ax.barh(1 + y_offset, band['intensity'], height=bar_height, 
                   left=band['position'], color=color, alpha=0.7)
        
        # Lane 2 bands
        for band in bands2:
            color = 'green' if any(m['band2']['id'] == band['id'] for m in comparison_result['matches']) else 'red'
            ax.barh(2 + y_offset, band['intensity'], height=bar_height, 
                   left=band['position'], color=color, alpha=0.7)
        
        ax.set_ylim(0.5, 3)
        ax.set_yticks([1.25, 2.25])
        ax.set_yticklabels([f'Lane {lane1_id}', f'Lane {lane2_id}'])
        ax.set_xlabel('Position (pixels)')
        ax.set_title(f'Comparison: {comparison_result["similarity_score"]:.1f}% Similar')
        
        # Add legend
        ax.plot([], [], 'g-', linewidth=5, alpha=0.7, label='Matching bands')
        ax.plot([], [], 'r-', linewidth=5, alpha=0.7, label='Unique bands')
        ax.legend()
    
    def generate_report(self, comparison_result=None, output_path="gel_analysis_report.json"):
        """Generate analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'image_info': {
                'dimensions': self.image.shape if self.image is not None else None,
                'total_lanes': len(self.lanes)
            },
            'lanes': self.lanes,
            'bands': self.bands,
            'measurements': self.measure_bands(),
            'comparison': comparison_result
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def process_gel_image(image_path, num_lanes=None, compare_lanes=None, output_dir="gel_results"):
    """Main function to process gel electrophoresis image"""
    
    # Check required dependencies
    missing_deps = []
    if cv2 is None:
        missing_deps.append("opencv-python")
    if ndimage is None or find_peaks is None:
        missing_deps.append("scipy")
    if plt is None:
        missing_deps.append("matplotlib")
    
    if missing_deps:
        raise ImportError(f"Missing required dependencies: {', '.join(missing_deps)}. Run: pip install {' '.join(missing_deps)}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize analyzer
    analyzer = GelElectrophoresisAnalyzer()
    
    # Load and process image
    analyzer.load_image(image_path)
    
    # Detect lanes
    lanes = analyzer.detect_lanes(num_lanes=num_lanes)
    print(f"Detected {len(lanes)} lanes")
    
    # Detect bands
    bands = analyzer.detect_all_bands()
    total_bands = sum(len(lane_bands) for lane_bands in bands.values())
    print(f"Detected {total_bands} total bands")
    
    # Perform comparison if requested
    comparison_result = None
    if compare_lanes and len(compare_lanes) == 2:
        comparison_result = analyzer.compare_lanes(compare_lanes[0], compare_lanes[1])
        print(f"Similarity between lanes {compare_lanes[0]} and {compare_lanes[1]}: {comparison_result['similarity_score']:.1f}%")
    
    # Generate visualization
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    viz_path = os.path.join(output_dir, f"gel_analysis_{timestamp}.png")
    analyzer.visualize_analysis(comparison_result, save_path=viz_path)
    
    # Generate report
    report_path = os.path.join(output_dir, f"gel_report_{timestamp}.json")
    report = analyzer.generate_report(comparison_result, output_path=report_path)
    
    return {
        'analyzer': analyzer,
        'lanes': lanes,
        'bands': bands,
        'comparison': comparison_result,
        'visualization_path': viz_path,
        'report_path': report_path,
        'report': report
    }

def test_analyzer():
    """Test function to verify analyzer functionality"""
    try:
        analyzer = GelElectrophoresisAnalyzer()
        print("SUCCESS: GelElectrophoresisAnalyzer initialized successfully")
        
        # Test dependency checks
        missing_deps = []
        if cv2 is None:
            missing_deps.append("opencv-python")
        if ndimage is None or find_peaks is None:
            missing_deps.append("scipy")
        if plt is None:
            missing_deps.append("matplotlib")
        
        if missing_deps:
            print(f"WARNING: Missing dependencies: {', '.join(missing_deps)}")
            print(f"Run: pip install {' '.join(missing_deps)}")
        else:
            print("SUCCESS: All required dependencies are available")
        
        return True
    except Exception as e:
        print(f"ERROR: Error testing analyzer: {e}")
        return False

if __name__ == "__main__":
    test_analyzer()