# 🧬 DNA FORENSIC ANALYSIS SYSTEM - PROJECT FLOW

## 📊 COMPLETE PROJECT FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER OPENS WEB BROWSER                        │
│                  http://localhost:5000                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              FLASK SERVER STARTS (run_final.py)                  │
│  • Loads simple_app.py                                          │
│  • Initializes Flask application                                │
│  • Sets up routes (/analyze, /gel_upload, etc.)                │
│  • Loads ML models from model/ folder                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 WEB PAGE LOADS (index.html)                      │
│  • Shows navigation tabs                                        │
│  • DNA Analysis | Comparison | Gel Analysis | Dashboard        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌──────────────────┐              ┌──────────────────┐
│  DNA ANALYSIS    │              │  GEL ANALYSIS    │
│     FLOW         │              │      FLOW        │
└──────────────────┘              └──────────────────┘
```

---

## 🔬 FLOW 1: DNA SEQUENCE ANALYSIS

### Step-by-Step Process

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│ 1. USER ENTERS DATA                     │
│    • Investigator name: "Dr. Smith"     │
│    • Sample name: "Sample A"            │
│    • DNA sequence: "ATGCATGC..."        │
│    OR uploads .txt/.fasta file          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 2. USER CLICKS "Analyze DNA Sample"     │
│    • JavaScript captures form data      │
│    • Creates FormData object            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 3. FRONTEND VALIDATION (JavaScript)     │
│    • Check if fields are filled         │
│    • Show loading message               │
│    • Send AJAX POST to /analyze         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 4. FLASK RECEIVES REQUEST               │
│    Route: @app.route('/analyze')        │
│    • Extracts form data                 │
│    • Gets DNA sequence                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 5. BACKEND VALIDATION (Python)          │
│    validate_dna_sequence()              │
│    ✓ Check if empty                     │
│    ✓ Check for numbers                  │
│    ✓ Check for invalid characters       │
│    ✓ Check minimum length (10 bp)       │
│    ✓ Check base diversity               │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    ❌ ERROR          ✅ VALID
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 6. CLEAN SEQUENCE                       │
        │    │    • Remove whitespace                  │
        │    │    • Convert to uppercase               │
        │    │    • Remove special characters          │
        │    │    Input:  "atgc atgc"                  │
        │    │    Output: "ATGCATGC"                   │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 7. EXTRACT K-MERS (Feature Engineering) │
        │    │    K = 3 (triplets)                     │
        │    │    Sequence: "ATGCATGC"                 │
        │    │    K-mers:                              │
        │    │    • ATG (position 0-2)                 │
        │    │    • TGC (position 1-3)                 │
        │    │    • GCA (position 2-4)                 │
        │    │    • CAT (position 3-5)                 │
        │    │    • ATG (position 4-6)                 │
        │    │    • TGC (position 5-7)                 │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 8. COUNT K-MER FREQUENCIES              │
        │    │    Counter({'ATG': 2, 'TGC': 2,         │
        │    │             'GCA': 1, 'CAT': 1})        │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 9. CREATE FEATURE VECTOR                │
        │    │    Vocabulary: All possible k-mers      │
        │    │    (4^3 = 64 possible triplets)         │
        │    │    Vector: [2, 1, 2, 1, 0, 0, ...]      │
        │    │    Length: 64 features                  │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 10. SCALE FEATURES                      │
        │    │     scaler.transform(features)          │
        │    │     Normalizes values for ML model      │
        │    │     Before: [2, 1, 2, 1, ...]           │
        │    │     After:  [0.5, 0.2, 0.5, 0.2, ...]   │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 11. ML MODEL PREDICTION                 │
        │    │     model.predict(scaled_features)      │
        │    │     • Loads best_model.pkl              │
        │    │     • Random Forest/XGBoost classifier  │
        │    │     • Predicts DNA category             │
        │    │     Result: "Human DNA"                 │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 12. CALCULATE CONFIDENCE                │
        │    │     model.predict_proba(features)       │
        │    │     Returns probability for each class  │
        │    │     [0.05, 0.87, 0.08]                  │
        │    │     Max = 0.87 = 87% confidence         │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 13. CALCULATE DNA CHARACTERISTICS       │
        │    │     • Length: count(sequence)           │
        │    │     • GC Content: (G+C)/total × 100     │
        │    │     • Base Composition:                 │
        │    │       A: 25%, T: 25%, G: 25%, C: 25%    │
        │    │     • Quality: "Good"                   │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 14. SAVE TO DATABASE                    │
        │    │     SQLite: dna_forensics.db            │
        │    │     INSERT INTO dna_analysis            │
        │    │     (timestamp, investigator, sample,   │
        │    │      prediction, confidence)            │
        │    └────────────┬────────────────────────────┘
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────────┐
        │    │ 15. CREATE JSON RESPONSE                │
        │    │     {                                   │
        │    │       "success": true,                  │
        │    │       "prediction": "Human DNA",        │
        │    │       "confidence": 0.87,               │
        │    │       "dna_characteristics": {...}      │
        │    │     }                                   │
        │    └────────────┬────────────────────────────┘
        │                 │
        └─────────────────┼─────────────────────────────┐
                          │                             │
                          ▼                             ▼
        ┌─────────────────────────────┐   ┌─────────────────────────────┐
        │ 16. SEND RESPONSE TO BROWSER│   │ 16. SEND ERROR TO BROWSER   │
        │     Status: 200 OK          │   │     Status: 400 Bad Request │
        │     Content-Type: JSON      │   │     Error message in JSON   │
        └────────────┬────────────────┘   └─────────────┬───────────────┘
                     │                                   │
                     ▼                                   ▼
        ┌─────────────────────────────┐   ┌─────────────────────────────┐
        │ 17. JAVASCRIPT RECEIVES     │   │ 17. JAVASCRIPT SHOWS ERROR  │
        │     • Parse JSON response   │   │     • Display red error box │
        │     • Extract data          │   │     • Show error message    │
        └────────────┬────────────────┘   │     • Shake animation       │
                     │                     └─────────────────────────────┘
                     ▼
        ┌─────────────────────────────────────────┐
        │ 18. DISPLAY RESULTS ON PAGE             │
        │     • Prediction: "Human DNA"           │
        │     • Confidence: 87% (green indicator) │
        │     • DNA Characteristics table         │
        │     • GC Content: 52.3%                 │
        │     • Base Composition chart            │
        │     • Enable voice synthesis button     │
        │     • Show "Generate Report" button     │
        └─────────────────────────────────────────┘
                     │
                     ▼
                   END
```

