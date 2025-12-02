# BPM - Blood Pressure Monitoring Analysis Tool

## Project Overview

A clinical decision-support tool for analyzing temporal blood pressure variability in ~1000 patients, inspired by the methodology from [Grillo et al., J Clin Hypertens 2015](https://pubmed.ncbi.nlm.nih.gov/25880017/).

### Target Users
- Data entry staff (non-technical)
- Cardiologists (for reviewing outputs)

### Core Requirements
- Excel file upload (raw BP data)
- Temporal BP variability analysis
- Professional, Apple-style UI
- Cross-platform: Windows 11 + macOS
- Guided workflow for non-technical users

---

## Analysis Methodology (Based on Reference Study)

### Input Data Expected
| Column | Description |
|--------|-------------|
| Patient ID | Unique identifier |
| Date | Measurement date |
| Time | Measurement time |
| SBP | Systolic Blood Pressure (mmHg) |
| DBP | Diastolic Blood Pressure (mmHg) |
| Heart Rate | Optional (bpm) |
| Notes | Optional |

### Time Period Definitions
- **Daytime**: 08:00 - 22:00
- **Nighttime**: 00:00 - 06:00
- **24-hour**: Full day

### Calculated Metrics

#### 1. Basic Statistics (per patient, per period)
- Mean SBP / DBP
- Min / Max values
- Reading count

#### 2. Dispersion Measures
- **SD (Standard Deviation)**: √[Σ(xi - x̄)² / (n-1)]
- **CV (Coefficient of Variation)**: (SD / Mean) × 100
- **Weighted SD**: (SD_day × hours_day + SD_night × hours_night) / 24

#### 3. Sequence-Based Measures
- **ARV (Average Real Variability)**: Σ|BPi+1 - BPi| / (n-1)
  - Captures beat-to-beat or reading-to-reading variation
  - More sensitive to short-term fluctuations than SD

#### 4. Derived Indices
- **Morning Surge**: Morning SBP - Lowest nighttime SBP
- **Nocturnal Dipping**: ((Daytime mean - Nighttime mean) / Daytime mean) × 100
  - Normal dipper: 10-20%
  - Non-dipper: <10%
  - Extreme dipper: >20%
  - Reverse dipper: <0%

### Output Reports
1. **Individual Patient Report** (PDF)
   - Summary statistics table
   - Temporal trend chart
   - Variability metrics
   - Dipping status classification

2. **Cohort Summary** (Excel/PDF)
   - Aggregate statistics across all patients
   - Distribution histograms
   - Risk stratification counts

3. **Raw Processed Data** (Excel)
   - All calculated metrics exportable

---

## Alternative Solutions

### Option A: Excel VBA Macro
**Complexity: Low | Dev Time: 1-2 weeks**

```
Pros:
+ Simplest deployment (single .xlsm file)
+ No installation required
+ Familiar environment for data entry staff
+ Easy to modify formulas
+ Works offline

Cons:
- Limited UI customization (no Apple-style)
- Windows-centric (Mac Excel VBA support is poor)
- Security warnings for macros
- Difficult to create beautiful charts
- No guided workflow possible
- Hard to maintain as complexity grows
```

### Option B: Python Desktop App (PyQt/PySide + Pandas)
**Complexity: Medium | Dev Time: 3-4 weeks**

```
Pros:
+ Full UI customization (Apple-style achievable)
+ Cross-platform (Windows + Mac)
+ Powerful data analysis (Pandas, NumPy, SciPy)
+ Professional PDF reports (ReportLab, WeasyPrint)
+ Beautiful charts (Matplotlib, Plotly)
+ Guided wizard-style workflow possible

Cons:
- Requires packaging (PyInstaller/cx_Freeze)
- Larger app size (~100-200MB)
- Needs code signing for smooth Mac install
- Users download and install executable
```

### Option C: Electron Desktop App (JavaScript/TypeScript)
**Complexity: Medium-High | Dev Time: 4-5 weeks**

```
Pros:
+ Best UI flexibility (web technologies)
+ Apple-style design easy with CSS
+ Cross-platform native feel
+ Modern, polished look

Cons:
- Large app size (~150-300MB)
- Higher memory usage
- Statistical libraries less mature than Python
- Overkill for data analysis tasks
```

### Option D: Web Application (Streamlit or Gradio)
**Complexity: Low-Medium | Dev Time: 2-3 weeks**

```
Pros:
+ No installation for users (browser-based)
+ Easy deployment (can run locally or hosted)
+ Python backend (full Pandas power)
+ Decent UI components
+ Auto-updates (if hosted)

Cons:
- Requires local server or internet
- Less "app-like" feel
- Privacy concerns if hosted (patient data)
- Limited offline capability
```

### Option E: Tauri Desktop App (Rust + Web Frontend)
**Complexity: High | Dev Time: 5-6 weeks**

```
Pros:
+ Smallest app size (~10-30MB)
+ Best performance
+ Native OS integration
+ Modern UI (React/Vue/Svelte frontend)

Cons:
- Rust learning curve
- Statistical analysis in Rust is less convenient
- More complex build process
```

---

## My Recommendation: Option B (Python Desktop App)

### Rationale

1. **Best balance of UI quality and analytical power**
   - PyQt6/PySide6 can achieve Apple-style aesthetics
   - Pandas/NumPy handle statistical calculations effortlessly
   - Matplotlib/Plotly create publication-quality charts

2. **Cross-platform reality**
   - Python apps work reliably on both Windows and Mac
   - PyInstaller creates standalone executables
   - No runtime installation needed by users

3. **Medical/Clinical domain fit**
   - Python is the de facto standard in biomedical data analysis
   - Easy to add new metrics as research evolves
   - Extensive statistical libraries (scipy.stats)

4. **Maintainability**
   - Clean separation of UI and logic
   - Easy to unit test calculations
   - Well-documented ecosystem

### Recommended Stack

| Component | Technology |
|-----------|------------|
| UI Framework | PySide6 (Qt for Python) |
| Data Processing | Pandas, NumPy |
| Statistics | SciPy |
| Charts | Matplotlib + Plotly |
| PDF Reports | ReportLab or WeasyPrint |
| Excel I/O | openpyxl |
| Packaging | PyInstaller |
| Styling | Qt Style Sheets (QSS) |

---

## Proposed Architecture

```
BPM/
├── src/
│   ├── main.py              # Entry point
│   ├── ui/
│   │   ├── main_window.py   # Main application window
│   │   ├── wizard.py        # Step-by-step guided workflow
│   │   ├── styles.qss       # Apple-style CSS
│   │   └── components/      # Reusable UI components
│   ├── analysis/
│   │   ├── metrics.py       # BP variability calculations
│   │   ├── temporal.py      # Time-based analysis
│   │   └── classification.py # Dipping status, risk groups
│   ├── io/
│   │   ├── excel_reader.py  # Excel import
│   │   └── report_generator.py # PDF/Excel export
│   └── utils/
│       └── validators.py    # Data validation
├── resources/
│   ├── icons/
│   └── templates/
├── tests/
├── requirements.txt
└── build/                   # PyInstaller output
```

---

## UI Design Principles (Apple Style)

1. **Simplicity**: One primary action per screen
2. **Whitespace**: Generous padding, breathing room
3. **Typography**: SF Pro or Inter font, clear hierarchy
4. **Colors**:
   - Primary: #007AFF (blue)
   - Background: #F5F5F7 (light gray)
   - Text: #1D1D1F (near black)
   - Success: #34C759 (green)
   - Warning: #FF9500 (orange)
   - Error: #FF3B30 (red)
5. **Animations**: Subtle transitions (200-300ms)
6. **Feedback**: Clear loading states, success confirmations

### Wizard Flow

```
[1. Welcome] → [2. Upload Excel] → [3. Map Columns] → [4. Validate Data]
     ↓
[5. Configure Analysis] → [6. Processing...] → [7. Review Results] → [8. Export]
```

---

## Development Phases

### Phase 1: Core Engine (Week 1)
- [ ] Excel file parsing
- [ ] Data validation
- [ ] Basic statistics (mean, SD, CV)
- [ ] ARV calculation
- [ ] Time period classification

### Phase 2: Advanced Metrics (Week 2)
- [ ] Weighted SD
- [ ] Nocturnal dipping classification
- [ ] Morning surge calculation
- [ ] Per-patient aggregation

### Phase 3: UI Development (Week 2-3)
- [ ] Main window with Apple styling
- [ ] Wizard workflow
- [ ] Data preview table
- [ ] Interactive charts
- [ ] Progress indicators

### Phase 4: Reporting (Week 3-4)
- [ ] Individual patient PDF
- [ ] Cohort summary PDF
- [ ] Excel export with all metrics
- [ ] Chart embedding in reports

### Phase 5: Packaging & Testing (Week 4)
- [ ] PyInstaller build for Windows
- [ ] PyInstaller build for macOS
- [ ] User acceptance testing
- [ ] Documentation

---

## Clarified Requirements

1. **Data format**: Variable - need flexible column mapper (simple drag-drop or dropdown selection)
2. **Measurement frequency**: Variable - minutes to hours to days (adaptive time analysis)
3. **Time spans**: Variable - single day or longitudinal visits over weeks/months
4. **Priority metrics**: All clinically important metrics
5. **Privacy**: Local-only processing, no cloud, respect patient data privacy

---

## Summary

| Option | UI Quality | Cross-Platform | Dev Effort | My Vote |
|--------|-----------|----------------|------------|---------|
| Excel Macro | Poor | No (Mac issues) | Low | No |
| Python Desktop | Excellent | Yes | Medium | **Yes** |
| Electron | Excellent | Yes | High | Overkill |
| Web App | Good | Yes (browser) | Low-Medium | Privacy concerns |
| Tauri | Excellent | Yes | High | Overkill |

**Recommended**: Python Desktop App with PySide6, delivering an Apple-style guided wizard for non-technical users to upload Excel data and receive professional clinical reports.
