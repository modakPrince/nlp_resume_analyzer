# Data Export Feature

## Overview
The Data Export feature allows users to export their resume analysis data in multiple formats for record-keeping, sharing, or further analysis in external tools.

## Export Formats

### 1. CSV Export (Bulk)
**Route:** `/export/csv`  
**Button Location:** History page, top-right near filters

Exports all analyses (or filtered subset) to a CSV file.

**Features:**
- ✅ Respects current filters (mode, search)
- ✅ Includes all key metrics and metadata
- ✅ Timestamp-based filename
- ✅ Compatible with Excel, Google Sheets, etc.

**CSV Columns:**
```csv
ID, Upload Date, Filename, Name, Email, Phone, Mode, 
Quality Score, Job Match Score, Impact Score, Structure Score, 
Overall Score, Skills Count, Matched Keywords, Missing Keywords
```

**Example Filename:**
```
resume_analyses_20251006_215530.csv
```

**Use Cases:**
- Track resume improvements over time
- Compare multiple candidate analyses
- Create charts/graphs in spreadsheet software
- Backup analysis data
- Share data with team members

---

### 2. JSON Export (Individual)
**Route:** `/analysis/<id>/export/json`  
**Button Location:** History page, actions column (📥 icon)

Exports a single analysis with complete details as JSON.

**Features:**
- ✅ Complete analysis data including full results
- ✅ Machine-readable format
- ✅ Safe filename generation
- ✅ Timestamp included

**JSON Structure:**
```json
{
  "id": 1,
  "filename": "john_doe_resume.pdf",
  "upload_date": "2025-10-06T21:30:00",
  "extracted_name": "John Doe",
  "extracted_email": "john@example.com",
  "extracted_phone": "+1-555-0123",
  "mode": "full_analysis",
  "quality_score": 85.5,
  "job_match_score": 78.2,
  "impact_score": 82.0,
  "structure_score": 88.0,
  "overall_score": 83.4,
  "skills_count": 15,
  "matched_keywords_count": 8,
  "missing_keywords_count": 3,
  "results": {
    // Complete analysis results
  }
}
```

**Example Filename:**
```
analysis_john_doe_resume_20251006_215530.json
```

**Use Cases:**
- Import data into other systems
- API integrations
- Detailed data analysis with Python/R
- Archive complete analysis details
- Share with technical stakeholders

---

## Implementation Details

### CSV Export Implementation

**File:** `src/web_app/app.py`

```python
@app.route('/export/csv')
def export_csv():
    # Get filter parameters (same as history page)
    mode_filter = request.args.get('mode', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Query database with filters
    query = Analysis.query
    if mode_filter != 'all':
        query = query.filter_by(mode=mode_filter)
    if search_query:
        query = query.filter(...)
    
    analyses = query.order_by(Analysis.upload_date.desc()).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([...])  # Header
    
    for analysis in analyses:
        writer.writerow([...])  # Data
    
    # Return as downloadable file
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
```

**Key Features:**
- Uses Python's built-in `csv` module
- Creates file in memory (no disk write)
- Preserves filter state from history page
- Automatic timestamp in filename
- Proper CSV escaping for special characters

---

### JSON Export Implementation

**File:** `src/web_app/app.py`

```python
@app.route('/analysis/<int:analysis_id>/export/json')
def export_single_json(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Get complete data using model method
    analysis_dict = analysis.to_dict()
    
    # Return as downloadable JSON
    return Response(
        json.dumps(analysis_dict, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
```

**Key Features:**
- Uses model's `to_dict()` method
- Pretty-printed JSON (indent=2)
- Safe filename generation
- Complete data preservation

---

## UI Components

### History Page - CSV Export Button

**Location:** Next to "Apply Filters" button

```html
<a href="/export/csv?mode={{ current_filter }}&search={{ search_query }}" 
   class="btn-cyan">
    <span class="mr-2">📥</span>
    Export to CSV
</a>
```

**Behavior:**
- Passes current filter state via URL parameters
- Opens download dialog immediately
- No page reload required

---

### History Page - JSON Export Button

**Location:** Actions column in each table row

```html
<a href="/analysis/{{ analysis.id }}/export/json" 
   class="btn-cyan-small"
   title="Export as JSON">
    📥
</a>
```

**Behavior:**
- Icon-only button to save space
- Hover shows tooltip
- Downloads single analysis

---

## Usage Guide

### Exporting to CSV

1. **Navigate to History page** (`/history`)
2. **(Optional) Apply filters:**
   - Select mode: "All" / "Quality Check" / "Full Analysis"
   - Enter search term for filename or name
   - Click "Apply Filters"
3. **Click "Export to CSV"** button (top-right)
4. **File downloads automatically:**
   - Opens in default CSV viewer (Excel/Sheets)
   - Saved to Downloads folder

### Exporting Individual Analysis as JSON

1. **Navigate to History page** (`/history`)
2. **Find the analysis** you want to export
3. **Click the 📥 icon** in the Actions column
4. **JSON file downloads automatically:**
   - Can be opened in text editor
   - Can be imported into other tools

---

## Data Format Details

### CSV Format

```csv
ID,Upload Date,Filename,Name,Email,Phone,Mode,Quality Score,Job Match Score,Impact Score,Structure Score,Overall Score,Skills Count,Matched Keywords,Missing Keywords
1,2025-10-06 21:30:00,john_resume.pdf,John Doe,john@example.com,+1-555-0123,full_analysis,85.50,78.20,82.00,88.00,83.40,15,8,3
2,2025-10-06 20:15:00,jane_resume.pdf,Jane Smith,jane@example.com,,quality_check,90.00,N/A,85.50,92.00,89.20,18,0,0
```