---

## 🧪 FLOW 2: GEL ELECTROPHORESIS ANALYSIS

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│ 1. USER UPLOADS GEL IMAGE               │
│    • Clicks "Choose File"               │
│    • Selects gel_image.png              │
│    • (Optional) Enters number of lanes  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 2. USER CLICKS "Analyze Gel Image"      │
│    • JavaScript captures form           │
│    • Creates FormData with image        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 3. SEND TO FLASK                        │
│    POST /gel_upload                     │
│    • Multipart form data                │
│    • Image file in request              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 4. FLASK RECEIVES IMAGE                 │
│    • Validate file format               │
│    • Check file size (max 16MB)         │
│    • Save to uploads/ folder            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 5. LOAD IMAGE WITH OPENCV               │
│    cv2.imread(image_path)               │
│    • Read image as numpy array          │
│    • Convert BGR to RGB                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 6. PREPROCESS IMAGE                     │
│    • Convert to grayscale               │
│    • Apply Gaussian blur (reduce noise) │
│    • Enhance contrast                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 7. DETECT LANES (Vertical)              │
│    • Calculate vertical intensity       │
│      profile (average each column)      │
│    • Smooth with Gaussian filter        │
│    • Find valleys (dark regions)        │
│    • Valleys = lane boundaries          │
│                                         │
│    Image:  ║ ║ ║ ║ ║ ║                 │
│           Lane1 Lane2 Lane3...          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 8. FOR EACH LANE: DETECT BANDS          │
│    • Extract lane region                │
│    • Calculate horizontal intensity     │
│      profile (average each row)         │
│    • Find peaks (dark bands)            │
│    • Use scipy.signal.find_peaks()      │
│                                         │
│    Lane:  ═══ ← Band 1                  │
│           ───                           │
│           ═══ ← Band 2                  │
│           ───                           │
│           ═══ ← Band 3                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 9. MEASURE BANDS                        │
│    For each band:                       │
│    • Position (pixels from top)         │
│    • Intensity (brightness)             │
│    • Width (thickness)                  │
│    • Lane ID                            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 10. CREATE RESPONSE                     │
│     {                                   │
│       "lanes_detected": 6,              │
│       "total_bands": 24,                │
│       "lanes": [...],                   │
│       "bands": {...}                    │
│     }                                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 11. DISPLAY RESULTS                     │
│     • Show lane count                   │
│     • Show band count                   │
│     • Display table with details        │
│     • Enable lane comparison            │
└─────────────────────────────────────────┘
                 │
                 ▼
               END
