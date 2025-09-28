# NLP Resume Analyzer

An intelligent resume analyzer that uses advanced NLP techniques to match resumes with job descriptions while preventing keyword farming and gaming. Features a modern YAML-based configuration system for easy skills and action verb management.

## 🚀 Features

- **Advanced Semantic Analysis**: Uses sentence-transformers for context-aware matching
- **YAML Configuration System**: Externalized skills and action verbs with synonym support
- **Weighted Action Verb Scoring**: Tiered scoring system (Impact/Build/Support verbs)
- **Anti-Farming Protection**: Detects keyword stuffing and context-less skill lists
- **Readability Analysis**: Flags poorly written or machine-generated resumes
- **Multi-format Support**: Processes PDF and DOCX resume files
- **Web Interface**: Clean, user-friendly Flask application
- **Enhanced Skills Detection**: Supports synonyms and abbreviations (e.g., "js" → "JavaScript")
- **Docker Support**: Containerized deployment ready

## 📁 Project Structure

```
nlp-resume-analyzer/
├── src/
│   ├── nlp_engine/          # Core NLP processing
│   │   ├── __init__.py
│   │   ├── analyzer.py      # Resume analysis logic
│   │   ├── parser.py        # Text extraction and skills detection
│   │   └── config_loader.py # YAML configuration loader
│   └── web_app/             # Flask web application
│       ├── app.py           # Main Flask application
│       ├── static/          # CSS, JS, and assets
│       └── templates/       # HTML templates
├── config/                  # YAML configuration files
│   ├── skills.yaml          # Skills database with categories and synonyms
│   └── action_verbs.yaml    # Action verbs for weighted scoring
├── tests/                   # Unit and integration tests
├── data/                    # Sample data for testing
│   ├── job_descriptions/    # Sample job postings
│   └── sample_resumes/      # Test resume files
├── uploads/                 # Temporary file storage (gitignored)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker containerization
└── README.md               # This file
```

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/modakPrince/resume_analyzer.git
   cd nlp-resume-analyzer
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t nlp-resume-analyzer .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:8080 nlp-resume-analyzer
   ```

## 🎯 Usage

### Web Application
1. Start the application:
   ```bash
   python src/web_app/app.py
   ```
2. Open your browser to `http://localhost:5000`
3. Upload a resume (PDF format) and paste a job description
4. Get intelligent matching results with enhanced skills detection

### Configuration Management
The application uses YAML configuration files for easy maintenance:

- **`config/skills.yaml`**: Add new skills, synonyms, and categories
- **`config/action_verbs.yaml`**: Manage action verbs for weighted scoring

#### Adding New Skills
```yaml
# Example: Add a new programming language
programming_languages:
  - name: "Rust"
    synonyms: ["rustlang", "rust-lang"]
```

#### Action Verb Categories
- **Impact Verbs** (Weight 3.0): Leadership, innovation, ownership
- **Build Verbs** (Weight 2.0): Creation, implementation, engineering
- **Support Verbs** (Weight 1.0): Assistance, collaboration, maintenance

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src

# Test specific component
python -m pytest tests/test_analyzer.py
```

## 🚀 Development Roadmap

### ✅ Phase 1: Core NLP Engine (Completed)
- [x] Resume parsing (PDF/DOCX)
- [x] Information extraction (name, email, phone, skills)
- [x] YAML-based configuration system (SCH-28)
- [x] Enhanced skills detection with synonym support
- [x] Semantic similarity analysis foundation
- [x] Web application framework

### 🔄 Phase 2: Advanced Analytics (In Progress)
- [x] YAML configuration externalization (SCH-28)
- [ ] Weighted action verb scoring system (SCH-30)
- [ ] Keyword farming detection enhancement
- [ ] Readability scoring implementation
- [ ] Advanced semantic analysis

### 📋 Phase 3: Production Features (Planned)
- [ ] Job board API integration
- [ ] Advanced anti-gaming algorithms
- [ ] Performance optimization
- [ ] Cloud deployment (AWS/Azure)
- [ ] API endpoints for integration
- [ ] Batch processing capabilities

## 🏗️ Architecture

The application follows a modular architecture:

- **`config_loader.py`**: Centralized YAML configuration management
- **`parser.py`**: Text extraction and skills detection with synonym support
- **`analyzer.py`**: Advanced resume analysis and scoring
- **`app.py`**: Flask web interface and API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and add tests
4. Ensure all tests pass: `python -m pytest`
5. Submit a pull request

### Adding Skills or Verbs
Non-technical contributions are welcome! You can enhance the system by:
- Adding new skills to `config/skills.yaml`
- Adding synonyms for existing skills
- Categorizing action verbs in `config/action_verbs.yaml`

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Related Issues

- **SCH-28**: ✅ Externalize skills, verbs, synonyms to YAML (Completed)
- **SCH-30**: 🔄 Add weighted action verb tiers scoring (In Progress)

For detailed issue tracking, see the Linear project board.
