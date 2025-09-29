# NLP Resume Analyzer - Data Flow Diagram

## Overview
This document describes the data flow architecture of the NLP Resume Analyzer system, showing how data moves through different components from input to final analysis results.

## System Architecture Data Flow

```mermaid
graph TB
    %% Input Layer
    subgraph "Input Layer"
        USER[👤 User]
        RESUME[📄 Resume PDF]
        JOB_DESC[📝 Job Description]
    end

    %% Web Interface Layer
    subgraph "Web Interface Layer"
        WEB_UI[🌐 Web Interface<br/>templates/index.html]
        FLASK_APP[🔧 Flask App<br/>web_app/app.py]
        UPLOAD[📁 File Upload<br/>uploads/]
    end

    %% Configuration Layer
    subgraph "Configuration Layer"
        CONFIG_LOADER[⚙️ Config Loader<br/>config_loader.py]
        SKILLS_YAML[📋 Skills Config<br/>config/skills.yaml]
        VERBS_YAML[📊 Action Verbs<br/>config/action_verbs.yaml]
    end

    %% NLP Engine Core
    subgraph "NLP Engine Core"
        PARSER[🔍 Parser<br/>parser.py]
        ANALYZER[🧠 Analyzer<br/>analyzer.py]
        
        subgraph "NLP Models"
            SPACY[🔤 spaCy NLP<br/>en_core_web_sm]
            SENTENCE_BERT[🎯 Sentence BERT<br/>all-MiniLM-L6-v2]
        end
    end

    %% Analysis Components
    subgraph "Analysis Components"
        EXTRACTION[📊 Data Extraction]
        SIMILARITY[🎯 Similarity Analysis]
        QUALITY[✨ Quality Scoring]
        KEYWORDS[🔑 Keyword Analysis]
    end

    %% Output Layer
    subgraph "Output Layer"
        RESULTS[📈 Analysis Results]
        WEB_RESULTS[🌐 Results Page<br/>templates/results.html]
        JSON_OUTPUT[📋 JSON Output]
    end

    %% Data Flow Connections
    USER --> WEB_UI
    USER --> RESUME
    USER --> JOB_DESC
    
    WEB_UI --> FLASK_APP
    RESUME --> UPLOAD
    UPLOAD --> PARSER
    JOB_DESC --> FLASK_APP
    
    CONFIG_LOADER --> SKILLS_YAML
    CONFIG_LOADER --> VERBS_YAML
    
    FLASK_APP --> PARSER
    FLASK_APP --> ANALYZER
    PARSER --> SPACY
    ANALYZER --> SENTENCE_BERT
    
    PARSER --> EXTRACTION
    ANALYZER --> SIMILARITY
    ANALYZER --> QUALITY
    ANALYZER --> KEYWORDS
    
    CONFIG_LOADER --> EXTRACTION
    CONFIG_LOADER --> QUALITY
    CONFIG_LOADER --> KEYWORDS
    
    EXTRACTION --> RESULTS
    SIMILARITY --> RESULTS
    QUALITY --> RESULTS
    KEYWORDS --> RESULTS
    
    RESULTS --> JSON_OUTPUT
    RESULTS --> WEB_RESULTS
    WEB_RESULTS --> USER

    %% Styling
    classDef inputClass fill:#e1f5fe
    classDef webClass fill:#f3e5f5
    classDef configClass fill:#fff3e0
    classDef nlpClass fill:#e8f5e8
    classDef analysisClass fill:#fff8e1
    classDef outputClass fill:#fce4ec

    class USER,RESUME,JOB_DESC inputClass
    class WEB_UI,FLASK_APP,UPLOAD webClass
    class CONFIG_LOADER,SKILLS_YAML,VERBS_YAML configClass
    class PARSER,ANALYZER,SPACY,SENTENCE_BERT nlpClass
    class EXTRACTION,SIMILARITY,QUALITY,KEYWORDS analysisClass
    class RESULTS,WEB_RESULTS,JSON_OUTPUT outputClass
```

## Detailed Data Flow Process

### 1. Input Processing Flow
```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant Flask
    participant Upload
    participant Parser

    User->>WebUI: Upload resume PDF + job description
    WebUI->>Flask: POST /analyze
    Flask->>Upload: Save resume with UUID filename
    Flask->>Parser: extract_text_from_pdf(file_path)
    Parser-->>Flask: Resume text content
    Note over Flask: Clean up uploaded file after processing
```

### 2. Configuration Loading Flow
```mermaid
sequenceDiagram
    participant ConfigLoader
    participant SkillsYAML
    participant VerbsYAML
    participant Cache

    ConfigLoader->>SkillsYAML: Load skills configuration
    SkillsYAML-->>ConfigLoader: Skills with synonyms mapping
    ConfigLoader->>VerbsYAML: Load action verbs with weights
    VerbsYAML-->>ConfigLoader: Weighted verb tiers
    ConfigLoader->>Cache: Store processed configurations
    Note over ConfigLoader: Lazy loading on first use
```

