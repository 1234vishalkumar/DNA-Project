# 🔍 PREPROCESSING LOCATIONS IN DNA FORENSIC ANALYSIS SYSTEM

## 📍 WHERE PREPROCESSING HAPPENS

Preprocessing occurs at **3 MAIN LOCATIONS** in your project:

---

## 1️⃣ DNA SEQUENCE PREPROCESSING

### Location 1: `simple_app.py` (Backend Validation)

**File:** `DNA_PROJECT/simple_app.py`
**Function:** `validate_dna_sequence()`
**Line:** ~30-70

```python
def validate_dna_sequence(sequence):
    """Validate DNA sequence - must contain only A, T, G, C, N characters"""
    
    # ============ PREPROCESSING STEP 1: Type Check ============
    if not sequence or not isinstance(sequence, str):
        return False, "❌ ERROR: DNA sequence is empty or invalid type"
    
    # ============ PREPROCESSING STEP 2: Clean Sequence ============
    # Remove whitespace and convert to uppercase
    sequence = sequence.strip().upper()
    sequence = sequence.replace(' ', '')
    sequence = sequence.replace('\n', '')
    sequence = sequence.replace('\r', '')
    sequence = sequence.replace('>', '')  # Remove FASTA header marker
    
    # ============ PREPROCESSING STEP 3: Empty Check ============
    if not sequence:
        return False, "❌ ERROR: DNA sequence is empty after removing whitespace"
    
    # ============ PREPROCESSING STEP 4: Length Validation ============
    if len(sequence) < 10:
        return False, f"❌ ERROR: DNA sequence is too short ({len(sequence)} bp)"
    
    # ============ PREPROCESSING STEP 5: Number Detection ============
    if any(char.isdigit() for char in sequence):
        return False, "❌ ERROR: Numbers detected in sequence"
    
    # ============ PREPROCESSING STEP 6: Character Validation ============
    valid_chars = set('ATGCN')
    sequence_chars = set(sequence)
    invalid_chars = sequence_chars - valid_chars
    
    if invalid_chars:
        invalid_list = ', '.join(f"'{char}'" for char in sorted(invalid_chars))
        return False, f"❌ ERROR: Invalid DNA characters detected: {invalid_list}"
    
    # ============ PREPROCESSING STEP 7: Base Diversity Check ============
    unique_bases = len(set(sequence.replace('N', '')))
    if unique_bases < 2:
        return False, "❌ ERROR: Invalid DNA sequence - only one type of nucleotide"
    
    # ✅ Return cleaned sequence
    return True, sequence
```

**What happens here:**
1. ✅ Type checking
2. ✅ Whitespace removal
3. ✅ Case normalization (uppercase)
4. ✅ FASTA header removal
5. ✅ Length validation
6. ✅ Character validation
7. ✅ Quality checks

---

### Location 2: `utils.py` (Feature Extraction)

**File:** `DNA_PROJECT/utils.py`
**Function:** `clean_sequence()`
**Line:** ~25

```python
def clean_sequence(seq):
    """
    ============ PREPROCESSING FOR ML MODEL ============
    Clean DNA sequence by keeping only valid nucleotides
    """
    # Remove all characters except A, T, G, C
    # Convert to uppercase
    return ''.join([s for s in seq.upper() if s in "ACGT"])
```

**What happens here:**
1. ✅ Convert to uppercase
2. ✅ Filter only ATGC characters
3. ✅ Remove N (unknown bases)
4. ✅ Remove any remaining invalid characters

**When it's called:**
```python
# In extract_features() function (Line ~35)
def extract_features(seq):
    seq = clean_sequence(seq)  # ← PREPROCESSING HAPPENS HERE
    kmers = get_kmers(seq, K)
    counts = Counter(kmers)
    vec = np.array([counts.get(k, 0) for k in VOCAB]).reshape(1, -1)
    return scaler.transform(vec)
```

---

### Location 3: `utils.py` (File Parsing)

**File:** `DNA_PROJECT/utils.py`
**Function:** `parse_dna_input()`
**Line:** ~250

```python
def parse_dna_input(file_content, filename):
    """
    ============ PREPROCESSING FOR FILE UPLOADS ============
    Parse DNA input from various formats
    """
    try:
        # PREPROCESSING: Detect and parse FASTA format
        if filename.endswith('.fasta') or filename.endswith('.fa'):
            sequences = []
            for record in SeqIO.parse(BytesIO(file_content), "fasta"):
                sequences.append(str(record.seq))
            return sequences[0] if sequences else None
        
        # PREPROCESSING: Parse plain text
        elif filename.endswith('.txt'):
            content = file_content.decode('utf-8').strip()
            return clean_sequence(content)  # ← Additional cleaning
        
        # PREPROCESSING: Try to parse as plain sequence
        else:
            content = file_content.decode('utf-8').strip()
            return clean_sequence(content)
    
    except Exception as e:
        return None
```

