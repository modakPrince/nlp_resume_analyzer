# History Page Implementation

## Overview
The History page feature allows users to view, search, filter, and manage all their previously analyzed resumes. Every analysis is automatically saved to a SQLite database and can be retrieved later.

## Database Schema

### Analysis Table
```python
- id: Primary key (auto-increment)
- filename: Original resume filename
- upload_date: Timestamp of when the analysis was performed
- extracted_name: Name extracted from resume
- extracted_email: Email extracted from resume
- extracted_phone: Phone number extracted from resume
- mode: 'quality_check' or 'full_analysis'
- quality_score: Quality score (0-100)
- job_match_score: Job matching score (0-100, 0 for quality check mode)
- impact_score: Impact score from enhanced analysis
- structure_score: Structure score from enhanced analysis
- overall_score: Overall composite score
- results_json: Complete analysis results stored as JSON
- resume_preview: First 500 characters of resume text
- skills_count: Number of skills extracted
- matched_keywords_count: Keywords matched with job description
- missing_keywords_count: Keywords missing from resume
```

## Features Implemented

### 1. Automatic Saving
**Location:** `src/web_app/app.py` - `/analyze` route

Every resume analysis is automatically saved to the database after processing:
- Captures both Quality Check and Full Analysis modes
- Stores complete results as JSON for future retrieval
- Includes metadata (scores, contact info, skills count)
- Gracefully handles database errors without breaking the analysis

```python
# Database save happens automatically after analysis
analysis_record = Analysis(
    filename=resume_file.filename,
    mode='quality_check' if is_quality_mode else 'full_analysis',
    quality_score=enhanced_analysis['quality']['score'],
    # ... other fields
)
db.session.add(analysis_record)
db.session.commit()
```

### 2. History Page
**Route:** `/history`
**Template:** `src/web_app/templates/history.html`

Displays all saved analyses in a table with:
- **Statistics Dashboard:**
  - Total analyses count
  - Quality Check count
  - Full Analysis count
  - Average quality score

- **Filtering & Search:**
  - Mode filter (All / Quality Check Only / Full Analysis)
  - Search by filename or candidate name
  - Auto-submit on filter change

- **Analysis Table:**
  - Date & time of analysis
  - Filename (truncated with tooltip)
  - Extracted candidate name
  - Mode badge (color-coded)
  - Quality, Match, and Overall scores
  - Action buttons (View, Delete)

### 3. View Individual Analysis
**Route:** `/analysis/<id>`

Retrieves a saved analysis from the database and displays it using the same results template:
- Loads complete results from `results_json` field
- Adds metadata (upload date, filename) to the display
- Shows a banner indicating it's a historical view
- Full functionality identical to fresh analysis

### 4. Delete Analysis
**Route:** `/analysis/<id>/delete` (POST)

Allows users to permanently delete saved analyses:
- Requires POST method for safety
- Includes JavaScript confirmation dialog
- Redirects to history page after deletion

### 5. Navigation Integration

Added "View History" links to:
- **Index page (/):** Top-right navigation button
- **Results page (/analyze):** Top-right navigation button with back to home link

## Database Configuration

**Location:** `data/resume_analyzer.db`

The database is automatically created on first run using SQLite:
```python
DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'resume_analyzer.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
```

**Benefits of SQLite:**
- No server required
- Single portable file
- Perfect for desktop/local applications
- Supports full SQL queries with indexes

## Usage Guide

### For Users

1. **Viewing History:**
   - Click "View History" button from home or results page
   - See all your past analyses at a glance

2. **Filtering:**
   - Use the "Filter by Mode" dropdown to see only Quality Checks or Full Analyses
   - Filter automatically applies when changed

3. **Searching:**
   - Type in the search box to find analyses by filename or candidate name
   - Click "Apply Filters" to execute search

4. **Viewing Details:**
   - Click "View" button on any analysis
   - See the complete original analysis results