### 3. NLP Analysis Flow
```mermaid
sequenceDiagram
    participant Analyzer
    participant Parser
    participant spaCy
    participant SentenceBERT
    participant ConfigLoader

    Analyzer->>Parser: extract_name/email/phone/skills
    Parser->>spaCy: NER processing for personal info
    spaCy-->>Parser: Extracted entities
    
    Analyzer->>SentenceBERT: encode(resume_text, job_description)
    SentenceBERT-->>Analyzer: Similarity embeddings
    
    Analyzer->>ConfigLoader: get_action_verbs_config()
    ConfigLoader-->>Analyzer: Weighted action verbs
    
    Analyzer->>Parser: extract_action_verbs(text)
    Parser-->>Analyzer: Action verb analysis with weights
```

### 4. Scoring and Analysis Flow
```mermaid
flowchart TD
    START[Resume Text Input] --> BASIC[Basic Info Extraction]
    START --> SIMILARITY[Similarity Analysis]
    START --> QUALITY[Quality Scoring]
    
    BASIC --> NAME[Name via spaCy NER]
    BASIC --> EMAIL[Email via Regex]
    BASIC --> PHONE[Phone via Regex]
    BASIC --> SKILLS[Skills via YAML Config]
    
    SIMILARITY --> EMBEDDINGS[Generate Text Embeddings]
    EMBEDDINGS --> COSINE[Calculate Cosine Similarity]
    
    QUALITY --> ACTION_VERBS[Extract Action Verbs]
    QUALITY --> QUANTIFIABLE[Count Quantifiable Achievements]
    QUALITY --> CONCISENESS[Measure Conciseness]
    
    ACTION_VERBS --> WEIGHTED_SCORE[Apply Tier Weights]
    QUANTIFIABLE --> REGEX_COUNT[Regex Pattern Matching]
    CONCISENESS --> SENTENCE_ANALYSIS[Average Words per Sentence]
    
    WEIGHTED_SCORE --> COMPOSITE[Composite Quality Score]
    REGEX_COUNT --> COMPOSITE
    SENTENCE_ANALYSIS --> COMPOSITE
    
    NAME --> RESULTS[Final Results Dictionary]
    EMAIL --> RESULTS
    PHONE --> RESULTS
    SKILLS --> RESULTS
    COSINE --> RESULTS
    COMPOSITE --> RESULTS
    
    RESULTS --> JSON_API[JSON API Response]
    RESULTS --> WEB_DISPLAY[Web Template Rendering]
```

## Data Structures and Flow

### Input Data Structure
```
User Input:
├── Resume File (PDF)
├── Job Description (Text)
└── Analysis Request

File Processing:
├── UUID Generation for uploaded file
├── PDF Text Extraction (PyMuPDF)
├── Temporary File Storage
└── Cleanup after processing
```

### Configuration Data Flow
```
YAML Configs:
├── skills.yaml
│   ├── Categories (programming_languages, web_frameworks, etc.)
│   ├── Primary Skills
│   └── Synonyms Mapping
└── action_verbs.yaml
    ├── Tier Classification (impact, achievement, technical, basic)
    ├── Weight Assignment (3.0, 2.0, 1.5, 1.0)
    └── Verb Lists per Tier

Processing:
├── Lazy Loading on First Use
├── Caching for Performance
├── Synonym Resolution
└── Weight Application
```

### Analysis Pipeline Data Flow
```
Text Processing:
├── spaCy Pipeline
│   ├── Tokenization
│   ├── Named Entity Recognition
│   ├── Part-of-Speech Tagging
│   └── Sentence Segmentation
├── Sentence Transformers
│   ├── Text Embedding Generation
│   ├── Similarity Computation
│   └── Cosine Score Calculation
└── Regex Pattern Matching
    ├── Email Detection
    ├── Phone Number Detection
    └── Quantifiable Achievement Detection

Scoring Components:
├── Action Verb Scoring (60% weight)
│   ├── Tier-based Weight Application
│   ├── Frequency Analysis
│   └── Line-normalized Scoring
├── Quantifiable Achievements (25% weight)
│   ├── Number Pattern Detection
│   ├── Percentage Identification
│   └── Currency Amount Detection
└── Conciseness Scoring (15% weight)
    ├── Average Words per Sentence
    ├── Sentence Length Analysis
    └── Brevity Assessment
```

### Output Data Structure
```
Analysis Results:
├── Basic Information
│   ├── name: String
│   ├── email: String
│   ├── phone: String
│   └── skills: List[String]
├── Similarity Analysis
│   └── similarity_score: Float (0-1)
├── Quality Analysis
│   ├── overall_score: Float (0-100)
│   ├── action_verb_analysis: Dict
│   ├── quantifiable_score: Float
│   ├── conciseness_score: Float
│   └── breakdown: Dict
├── Keyword Analysis
│   ├── matched_keywords: List[String]
│   └── missing_keywords: List[String]
└── Presentation
    ├── JSON API Response
    └── HTML Template Rendering
```

## Performance Considerations

### Model Loading Strategy
- **Lazy Loading**: NLP models loaded only when first needed
- **Singleton Pattern**: Models cached after first load
- **Memory Management**: Efficient model reuse across requests

### File Processing Optimization
- **Temporary Storage**: UUID-based filename collision avoidance
- **Immediate Cleanup**: Files deleted after processing
- **Error Handling**: Graceful failure with cleanup

### Configuration Caching
- **One-time Load**: YAML configs loaded and cached
- **Synonym Preprocessing**: Efficient lookup structures
- **Weight Normalization**: Pre-calculated scoring weights

This data flow diagram provides a comprehensive view of how data moves through the NLP Resume Analyzer system, from user input through processing to final results presentation.