**What happens here:**
1. ✅ File format detection
2. ✅ FASTA parsing (removes headers, metadata)
3. ✅ Text decoding (UTF-8)
4. ✅ Whitespace stripping
5. ✅ Sequence cleaning

---

## 2️⃣ GEL IMAGE PREPROCESSING

### Location 4: `gel_analysis.py` (Image Loading)

**File:** `DNA_PROJECT/gel_analysis.py`
**Class:** `GelElectrophoresisAnalyzer`
**Method:** `load_image()`
**Line:** ~25-45

```python
def load_image(self, image_path):
    """
    ============ IMAGE PREPROCESSING ============
    Load and preprocess gel electrophoresis image
    """
    if cv2 is None:
        raise ImportError("OpenCV not installed")
    
    # PREPROCESSING STEP 1: Load image
    self.image = cv2.imread(image_path)
    if self.image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # PREPROCESSING STEP 2: Validate dimensions
    if self.image.shape[0] < 100 or self.image.shape[1] < 100:
        raise ValueError("Image too small for analysis")
    
    # PREPROCESSING STEP 3: Convert to grayscale
    self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
    
    # PREPROCESSING STEP 4: Apply Gaussian blur (noise reduction)
    self.processed_image = cv2.GaussianBlur(self.gray, (5, 5), 0)
    
    return True
```

**What happens here:**
1. ✅ Image loading from file
2. ✅ Dimension validation
3. ✅ Color space conversion (BGR → Grayscale)
4. ✅ Noise reduction (Gaussian blur)

---

### Location 5: `gel_analysis.py` (Lane Detection Preprocessing)

**File:** `DNA_PROJECT/gel_analysis.py`
**Method:** `detect_lanes()`
**Line:** ~50-80

```python
def detect_lanes(self, num_lanes=None, manual_lanes=None):
    """
    ============ LANE DETECTION PREPROCESSING ============
    """
    # ... code ...
    
    # PREPROCESSING STEP 1: Calculate vertical intensity profile
    vertical_profile = np.mean(self.processed_image, axis=0)
    
    # PREPROCESSING STEP 2: Smooth the profile (reduce noise)
    vertical_profile = ndimage.gaussian_filter1d(vertical_profile, sigma=2)
    
    # PREPROCESSING STEP 3: Invert profile (valleys become peaks)
    inverted_profile = np.max(vertical_profile) - vertical_profile
    
    # Now ready for peak detection...
```

**What happens here:**
1. ✅ Intensity profile calculation
2. ✅ Gaussian smoothing (sigma=2)
3. ✅ Profile inversion

---

### Location 6: `gel_analysis.py` (Band Detection Preprocessing)

**File:** `DNA_PROJECT/gel_analysis.py`
**Method:** `detect_bands_in_lane()`
**Line:** ~90-120

```python
def detect_bands_in_lane(self, lane_id):
    """
    ============ BAND DETECTION PREPROCESSING ============
    """
    # ... code ...
    
    # PREPROCESSING STEP 1: Extract lane region
    lane_region = self.processed_image[lane['y1']:lane['y2'], 
                                       lane['x1']:lane['x2']]
    
    # PREPROCESSING STEP 2: Calculate horizontal intensity profile
    horizontal_profile = np.mean(lane_region, axis=1)
    
    # PREPROCESSING STEP 3: Smooth the profile
    horizontal_profile = ndimage.gaussian_filter1d(horizontal_profile, sigma=1)
    
    # PREPROCESSING STEP 4: Invert profile
    inverted_profile = np.max(horizontal_profile) - horizontal_profile
    
    # PREPROCESSING STEP 5: Calculate adaptive threshold
    threshold = np.percentile(inverted_profile, 75)
    
    # Now ready for peak detection...
```

**What happens here:**
1. ✅ Region extraction
2. ✅ Intensity profile calculation
3. ✅ Gaussian smoothing (sigma=1)
4. ✅ Profile inversion
5. ✅ Adaptive threshold calculation

---

## 3️⃣ MACHINE LEARNING PREPROCESSING

### Location 7: `utils.py` (Feature Scaling)

**File:** `DNA_PROJECT/utils.py`
**Function:** `extract_features()`
**Line:** ~35-45

