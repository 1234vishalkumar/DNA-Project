# 📁 PREPROCESSING FILES - QUICK REFERENCE

## ✅ PREPROCESSING IS DONE IN THESE FILES:

---

## 1️⃣ **`simple_app.py`** - INPUT VALIDATION & CLEANING

**Location:** `DNA_PROJECT/simple_app.py`

**What it does:**
- Validates user input from web form
- Cleans DNA sequences (removes whitespace, converts to uppercase)
- Checks for invalid characters
- Validates sequence length

**Preprocessing Functions:**
```python
def validate_dna_sequence(sequence):
    # Preprocessing steps:
    # 1. Remove whitespace
    # 2. Convert to uppercase
    # 3. Remove special characters
    # 4. Validate characters (only ATGC allowed)
    # 5. Check minimum length
```

**When it runs:** When user submits DNA sequence through web form

---

## 2️⃣ **`utils.py`** - FEATURE EXTRACTION & ML PREPROCESSING

**Location:** `DNA_PROJECT/utils.py`

**What it does:**
- Cleans sequences for ML model
- Extracts k-mers (feature engineering)
- Scales features for ML model
- Parses different file formats (FASTA, TXT)

**Preprocessing Functions:**

### Function 1: `clean_sequence(seq)`
```python
def clean_sequence(seq):
    # Keeps only A, T, G, C characters
    # Removes everything else
    return ''.join([s for s in seq.upper() if s in "ACGT"])
```

### Function 2: `extract_features(seq)`
```python
def extract_features(seq):
    seq = clean_sequence(seq)        # Clean
    kmers = get_kmers(seq, K)        # Extract k-mers
    counts = Counter(kmers)          # Count frequencies
    vec = np.array([...])            # Create vector
    return scaler.transform(vec)     # Scale features
```

### Function 3: `parse_dna_input(file_content, filename)`
```python
def parse_dna_input(file_content, filename):
    # Parses FASTA files
    # Decodes text files
    # Cleans sequences
```

**When it runs:** Before ML prediction

---

## 3️⃣ **`gel_analysis.py`** - IMAGE PREPROCESSING

**Location:** `DNA_PROJECT/gel_analysis.py`

**What it does:**
- Loads and preprocesses gel images
- Converts to grayscale
- Applies noise reduction
- Prepares images for lane/band detection

**Preprocessing Methods:**

### Method 1: `load_image(image_path)`
```python
def load_image(self, image_path):
    self.image = cv2.imread(image_path)           # Load
    self.gray = cv2.cvtColor(self.image, ...)     # Grayscale
    self.processed_image = cv2.GaussianBlur(...)  # Blur (noise reduction)
```

### Method 2: `detect_lanes()`
```python
def detect_lanes(self):
    vertical_profile = np.mean(...)                    # Calculate profile
    vertical_profile = ndimage.gaussian_filter1d(...)  # Smooth
    inverted_profile = np.max(...) - ...               # Invert
```

### Method 3: `detect_bands_in_lane()`
```python
def detect_bands_in_lane(self, lane_id):
    lane_region = self.processed_image[...]            # Extract region
    horizontal_profile = np.mean(...)                  # Calculate profile
    horizontal_profile = ndimage.gaussian_filter1d(...) # Smooth
    inverted_profile = np.max(...) - ...               # Invert
    threshold = np.percentile(...)                     # Adaptive threshold
```

**When it runs:** When user uploads gel image

---

## 4️⃣ **`train_model.py`** - TRAINING DATA PREPROCESSING

**Location:** `DNA_PROJECT/train_model.py`

**What it does:**
- Preprocesses training data
- Cleans sequences
- Extracts features
- Splits data (train/validation/test)
- Scales features

**Preprocessing Steps:**
```python
# 1. Load data
sequences, labels = load_training_data()

# 2. Clean sequences
cleaned_sequences = [clean_sequence(seq) for seq in sequences]

# 3. Extract features
X = extract_features_from_sequences(cleaned_sequences)

# 4. Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15)

# 5. Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**When it runs:** During model training (one-time setup)

---

## 📊 SUMMARY TABLE

| File | Purpose | Preprocessing Type | When It Runs |
|------|---------|-------------------|--------------|
| **`simple_app.py`** | Input validation | User input cleaning | When user submits form |
| **`utils.py`** | Feature extraction | ML preprocessing | Before prediction |
| **`gel_analysis.py`** | Image processing | Image preprocessing | When image uploaded |
| **`train_model.py`** | Model training | Training data prep | During training |

---

## 🔄 PREPROCESSING FLOW

```
USER INPUT
    ↓
┌─────────────────────────────────┐
│  simple_app.py                  │
│  validate_dna_sequence()        │
│  • Remove whitespace            │
│  • Convert to uppercase         │
│  • Validate characters          │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  utils.py                       │
│  clean_sequence()               │
│  • Keep only ATGC               │
│  • Remove invalid chars         │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  utils.py                       │
│  extract_features()             │
│  • Extract k-mers               │
│  • Count frequencies            │
│  • Create vector                │
│  • Scale features               │
└────────────┬────────────────────┘
             ↓
        ML MODEL
```

---

## 🎯 QUICK ANSWER

**Main preprocessing files:**

1. **`simple_app.py`** - First level validation and cleaning
2. **`utils.py`** - ML feature extraction and scaling
3. **`gel_analysis.py`** - Image preprocessing

**Most important for DNA analysis:** `utils.py`
**Most important for gel analysis:** `gel_analysis.py`

---

## 📝 CODE LOCATIONS

### DNA Preprocessing:
- **File:** `utils.py`
- **Line:** ~25 (`clean_sequence`)
- **Line:** ~35 (`extract_features`)
- **Line:** ~250 (`parse_dna_input`)

### Image Preprocessing:
- **File:** `gel_analysis.py`
- **Line:** ~25 (`load_image`)
- **Line:** ~50 (`detect_lanes`)
- **Line:** ~90 (`detect_bands_in_lane`)

### Input Validation:
- **File:** `simple_app.py`
- **Line:** ~30 (`validate_dna_sequence`)

---

**ANSWER: Preprocessing is mainly done in `utils.py` (for DNA) and `gel_analysis.py` (for images)** ✅