5. **Deleting:**
   - Click "Delete" button on unwanted analyses
   - Confirm deletion in the popup dialog

### For Developers

**Adding New Fields:**
1. Update `models.py` Analysis class
2. Update `app.py` analyze route to save new field
3. Update `history.html` template to display new field
4. Run database migration or drop/recreate tables

**Querying Analyses:**
```python
from models import Analysis, db

# Get all analyses
all_analyses = Analysis.query.all()

# Filter by mode
quality_checks = Analysis.query.filter_by(mode='quality_check').all()

# Search by name
results = Analysis.query.filter(Analysis.extracted_name.ilike('%John%')).all()

# Get statistics
stats = Analysis.get_statistics()
```

## File Structure

```
src/web_app/
├── app.py                      # Routes: /history, /analysis/<id>, /analysis/<id>/delete
├── models.py                   # Analysis model with SQLAlchemy
└── templates/
    ├── history.html            # History page template
    ├── index.html              # Updated with history link
    └── results.html            # Updated with history link, reused for viewing saved analyses
```

## Technical Details

### Database Indexes
Created for performance on common queries:
- `upload_date` - For chronological sorting
- `mode` - For filtering by analysis type
- `quality_score` - For statistics calculations
- `job_match_score` - For statistics calculations

### JSON Storage
Complete analysis results stored as JSON text:
- Allows flexible schema changes
- Preserves all data for future use
- Enables export functionality
- Supports backward compatibility

### Error Handling
- Database save failures don't break analysis
- 404 errors for invalid analysis IDs
- Graceful handling of missing data
- Confirmation dialogs prevent accidental deletion

## Future Enhancements

Potential additions:
- **CSV Export:** Download history as CSV file
- **Batch Operations:** Delete multiple analyses at once
- **Date Range Filter:** Filter by upload date
- **Sorting:** Sort table by any column
- **Pagination:** For large history lists
- **Analytics Dashboard:** Trends over time, score comparisons
- **Sharing:** Generate shareable links to analyses
- **Notes:** Add custom notes to saved analyses

## Testing

To test the History page:

1. **Start Flask server:**
   ```bash
   python src/web_app/app.py
   ```

2. **Upload test resumes:**
   - Navigate to http://localhost:8080
   - Upload `data/sample_resumes/sample_resume.pdf`
   - Try both Quality Check and Full Analysis modes

3. **View history:**
   - Click "View History" button
   - Verify analyses appear in table
   - Test filters and search

4. **View details:**
   - Click "View" on any analysis
   - Verify all data displays correctly

5. **Delete analysis:**
   - Click "Delete" button
   - Confirm deletion
   - Verify it's removed from history

## Troubleshooting

**Database not created:**
- Check that `data/` directory exists
- Verify Flask app has write permissions
- Check console for database initialization message

**Analyses not saving:**
- Check terminal for error messages
- Verify SQLAlchemy is installed: `pip list | grep SQLAlchemy`
- Check database file exists: `data/resume_analyzer.db`

**History page shows no data:**
- Verify analyses are being saved (check database file size)
- Check browser console for JavaScript errors
- Try clearing filters and search

**"View" button shows error:**
- Verify `results_json` field is valid JSON
- Check Analysis model's `get_results()` method
- Ensure all required fields are present in results

## Implementation Status

✅ Database setup with SQLite and SQLAlchemy
✅ Analysis model with complete schema
✅ Automatic saving of all analyses
✅ History page with statistics dashboard
✅ Filtering by mode (Quality Check / Full Analysis)
✅ Search by filename and name
✅ View individual saved analysis
✅ Delete saved analysis
✅ Navigation integration in all pages
✅ Responsive design with Tailwind CSS
✅ Dark mode support
✅ Empty state handling

## Git Commits

Relevant commits:
- `Setup SQLite and SQLAlchemy` - Database foundation
- Next: `Implement History page with filtering and search`
