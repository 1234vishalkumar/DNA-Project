# 🧬 Enhanced DNA Forensic Analysis System

A comprehensive AI-powered DNA forensic analysis platform with advanced features for law enforcement, research, and educational purposes.

## 📚 Documentation

- **[Project Description](PROJECT_DESCRIPTION.md)** - Comprehensive overview of features and capabilities
- **[Architecture Diagrams](ARCHITECTURE.md)** - System architecture and flow diagrams
- **[Team Information](AUTHORS.md)** - Project team and contributors
- **[License](LICENSE)** - MIT License details

##  Features Overview

###  1. AI-Based Similarity Matching
- **Advanced Algorithms**: Levenshtein Distance, Cosine Similarity, and K-mer analysis
- **Percentage Matching**: Precise similarity calculations between DNA samples
- **Multi-Algorithm Comparison**: Combined scoring for enhanced accuracy
- **Use Case**: Match victim DNA with suspect samples

###  2. Mutation/SNP Detection
- **Real-time Detection**: Identify genetic variations and mutations
- **Visual Highlighting**: Color-coded mismatch display
- **Detailed Analysis**: Position-specific mutation reporting
- **Use Case**: Identify genetic variations or damaged DNA regions

###  3. Gel Electrophoresis Image Analysis
- **Image Upload**: Support for JPG, PNG, BMP, TIFF formats
- **Lane Detection**: Automatic vertical lane identification
- **Band Detection**: DNA band position and intensity analysis
- **Similarity Comparison**: Lane-to-lane matching algorithms
- **Visual Overlay**: Annotated images with detected features
- **Use Case**: Analyze gel images for DNA fragment comparison

###  4. Automated Report Generation
- **Comprehensive PDF Reports**: Professional forensic documentation
- **Detailed Analysis**: Sample info, predictions, confidence scores
- **Timestamp Tracking**: Complete audit trail
- **Export Options**: PDF download with custom formatting

###  5. Voice-Based Interaction (AI Assistant)
- **Offline TTS**: Using pyttsx3 for local text-to-speech
- **Online TTS**: gTTS integration for high-quality audio
- **Result Narration**: Automated reading of all analysis results
- **Multi-Feature Support**: Voice synthesis for DNA Analysis, Comparison, Batch Processing, Multi-Modal Analysis
- **Accessibility**: Makes forensic dashboard accessible to all users

###  6. Visualization Dashboard
- **Interactive Charts**: Plotly-powered visualizations
- **K-mer Frequency Analysis**: Bar charts of genetic patterns
- **Confidence Distribution**: Pie charts of prediction probabilities
- **Similarity Metrics**: Visual comparison displays

###  7. Database Integration (SQLite)
- **Complete Data Storage**: DNA sequences, results, timestamps
- **Investigator Tracking**: User and case management
- **Analysis History**: Searchable forensic database
- **Data Export**: CSV and JSON export capabilities

###  8. Facial Recognition Integration
- **Multi-Modal Analysis**: DNA + facial feature verification
- **OpenCV Integration**: Advanced computer vision
- **Combined Confidence**: Multi-factor authentication scoring
- **Future Enhancement**: Biometric forensics expansion

###  9. Confidence-Based Filtering
- **Intelligent Thresholds**: Automatic quality assessment
- **Re-testing Flags**: Low confidence sample identification
- **Quality Assurance**: Credibility scoring for predictions
- **Risk Assessment**: Deployment readiness evaluation

###  10. Multiple DNA Input Types
- **Format Support**: .fasta, .txt, manual entry
- **Auto-Detection**: Intelligent format recognition
- **Batch Processing**: Multiple file analysis
- **Error Handling**: Robust input validation

###  11. Batch Processing
- **Multiple File Upload**: Process multiple DNA samples simultaneously
- **Bulk Analysis**: Automated comparison across all samples
- **Consolidated Reports**: Summary reports for entire batches
- **Time Efficiency**: Parallel processing for large datasets
- **Export Options**: CSV and JSON batch results

###  12. Cloud/API Deployment Ready
- **RESTful APIs**: External system integration
- **Scalable Architecture**: Cloud deployment ready
- **Cross-Platform**: Web-based accessibility
- **Mobile Responsive**: Works on any device

##  Quick Start

### Prerequisites
- Python 3.7+
- pip package manager
- 4GB+ RAM recommended
- Modern web browser

### Installation & Setup

1. **Clone the Project**
   ```bash
   git clone https://github.com/1234vishalkumar/DNA-Project.git
   cd DNA-Project
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the System**
   ```bash
   python run_system.py
   ```

4. **Access the Application**
   - Web Interface: `http://localhost:5000`
   - Dashboard: `http://localhost:5000/dashboard`
   - History: `http://localhost:5000/history`
   
   **Note:** These are local URLs that work only when running the application on your machine.

##  Usage Guide

### 🔬 DNA Analysis
1. Navigate to the "DNA Analysis" tab
2. Enter investigator and sample information
3. Choose input method (text or file upload)
4. Paste DNA sequence or upload file
5. Click "Analyze DNA Sample"
6. Review results with confidence assessment
7. Use voice synthesis to hear results
8. Generate PDF report

###  DNA Comparison
1. Go to "Comparison" tab
2. Enter two DNA sequences (text or files)
3. Click "Compare DNA Sequences"
4. Review similarity metrics and mutations
5. Analyze visual similarity charts

