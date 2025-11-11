# 🧪 Testing Instructions for DNA Forensic Analysis System

## 🚀 **How to Run & Test**

### 1. Start the System
```bash
python run_final.py
```

### 2. Open Web Browser
- Go to: `http://localhost:5000`
- You'll see the main interface with tabs

## 📋 **Test Scenarios**

### 🧪 **Gel Analysis Testing** (Main Feature)

#### Test 1: Basic Gel Upload
1. Click **"Gel Analysis"** tab
2. Click "Select gel electrophoresis image"
3. Upload any image file (JPG/PNG)
4. Set "Number of lanes" to 4-8
5. Click **"Analyze Gel Image"**
6. **Expected Result**: Lane detection and band analysis

#### Test 2: Lane Comparison
1. After gel analysis completes
2. Select two different lanes from dropdowns
3. Set tolerance to 10-15 pixels
4. Click **"Compare Selected Lanes"**
5. **Expected Result**: Similarity percentage and visual comparison

### 🧬 **DNA Sequence Testing**

#### Test 3: DNA Analysis
1. Click **"DNA Analysis"** tab
2. Enter investigator name: "Test User"
3. Enter sample name: "Sample 001"
4. Paste DNA sequence: `ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG`
5. Click **"Analyze DNA Sample"**
6. **Expected Result**: Analysis results (may show errors if models missing)

#### Test 4: File Upload
1. Stay in **"DNA Analysis"** tab
2. Select "Upload DNA File" radio button
3. Upload file: `test_samples/dna_sample_1.txt`
4. Click **"Analyze DNA Sample"**
5. **Expected Result**: File processed and analyzed

#### Test 5: DNA Comparison
1. Click **"Comparison"** tab
2. Enter two DNA sequences:
   - Sample 1: `ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG`
   - Sample 2: `ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCC`
3. Click **"Compare DNA Sequences"**
4. **Expected Result**: Similarity analysis with mutation detection

### 📊 **Batch Processing**

#### Test 6: Multiple Files
1. Click **"Batch Processing"** tab
2. Select multiple files from `test_samples/` folder
3. Click **"Process All Files"**
4. **Expected Result**: Batch analysis results table

## 📁 **Test Files Available**

```
test_samples/
├── dna_sample_1.txt     # Random DNA sequence
├── dna_sample_2.txt     # Another DNA sequence  
└── sample.fasta         # FASTA format file
```

## ✅ **Expected Behaviors**

### ✅ **Working Features:**
- File upload and validation
- Basic gel analysis framework
- DNA sequence input processing
- Web interface navigation
- Error handling and messages

### ⚠️ **Limited Features (due to missing dependencies):**
- Advanced gel image processing (needs OpenCV)
- ML-based DNA predictions (needs trained models)
- Complex visualizations (needs full matplotlib)

## 🔧 **Troubleshooting**

### Common Issues:
1. **"Gel analysis not available"** → OpenCV not installed
2. **"Analysis failed"** → Missing ML models or dependencies
3. **"Invalid file format"** → Use supported formats (JPG, PNG, TXT, FASTA)

### Solutions:
- Install missing packages: `pip install opencv-python scipy matplotlib`
- Use text-based DNA samples for testing
- Check file formats and sizes

## 🎯 **Success Criteria**

✅ **System is working if:**
- Web interface loads at localhost:5000
- File uploads are accepted
- Basic analysis runs without crashes
- Error messages are clear and helpful
- Navigation between tabs works

## 📞 **Testing Checklist**

- [ ] System starts without errors
- [ ] Web interface accessible
- [ ] Gel analysis tab loads
- [ ] File upload works
- [ ] DNA analysis processes input
- [ ] Comparison feature functions
- [ ] Error handling works
- [ ] All tabs navigate properly

**The system is ready for testing!** 🚀