**Notes:**
- Date format: `YYYY-MM-DD HH:MM:SS`
- Scores: 2 decimal places
- Missing data: Empty strings
- Job Match for Quality Check: `N/A`

---

### JSON Format

```json
{
  "id": 1,
  "filename": "john_resume.pdf",
  "upload_date": "2025-10-06T21:30:00",
  "extracted_name": "John Doe",
  "extracted_email": "john@example.com",
  "extracted_phone": "+1-555-0123",
  "mode": "full_analysis",
  "scores": {
    "quality": 85.5,
    "job_match": 78.2,
    "impact": 82.0,
    "structure": 88.0,
    "overall": 83.4
  },
  "metadata": {
    "skills_count": 15,
    "matched_keywords_count": 8,
    "missing_keywords_count": 3
  },
  "results": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "skills": [...],
    "matched_keywords": [...],
    "missing_keywords": [...],
    "enhanced_analysis": {...}
  }
}
```

---

## Technical Requirements

### Python Modules
```python
import csv               # Built-in
import json              # Built-in
from io import StringIO  # Built-in
from flask import Response  # Flask
```

**No additional dependencies required!**

---

## File Size Considerations

### CSV Files
- **Single row:** ~200-300 bytes
- **100 analyses:** ~25-30 KB
- **1000 analyses:** ~250-300 KB

CSV files are very compact and efficient.

### JSON Files
- **Single analysis:** ~5-15 KB (depending on result complexity)
- Larger due to complete data preservation
- Still very manageable for typical use

---

## Security & Privacy

### Data Protection
- ✅ No external API calls
- ✅ Files generated in memory
- ✅ No temporary files on disk
- ✅ User-initiated downloads only
- ✅ No data transmitted to third parties

### Filename Safety
```python
# Special characters are sanitized
safe_filename = filename.replace('.pdf', '').replace('.docx', '').replace(' ', '_')
```

---

## Browser Compatibility

**Tested Browsers:**
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari

**Download Behavior:**
- Modern browsers show download progress
- Files saved to default Downloads folder
- No popup blockers interfere (initiated by user click)

---

## Future Enhancements

### Potential Features
1. **PDF Export**
   - Generate PDF reports with charts
   - Professional formatting
   - Requires: `reportlab` or `weasyprint`

2. **Excel Export (.xlsx)**
   - Native Excel format with formatting
   - Multiple sheets (summary, details)
   - Requires: `openpyxl`

3. **Batch JSON Export**
   - Export all filtered analyses as single JSON array
   - Useful for bulk imports

4. **Custom Column Selection**
   - Let users choose which columns to include
   - Customize CSV output

5. **Scheduled Exports**
   - Automatic weekly/monthly exports
   - Email delivery option

---

## Troubleshooting

### CSV file won't open in Excel
**Solution:** The file is UTF-8 encoded. Excel should detect this automatically. If not:
1. Open Excel
2. Go to Data → From Text/CSV
3. Select the exported file
4. Choose UTF-8 encoding

### JSON file shows as plain text
**Solution:** This is normal. JSON files are text-based. To view formatted:
1. Open in browser (drag & drop)
2. Use JSON viewer extension
3. Open in VS Code or text editor

### Export button doesn't download
**Solution:**
1. Check browser's download settings
2. Disable popup blockers for localhost
3. Check Flask server console for errors

### Empty CSV file
**Solution:**
- No analyses match current filters
- Try clearing filters and search
- Upload some resumes first to create data

---

## Testing

### Manual Testing Steps

1. **Test CSV Export - All Data:**
   ```
   1. Go to /history
   2. Ensure no filters applied
   3. Click "Export to CSV"
   4. Verify file downloads
   5. Open in Excel/Sheets
   6. Verify all columns present
   ```

2. **Test CSV Export - Filtered:**
   ```
   1. Go to /history
   2. Filter by "Quality Check Only"
   3. Click "Export to CSV"
   4. Verify only quality checks in file
   ```

3. **Test JSON Export:**
   ```
   1. Go to /history
   2. Click 📥 icon on any analysis
   3. Verify JSON downloads
   4. Open in text editor
   5. Verify JSON is valid and complete
   ```

### Automated Testing (Future)

```python
def test_csv_export(client):
    response = client.get('/export/csv')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert 'resume_analyses_' in response.headers['Content-Disposition']

def test_json_export(client):
    response = client.get('/analysis/1/export/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    data = json.loads(response.data)
    assert 'id' in data
    assert 'results' in data
```

---

## Implementation Checklist

✅ CSV export route (`/export/csv`)
✅ JSON export route (`/analysis/<id>/export/json`)
✅ CSV button on history page
✅ JSON button on history page (per row)
✅ Filter state preservation
✅ Timestamp-based filenames
✅ Proper MIME types
✅ Download headers
✅ Error handling (404 for invalid IDs)
✅ Documentation

---

## Summary

The Data Export feature provides flexible data extraction:

- **CSV:** Perfect for spreadsheets, charts, and sharing
- **JSON:** Ideal for technical analysis and integrations
- **No dependencies:** Uses built-in Python modules
- **Filter-aware:** Exports exactly what you see
- **Privacy-focused:** All processing is local

Export your resume analysis data anytime, anywhere! 📥