```

---

## ⚖️ FLOW 3: DNA COMPARISON

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│ 1. USER ENTERS TWO DNA SEQUENCES        │
│    Sequence 1: "ATGCATGC..."            │
│    Sequence 2: "ATGCATCC..."            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 2. CLEAN BOTH SEQUENCES                 │
│    • Remove whitespace                  │
│    • Convert to uppercase               │
│    • Validate characters                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 3. EXTRACT FEATURES FROM BOTH           │
│    Seq1 → K-mers → Vector1              │
│    Seq2 → K-mers → Vector2              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 4. CALCULATE COSINE SIMILARITY          │
│    similarity = (V1 · V2) / (|V1||V2|)  │
│    Result: 0.95 (95%)                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 5. CALCULATE SEQUENCE SIMILARITY        │
│    SequenceMatcher(seq1, seq2).ratio()  │
│    Result: 0.92 (92%)                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 6. CALCULATE LEVENSHTEIN DISTANCE       │
│    Count edits needed to transform      │
│    seq1 → seq2                          │
│    Distance: 5 edits                    │
│    Similarity: 1 - (5/length) = 0.90    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 7. DETECT MUTATIONS                     │
│    Compare base by base:                │
│    Position 5: G → C (mutation)         │
│    Position 12: A → T (mutation)        │
│    Total: 2 mutations                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 8. COMBINE SCORES                       │
│    Average = (95 + 92 + 90) / 3         │
│    Combined Similarity: 92.3%           │
│    Match Quality: "EXCELLENT"           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 9. DISPLAY RESULTS                      │
│    • Similarity meter (92.3%)           │
│    • Match quality badge                │
│    • Mutation list                      │
│    • Similarity chart                   │
└─────────────────────────────────────────┘
                 │
                 ▼
               END
```

---

## 🗄️ DATABASE FLOW

```
┌─────────────────────────────────────────┐
│ EVERY ANALYSIS SAVES TO DATABASE        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ SQLite Database: dna_forensics.db       │
│                                         │
│ Table: dna_analysis                     │
│ ┌─────────────────────────────────┐    │
│ │ id (auto increment)             │    │
│ │ timestamp                       │    │
│ │ investigator_name               │    │
│ │ sample_name                     │    │
│ │ dna_sequence                    │    │
│ │ prediction                      │    │
│ │ confidence                      │    │
│ │ similarity_results (JSON)       │    │
│ │ mutations (JSON)                │    │
│ └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ DASHBOARD RETRIEVES HISTORY             │
│ • SELECT * FROM dna_analysis            │
│ • ORDER BY timestamp DESC               │
│ • LIMIT 50                              │
│ • Display in table                      │
└─────────────────────────────────────────┘
```

---

## 🎯 KEY COMPONENTS INTERACTION

```
┌──────────────┐
│   BROWSER    │ ← User Interface
└──────┬───────┘
       │ HTTP Request (AJAX)
       ▼
┌──────────────┐
│    FLASK     │ ← Web Server (Routes)
└──────┬───────┘
       │ Function Call
       ▼
┌──────────────┐
│  VALIDATION  │ ← Input Checking
└──────┬───────┘
       │ Clean Data
       ▼
┌──────────────┐
│  K-MER       │ ← Feature Engineering
│  EXTRACTION  │
└──────┬───────┘
       │ Feature Vector
       ▼
┌──────────────┐
│  ML MODEL    │ ← Prediction
└──────┬───────┘
       │ Results
       ▼
┌──────────────┐
│  DATABASE    │ ← Storage
└──────┬───────┘
       │ Response
       ▼
┌──────────────┐
│   BROWSER    │ ← Display Results
└──────────────┘
```

---

## 📝 SUMMARY

### The project works in 3 main phases:

**PHASE 1: INPUT & VALIDATION**
- User enters data
- Frontend validates
- Backend validates
- Errors shown immediately

**PHASE 2: PROCESSING & ANALYSIS**
- Clean data
- Extract features (k-mers)
- ML prediction
- Calculate metrics
- Save to database

**PHASE 3: OUTPUT & DISPLAY**
- Create JSON response
- Send to browser
- JavaScript displays results
- User can generate reports

### Key Technologies Working Together:
- **Flask**: Handles web requests
- **JavaScript**: User interaction
- **Python**: Data processing
- **ML Models**: Predictions
- **OpenCV**: Image analysis
- **SQLite**: Data storage

**Everything flows smoothly from user input → processing → results!** 🚀