###  Gel Electrophoresis Analysis
1. Go to "Gel Analysis" tab
2. Upload gel electrophoresis image
3. Click "Upload and Analyze"
4. Review detected lanes and bands
5. Analyze lane similarity scores
6. Download annotated images

###  Batch Processing
1. Select "Batch Processing" tab
2. Upload multiple DNA files
3. Click "Process All Files"
4. Review batch analysis results
5. Export results for further analysis

###  Multi-Modal Analysis
1. Access "Multi-Modal" tab
2. Enter DNA sequence
3. Optionally upload face image
4. Run combined analysis
5. Review multi-factor verification results

###  Dashboard Analytics
1. Visit "Dashboard" tab
2. View analysis statistics
3. Monitor confidence rates
4. Review recent analysis history
5. Track system performance

##  API Documentation

### DNA Prediction API
```bash
POST /api/predict
Content-Type: application/json

{
  "sequence": "ATCGATCGATCG..."
}
```

### DNA Comparison API
```bash
POST /api/compare
Content-Type: application/json

{
  "sequence1": "ATCGATCGATCG...",
  "sequence2": "ATCGATCGATCC..."
}
```

### Analysis History API
```bash
GET /api/history
```

##  Project Structure

```
DNA_MATCHING_PROJECT/
├── app/
│   ├── static/
│   │   └── style.css          # Enhanced UI styling
│   ├── templates/
│   │   ├── index.html         # Main interface
│   │   ├── dashboard.html     # Analytics dashboard
│   │   └── history.html       # Analysis history
│   └── app.py                 # Flask application
├── model/
│   ├── best_model.pkl         # Trained ML model
│   ├── scaler.pkl            # Feature scaler
│   ├── kmer_vocab.json       # K-mer vocabulary
│   └── label_info.json       # Class labels
├── dataset/
│   └── human.txt             # Training data
├── reference_data/
│   ├── person1.fasta         # Reference samples
│   ├── person2.fasta
│   └── person3.fasta
├── uploads/                  # File upload directory
├── reports/                  # Generated PDF reports
├── audio/                    # Voice synthesis files
├── utils.py                  # Core functionality
├── train_model.py           # Model training
├── test_enhanced_features.py # System tests
├── run_system.py            # System launcher
├── requirements.txt         # Dependencies
├── dna_forensics.db        # SQLite database
├── ARCHITECTURE.md          # System architecture diagrams
├── PROJECT_DESCRIPTION.md   # Comprehensive feature documentation
├── AUTHORS.md               # Team information
├── LICENSE                  # MIT License
└── README.md               # This file
```

##  Testing

Run comprehensive system tests:
```bash
python test_enhanced_features.py
```

Test individual components:
```bash
python -c "from utils import *; test_function()"
```

##  Security Features

- **Input Validation**: Robust DNA sequence validation
- **SQL Injection Protection**: Parameterized queries
- **File Upload Security**: Type and size restrictions
- **Error Handling**: Graceful failure management
- **Data Privacy**: Local processing and storage

##  Performance Optimization

- **Efficient Algorithms**: Optimized similarity calculations
- **Caching**: Model and scaler caching
- **Batch Processing**: Multiple file handling
- **Memory Management**: Efficient data structures
- **Database Indexing**: Fast query performance

##  Deployment Options

### Local Development
```bash
python run_system.py
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker (create Dockerfile)
docker build -t dna-forensics .
docker run -p 5000:5000 dna-forensics
```

### Cloud Platforms
- **Heroku**: Ready for deployment
- **Railway**: One-click deployment
- **Render**: Free tier available
- **AWS/GCP/Azure**: Enterprise deployment

##  Contributing

### For Team Members
Team members should work on their local cloned copies only. Changes to the main repository require approval.

1. Clone the repository (see Installation & Setup)
2. Make changes in your local copy
3. Test thoroughly before requesting merge
4. Contact the repository owner for integrating changes

### For External Contributors
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Authors

See [AUTHORS.md](AUTHORS.md) for complete team information.

**Lead Developers:**
- **Venika** - Full Stack Developer & System Architect
- **Vishal Kumar** - Full Stack Developer & AI/ML Engineer (vk3785940@gmail.com)

**Contributors:**
- **Sandhya** - Frontend Developer & UI/UX Designer
- **Ria** - Data Scientist & ML Engineer  
##  Acknowledgments

- **BioPython**: DNA sequence processing
- **Scikit-learn**: Machine learning algorithms
- **Flask**: Web framework
- **Plotly**: Interactive visualizations
- **OpenCV**: Computer vision capabilities

##  Future Enhancements

- [ ] Real-time DNA sequencing integration
- [ ] Advanced phylogenetic analysis
- [ ] Blockchain-based evidence tracking
- [ ] Mobile app development
- [ ] Cloud-based distributed processing
- [ ] Integration with forensic databases
- [ ] Advanced statistical analysis
- [ ] Multi-language support
- [ ] Enhanced gel image processing with AI
- [ ] 3D visualization of DNA structures
- [ ] Integration with CODIS database
- [ ] Advanced mutation prediction models

## 📞 Support

For support, email:vk3785940@gmail.com or create an issue in the repository.


**Made with ❤️ for the forensic science community**

*Empowering justice through advanced DNA analysis technology*
