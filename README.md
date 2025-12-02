# BPM - Blood Pressure Monitoring Analysis Tool

<p align="center">
  <img src="resources/icons/logo.png" alt="BPM Logo" width="128" height="128">
</p>

<p align="center">
  <strong>Analyze blood pressure variability patterns in your patient data</strong>
</p>

<p align="center">
  <a href="#for-clinicians">For Clinicians</a> •
  <a href="#for-data-entry-staff">For Data Entry Staff</a> •
  <a href="#installation">Installation</a> •
  <a href="#technical-details">Technical Details</a>
</p>

---

## What Does This App Do?

BPM helps cardiologists and healthcare professionals analyze **blood pressure variability** - an important clinical marker that goes beyond simple average BP readings.

### The Problem It Solves

Traditional BP analysis only looks at averages. But research shows that **how much blood pressure fluctuates** (variability) is equally important for predicting cardiovascular risk. Calculating these variability metrics manually from Excel spreadsheets is:

- Time-consuming (especially for 1000+ patients)
- Error-prone
- Requires statistical expertise

### The Solution

BPM automatically calculates all clinically important BP variability metrics from your Excel data in seconds, with a simple drag-and-drop interface that anyone can use.

---

## For Clinicians

### What Metrics Does BPM Calculate?

| Metric | What It Measures | Why It Matters |
|--------|------------------|----------------|
| **Mean SBP/DBP** | Average blood pressure | Baseline BP level |
| **SD (Standard Deviation)** | How spread out readings are | Overall variability |
| **CV (Coefficient of Variation)** | SD normalized by mean (%) | Compare variability across patients |
| **ARV (Average Real Variability)** | Average change between consecutive readings | Short-term fluctuations |
| **Weighted SD** | Day/night SD weighted by hours | Eliminates dipping artifact |
| **Nocturnal Dipping %** | Night vs day BP reduction | Cardiovascular risk marker |
| **Morning Surge** | AM rise from night low | Stroke/cardiac event risk |
| **BP Classification** | AHA/ACC staging | Treatment guidance |

### Dipping Status Classification

| Status | Definition | Clinical Significance |
|--------|------------|----------------------|
| Normal Dipper | 10-20% nocturnal drop | Normal pattern |
| Non-Dipper | <10% drop | Higher CV risk |
| Extreme Dipper | >20% drop | Nocturnal hypotension risk |
| Reverse Dipper | Night > Day | Highest CV risk |

### Evidence Base

This methodology is based on established clinical research, including:
- Grillo et al., J Clin Hypertens 2015 (DOI: 10.1111/jch.12551)
- Parati et al., J Clin Hypertens 2018 (DOI: 10.1111/jch.13304)
- ESH/ESC Guidelines on Ambulatory Blood Pressure Monitoring

---

## For Data Entry Staff

### How to Use BPM (Step-by-Step)

#### Step 1: Open the App
Double-click the BPM icon on your desktop.

#### Step 2: Upload Your Excel File
- **Drag and drop** your Excel file onto the app
- Or click "Browse" to select it

#### Step 3: Match Your Columns
The app will try to automatically detect your columns. You just need to verify:
- Which column has the **Patient ID**
- Which column has the **Date/Time**
- Which column has **Systolic BP** (the top number)
- Which column has **Diastolic BP** (the bottom number)

Use the dropdown menus if the app guessed wrong.

#### Step 4: Click "Continue"
The app will analyze all patients automatically.

#### Step 5: Export Results
- Click **"Export to Excel"** to save results
- Give the file to the doctor for review

### What Excel Format Do I Need?

BPM works with **any Excel format**! Your spreadsheet just needs columns for:

| Required | Example Column Names |
|----------|---------------------|
| Patient ID | "Patient ID", "MRN", "Subject", "ID" |
| Date/Time | "Date", "Time", "DateTime", "Timestamp" |
| Systolic BP | "SBP", "Systolic", "Sys", "Upper" |
| Diastolic BP | "DBP", "Diastolic", "Dia", "Lower" |