```python
def extract_features(seq):
    """
    ============ ML PREPROCESSING PIPELINE ============
    """
    # PREPROCESSING STEP 1: Clean sequence
    seq = clean_sequence(seq)
    
    # PREPROCESSING STEP 2: Extract k-mers
    kmers = get_kmers(seq, K)
    
    # PREPROCESSING STEP 3: Count k-mer frequencies
    counts = Counter(kmers)
    
    # PREPROCESSING STEP 4: Create feature vector
    vec = np.array([counts.get(k, 0) for k in VOCAB]).reshape(1, -1)
    
    # PREPROCESSING STEP 5: Scale features (normalization)
    return scaler.transform(vec)  # ← StandardScaler preprocessing
```

**What happens here:**
1. ✅ Sequence cleaning
2. ✅ K-mer extraction
3. ✅ Frequency counting
4. ✅ Vector creation
5. ✅ Feature scaling (StandardScaler)

---

## 📊 PREPROCESSING FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                                │
│  "atgc atgc 123 xyz"  OR  gel_image.png                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PREPROCESSING LAYER 1                           │
│              (simple_app.py)                                 │
│  • Type checking                                            │
│  • Whitespace removal                                       │
│  • Case normalization                                       │
│  • Basic validation                                         │
│  Output: "ATGCATGC" (cleaned)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PREPROCESSING LAYER 2                           │
│              (utils.py - clean_sequence)                     │
│  • Remove invalid characters                                │
│  • Keep only ATGC                                           │
│  • Final cleaning                                           │
│  Output: "ATGCATGC" (pure)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PREPROCESSING LAYER 3                           │
│              (utils.py - extract_features)                   │
│  • K-mer extraction                                         │
│  • Frequency counting                                       │
│  • Vector creation                                          │
│  • Feature scaling                                          │
│  Output: [0.5, 0.2, 0.5, ...] (scaled vector)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ML MODEL                                        │
│              (Prediction)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🖼️ IMAGE PREPROCESSING FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    GEL IMAGE                                 │
│              gel_electrophoresis.png                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         IMAGE PREPROCESSING LAYER 1                          │
│         (gel_analysis.py - load_image)                       │
│  • Load with OpenCV                                         │
│  • Validate dimensions                                      │
│  • BGR → Grayscale conversion                               │
│  • Gaussian blur (5x5, sigma=0)                             │
│  Output: Preprocessed grayscale image                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         LANE DETECTION PREPROCESSING                         │
│         (gel_analysis.py - detect_lanes)                     │
│  • Vertical intensity profile                               │
│  • Gaussian smoothing (sigma=2)                             │
│  • Profile inversion                                        │
│  Output: Preprocessed profile for peak detection            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         BAND DETECTION PREPROCESSING                         │
│         (gel_analysis.py - detect_bands_in_lane)            │
│  • Lane region extraction                                   │
│  • Horizontal intensity profile                             │
│  • Gaussian smoothing (sigma=1)                             │
│  • Profile inversion                                        │
│  • Adaptive threshold calculation                           │
│  Output: Preprocessed profile for band detection            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PEAK DETECTION                                  │
│              (scipy.signal.find_peaks)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 SUMMARY TABLE

| Preprocessing Type | File Location | Function/Method | What It Does |
|-------------------|---------------|-----------------|--------------|
| **Input Validation** | `simple_app.py` | `validate_dna_sequence()` | Type check, whitespace removal, case normalization |
| **Sequence Cleaning** | `utils.py` | `clean_sequence()` | Remove invalid chars, keep only ATGC |
| **File Parsing** | `utils.py` | `parse_dna_input()` | Parse FASTA, decode text, clean |
| **Feature Extraction** | `utils.py` | `extract_features()` | K-mer extraction, counting, scaling |
| **Image Loading** | `gel_analysis.py` | `load_image()` | Load, validate, grayscale, blur |
| **Lane Preprocessing** | `gel_analysis.py` | `detect_lanes()` | Intensity profile, smoothing, inversion |
| **Band Preprocessing** | `gel_analysis.py` | `detect_bands_in_lane()` | Region extraction, profile, threshold |

---

## 🎯 KEY TAKEAWAYS

### DNA Preprocessing happens in 3 stages:
1. **Validation** (`simple_app.py`) - User input cleaning
2. **Cleaning** (`utils.py`) - ML-ready cleaning
3. **Feature Engineering** (`utils.py`) - K-mer extraction + scaling

### Image Preprocessing happens in 3 stages:
1. **Loading** (`gel_analysis.py`) - Image loading + grayscale
2. **Lane Detection** (`gel_analysis.py`) - Intensity profile preprocessing
3. **Band Detection** (`gel_analysis.py`) - Region-specific preprocessing

### Why Multiple Preprocessing Layers?
- **Layer 1**: User-facing validation (catch errors early)
- **Layer 2**: Data cleaning (prepare for ML)
- **Layer 3**: Feature engineering (convert to ML format)

**Each layer has a specific purpose and happens at a specific location in the code!** 🔍✨