**Optional:** Heart Rate, Notes

### Example Input Data

| Patient_ID | Date | Time | SBP | DBP | HR |
|------------|------|------|-----|-----|----|
| P001 | 2024-01-15 | 08:00 | 142 | 88 | 72 |
| P001 | 2024-01-15 | 12:00 | 138 | 85 | 68 |
| P001 | 2024-01-15 | 18:00 | 145 | 90 | 75 |
| P002 | 2024-01-15 | 09:30 | 128 | 82 | 65 |

---

## Installation

### Option 1: Download Ready-to-Use App (Recommended)

**Windows:**
1. Download `BPM-Windows.zip`
2. Extract the folder
3. Double-click `BPM.exe`

**macOS:**
1. Download `BPM-macOS.dmg`
2. Drag BPM to Applications
3. Double-click to run

### Option 2: Run with Python

```bash
# Clone the repository
git clone https://github.com/yourusername/BPM.git
cd BPM

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/main.py
```

### Option 3: Run with Docker

```bash
# Build the image
docker build -t bpm .

# Run with GUI (Linux with X11)
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/data:/app/data \
    bpm

# Run with GUI (macOS with XQuartz)
xhost +localhost
docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -v $(pwd)/data:/app/data \
    bpm

# Run with GUI (Windows with VcXsrv)
docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -v ${PWD}/data:/app/data \
    bpm
```

Or use Docker Compose:
```bash
docker-compose up
```

---

## Technical Details

### Architecture

```
BPM/
├── src/
│   ├── main.py              # Application entry point
│   ├── analysis/
│   │   └── metrics.py       # BP variability calculations
│   ├── io/
│   │   └── excel_reader.py  # Flexible Excel parser
│   └── ui/
│       ├── main_window.py   # PySide6 GUI
│       └── styles.qss       # Apple-style theming
├── Dockerfile               # Docker containerization
├── docker-compose.yml       # Docker Compose config
└── requirements.txt         # Python dependencies
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI Framework | PySide6 (Qt 6) |
| Data Processing | Pandas, NumPy |
| Statistics | SciPy |
| Excel I/O | openpyxl |
| Charts | Matplotlib, Plotly |
| PDF Reports | ReportLab |

### Metrics Formulas

**Standard Deviation (SD):**
```
SD = √[Σ(xi - x̄)² / (n-1)]
```

**Coefficient of Variation (CV):**
```
CV = (SD / Mean) × 100%
```

**Average Real Variability (ARV):**
```
ARV = Σ|BP[i+1] - BP[i]| / (n-1)
```

**Weighted SD:**
```
Weighted_SD = (SD_day × hours_day + SD_night × hours_night) / 24
```

**Nocturnal Dipping:**
```
Dipping% = ((Mean_day - Mean_night) / Mean_day) × 100
```

### Time Period Definitions

- **Daytime:** 08:00 - 22:00
- **Nighttime:** 00:00 - 06:00
- **Morning:** First 2 hours of daytime

### Data Privacy

- **100% Local Processing** - Your data never leaves your computer
- **No Cloud** - No internet connection required
- **No Telemetry** - We don't collect any usage data
- **Open Source** - Audit the code yourself

---

## Building from Source

### Native Build (PyInstaller)

```bash
# Install PyInstaller
pip install pyinstaller

# Build for your platform
pyinstaller --name BPM \
    --windowed \
    --onefile \
    --icon=resources/icons/app.ico \
    src/main.py
```

### Docker Build

```bash
docker build -t bpm:latest .
```

---

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/BPM.git
cd BPM
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/

# Run the app
python src/main.py
```

---

## License

MIT License - See LICENSE file for details.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/BPM/issues)
- **Documentation:** [Wiki](https://github.com/yourusername/BPM/wiki)

---

<p align="center">
  Made with ❤️ for better cardiovascular care
</p>
