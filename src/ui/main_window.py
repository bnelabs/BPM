"""
BPM Main Window

Apple-style wizard interface for BP data analysis.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QFileDialog, QTableWidget,
    QTableWidgetItem, QComboBox, QProgressBar, QMessageBox,
    QHeaderView, QScrollArea, QSplitter, QTextEdit, QApplication
)
from PySide6.QtCore import Qt, Signal, QThread, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon

import pandas as pd

# Import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from io.excel_reader import ExcelReader, ColumnType, DataPreview
from analysis.metrics import BPMetricsCalculator, VariabilityMetrics


class DropZone(QFrame):
    """File drop zone widget"""

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setProperty("class", "drop-zone")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Icon placeholder
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("", 48))
        icon_label.setAlignment(Qt.AlignCenter)

        title = QLabel("Drop your Excel file here")
        title.setProperty("class", "section-header")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("or click to browse")
        subtitle.setProperty("class", "subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        formats = QLabel("Supports .xlsx, .xls, .csv")
        formats.setProperty("class", "caption")
        formats.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(formats)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("class", "drop-zone-active")
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("class", "drop-zone")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("class", "drop-zone")
        self.style().unpolish(self)
        self.style().polish(self)

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.xlsx', '.xls', '.csv')):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(
                    self, "Invalid File",
                    "Please select an Excel file (.xlsx, .xls) or CSV file."
                )

    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select BP Data File",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_dropped.emit(file_path)


class ColumnMapperWidget(QWidget):
    """Widget for mapping Excel columns to BP data fields"""

    mapping_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.combos: Dict[str, QComboBox] = {}
        self.column_names: List[str] = []

    def set_preview(self, preview: DataPreview):
        """Set up column mapper from data preview"""
        self.column_names = preview.columns

        # Clear existing layout
        if self.layout():
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Map Your Columns")
        header.setProperty("class", "section-header")
        layout.addWidget(header)

        desc = QLabel(
            "Match your Excel columns to the required data fields. "
            "We've auto-detected some - please verify."
        )
        desc.setProperty("class", "subtitle")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(16)

        # Create mapping rows
        fields = [
            (ColumnType.PATIENT_ID, "Patient ID", "Unique identifier for each patient"),
            (ColumnType.DATETIME, "Date/Time", "When the reading was taken"),
            (ColumnType.DATE, "Date Only", "If date and time are separate"),
            (ColumnType.TIME, "Time Only", "If date and time are separate"),
            (ColumnType.SBP, "Systolic BP *", "Required - upper BP number (mmHg)"),
            (ColumnType.DBP, "Diastolic BP *", "Required - lower BP number (mmHg)"),
            (ColumnType.HEART_RATE, "Heart Rate", "Optional - beats per minute"),
        ]

        # Create detection map
        detected = {m.source_column: m.target_type for m in preview.detected_mappings}
        reverse_detected = {}
        for col, col_type in detected.items():
            if col_type not in reverse_detected:
                reverse_detected[col_type] = col

        for col_type, label, tooltip in fields:
            row = QHBoxLayout()

            field_label = QLabel(label)
            field_label.setFixedWidth(120)
            field_label.setToolTip(tooltip)

            combo = QComboBox()
            combo.addItem("-- Not mapped --", None)
            for col in self.column_names:
                combo.addItem(col, col)

            # Set detected value
            if col_type in reverse_detected:
                idx = combo.findData(reverse_detected[col_type])
                if idx >= 0:
                    combo.setCurrentIndex(idx)

            combo.currentIndexChanged.connect(self._on_mapping_changed)
            self.combos[col_type.value] = combo

            row.addWidget(field_label)
            row.addWidget(combo, 1)
            layout.addLayout(row)

        layout.addStretch()

        # Show issues if any
        if preview.issues:
            issues_frame = QFrame()
            issues_frame.setProperty("class", "card")
            issues_layout = QVBoxLayout(issues_frame)

            issues_header = QLabel("⚠️ Data Quality Notes")
            issues_header.setProperty("class", "status-warning")
            issues_layout.addWidget(issues_header)

            for issue in preview.issues:
                issue_label = QLabel(f"• {issue}")
                issue_label.setWordWrap(True)
                issues_layout.addWidget(issue_label)

            layout.addWidget(issues_frame)

    def _on_mapping_changed(self):
        self.mapping_changed.emit(self.get_mapping())

    def get_mapping(self) -> Dict[str, ColumnType]:
        """Get current column mapping"""
        mapping = {}
        for col_type_str, combo in self.combos.items():
            source_col = combo.currentData()
            if source_col:
                col_type = ColumnType(col_type_str)
                mapping[source_col] = col_type
        return mapping


class ResultsWidget(QWidget):
    """Widget to display analysis results"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Analysis Results")
        header.setProperty("class", "title")
        layout.addWidget(header)

        # Summary cards
        self.summary_layout = QHBoxLayout()
        layout.addLayout(self.summary_layout)

        # Results table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Export buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.export_excel_btn = QPushButton("Export to Excel")
        self.export_excel_btn.setProperty("class", "secondary")

        self.export_pdf_btn = QPushButton("Export PDF Report")

        btn_layout.addWidget(self.export_excel_btn)
        btn_layout.addWidget(self.export_pdf_btn)
        layout.addLayout(btn_layout)

    def display_results(self, results: Dict[str, VariabilityMetrics]):
        """Display analysis results in table"""
        # Clear existing
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Summary cards
        if results:
            first_result = list(results.values())[0]

            cards_data = [
                ("Patients", str(len(results)), "#007AFF"),
                ("Avg SBP", f"{first_result.mean_sbp:.0f}", "#34C759"),
                ("Avg DBP", f"{first_result.mean_dbp:.0f}", "#5856D6"),
                ("Readings", str(first_result.reading_count), "#FF9500"),
            ]

            for title, value, color in cards_data:
                card = self._create_metric_card(title, value, color)
                self.summary_layout.addWidget(card)

            self.summary_layout.addStretch()

        # Table
        columns = [
            "Patient ID", "Readings", "Mean SBP", "Mean DBP",
            "SD SBP", "SD DBP", "CV SBP%", "CV DBP%",
            "ARV SBP", "ARV DBP", "Dipping %", "Classification"
        ]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(results))

        for row, (patient_id, metrics) in enumerate(results.items()):
            values = [
                patient_id,
                str(metrics.reading_count),
                f"{metrics.mean_sbp:.1f}",
                f"{metrics.mean_dbp:.1f}",
                f"{metrics.sd_sbp:.2f}",
                f"{metrics.sd_dbp:.2f}",
                f"{metrics.cv_sbp:.1f}",
                f"{metrics.cv_dbp:.1f}",
                f"{metrics.arv_sbp:.2f}",
                f"{metrics.arv_dbp:.2f}",
                f"{metrics.dipping_percentage:.1f}" if metrics.dipping_percentage else "N/A",
                metrics.mean_bp_classification.value if metrics.mean_bp_classification else "N/A"
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def _create_metric_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a metric summary card"""
        card = QFrame()
        card.setProperty("class", "metric-card")
        card.setFixedWidth(140)

        layout = QVBoxLayout(card)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setProperty("class", "caption")
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: 600; color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card


class MainWindow(QMainWindow):
    """Main application window with wizard-style workflow"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BPM - Blood Pressure Analysis")
        self.setMinimumSize(1000, 700)

        # Data
        self.excel_reader = ExcelReader()
        self.calculator = BPMetricsCalculator()
        self.preview: Optional[DataPreview] = None
        self.normalized_data: Optional[pd.DataFrame] = None
        self.results: Optional[Dict[str, VariabilityMetrics]] = None

        self.setup_ui()
        self.load_styles()

    def load_styles(self):
        """Load QSS stylesheet"""
        style_path = Path(__file__).parent / "styles.qss"
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())

    def setup_ui(self):
        """Setup the main UI"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Blood Pressure Analysis")
        title.setProperty("class", "title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Step indicator
        self.step_label = QLabel("Step 1 of 4")
        self.step_label.setProperty("class", "subtitle")
        header_layout.addWidget(self.step_label)

        layout.addLayout(header_layout)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(4)
        self.progress.setValue(1)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        layout.addWidget(self.progress)

        # Stacked widget for wizard pages
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # Create pages
        self._create_upload_page()
        self._create_mapping_page()
        self._create_processing_page()
        self._create_results_page()

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.back_btn = QPushButton("Back")
        self.back_btn.setProperty("class", "secondary")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()

        self.next_btn = QPushButton("Continue")
        self.next_btn.clicked.connect(self.go_next)
        self.next_btn.setEnabled(False)

        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

    def _create_upload_page(self):
        """Create file upload page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        # Welcome message
        welcome = QFrame()
        welcome.setProperty("class", "welcome-card")
        welcome_layout = QVBoxLayout(welcome)

        welcome_title = QLabel("Welcome to BPM")
        welcome_title.setStyleSheet("font-size: 24px; font-weight: 600;")
        welcome_layout.addWidget(welcome_title)

        welcome_desc = QLabel(
            "Analyze blood pressure variability from your patient data. "
            "Upload an Excel file to get started."
        )
        welcome_desc.setWordWrap(True)
        welcome_layout.addWidget(welcome_desc)

        layout.addWidget(welcome)
        layout.addSpacing(32)

        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_file_dropped)
        self.drop_zone.setMinimumHeight(250)
        layout.addWidget(self.drop_zone)

        layout.addStretch()
        self.stack.addWidget(page)

    def _create_mapping_page(self):
        """Create column mapping page"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # Splitter for mapper and preview
        splitter = QSplitter(Qt.Horizontal)

        # Column mapper
        self.column_mapper = ColumnMapperWidget()
        self.column_mapper.mapping_changed.connect(self._on_mapping_changed)

        mapper_scroll = QScrollArea()
        mapper_scroll.setWidget(self.column_mapper)
        mapper_scroll.setWidgetResizable(True)
        splitter.addWidget(mapper_scroll)

        # Data preview
        preview_frame = QFrame()
        preview_frame.setProperty("class", "card")
        preview_layout = QVBoxLayout(preview_frame)

        preview_header = QLabel("Data Preview")
        preview_header.setProperty("class", "section-header")
        preview_layout.addWidget(preview_header)

        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        preview_layout.addWidget(self.preview_table)

        splitter.addWidget(preview_frame)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)
        self.stack.addWidget(page)

    def _create_processing_page(self):
        """Create processing page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("⚙️")
        icon.setFont(QFont("", 64))
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Analyzing Your Data")
        title.setProperty("class", "section-header")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.processing_status = QLabel("Calculating BP variability metrics...")
        self.processing_status.setProperty("class", "subtitle")
        self.processing_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.processing_status)

        self.processing_progress = QProgressBar()
        self.processing_progress.setMinimum(0)
        self.processing_progress.setMaximum(0)  # Indeterminate
        self.processing_progress.setFixedWidth(300)
        layout.addWidget(self.processing_progress, alignment=Qt.AlignCenter)

        layout.addStretch()
        self.stack.addWidget(page)

    def _create_results_page(self):
        """Create results page"""
        self.results_widget = ResultsWidget()
        self.results_widget.export_excel_btn.clicked.connect(self._export_excel)
        self.results_widget.export_pdf_btn.clicked.connect(self._export_pdf)
        self.stack.addWidget(self.results_widget)

    def _on_file_dropped(self, file_path: str):
        """Handle file drop/selection"""
        try:
            self.preview = self.excel_reader.load_file(file_path)

            # Update preview table
            self.preview_table.setRowCount(len(self.preview.sample_rows))
            self.preview_table.setColumnCount(len(self.preview.columns))
            self.preview_table.setHorizontalHeaderLabels(self.preview.columns)

            for row_idx, row in self.preview.sample_rows.iterrows():
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if pd.notna(value) else "")
                    self.preview_table.setItem(row_idx, col_idx, item)

            # Setup column mapper
            self.column_mapper.set_preview(self.preview)

            # Enable next
            self.next_btn.setEnabled(True)

            # Show success
            QMessageBox.information(
                self, "File Loaded",
                f"Loaded {self.preview.row_count} rows from {Path(file_path).name}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def _on_mapping_changed(self, mapping: Dict):
        """Handle column mapping change"""
        # Check if required fields are mapped
        has_sbp = any(t == ColumnType.SBP for t in mapping.values())
        has_dbp = any(t == ColumnType.DBP for t in mapping.values())
        self.next_btn.setEnabled(has_sbp and has_dbp)

    def go_next(self):
        """Go to next wizard page"""
        current = self.stack.currentIndex()

        if current == 0:  # Upload -> Mapping
            self.stack.setCurrentIndex(1)
            self.back_btn.setVisible(True)
            self.step_label.setText("Step 2 of 4")
            self.progress.setValue(2)

        elif current == 1:  # Mapping -> Processing
            self.stack.setCurrentIndex(2)
            self.next_btn.setVisible(False)
            self.back_btn.setVisible(False)
            self.step_label.setText("Step 3 of 4")
            self.progress.setValue(3)

            # Start processing
            self._run_analysis()

        elif current == 2:  # Processing -> Results
            self.stack.setCurrentIndex(3)
            self.back_btn.setVisible(True)
            self.next_btn.setText("New Analysis")
            self.next_btn.setVisible(True)
            self.step_label.setText("Step 4 of 4")
            self.progress.setValue(4)

        elif current == 3:  # Results -> Start over
            self.stack.setCurrentIndex(0)
            self.back_btn.setVisible(False)
            self.next_btn.setText("Continue")
            self.next_btn.setEnabled(False)
            self.step_label.setText("Step 1 of 4")
            self.progress.setValue(1)

    def go_back(self):
        """Go to previous wizard page"""
        current = self.stack.currentIndex()

        if current == 1:
            self.stack.setCurrentIndex(0)
            self.back_btn.setVisible(False)
            self.step_label.setText("Step 1 of 4")
            self.progress.setValue(1)

        elif current == 3:
            self.stack.setCurrentIndex(1)
            self.next_btn.setText("Continue")
            self.step_label.setText("Step 2 of 4")
            self.progress.setValue(2)

    def _run_analysis(self):
        """Run BP variability analysis"""
        try:
            # Get mapping
            mapping = self.column_mapper.get_mapping()

            # Apply mapping
            self.normalized_data = self.excel_reader.apply_mapping(mapping)

            # Determine patient column
            patient_col = 'patient_id' if 'patient_id' in self.normalized_data.columns else None

            # Calculate metrics
            self.results = self.calculator.calculate_all_metrics(
                self.normalized_data,
                sbp_col='sbp',
                dbp_col='dbp',
                time_col='datetime' if 'datetime' in self.normalized_data.columns else None,
                patient_col=patient_col
            )

            # Display results
            self.results_widget.display_results(self.results)

            # Go to results page
            self.go_next()

        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Failed to analyze data:\n{str(e)}")
            self.stack.setCurrentIndex(1)
            self.back_btn.setVisible(True)
            self.next_btn.setVisible(True)

    def _export_excel(self):
        """Export results to Excel"""
        if not self.results:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "bp_analysis_results.xlsx",
            "Excel Files (*.xlsx)"
        )

        if file_path:
            try:
                # Convert results to DataFrame
                rows = []
                for patient_id, metrics in self.results.items():
                    row = {
                        'Patient ID': patient_id,
                        'Reading Count': metrics.reading_count,
                        'Mean SBP': metrics.mean_sbp,
                        'Mean DBP': metrics.mean_dbp,
                        'Min SBP': metrics.min_sbp,
                        'Max SBP': metrics.max_sbp,
                        'Min DBP': metrics.min_dbp,
                        'Max DBP': metrics.max_dbp,
                        'SD SBP': metrics.sd_sbp,
                        'SD DBP': metrics.sd_dbp,
                        'CV SBP (%)': metrics.cv_sbp,
                        'CV DBP (%)': metrics.cv_dbp,
                        'ARV SBP': metrics.arv_sbp,
                        'ARV DBP': metrics.arv_dbp,
                        'Weighted SD SBP': metrics.weighted_sd_sbp,
                        'Weighted SD DBP': metrics.weighted_sd_dbp,
                        'Pulse Pressure': metrics.pulse_pressure_mean,
                        'Dipping (%)': metrics.dipping_percentage,
                        'Dipping Status': metrics.dipping_status.value if metrics.dipping_status else None,
                        'BP Classification': metrics.mean_bp_classification.value if metrics.mean_bp_classification else None,
                    }
                    rows.append(row)

                df = pd.DataFrame(rows)
                df.to_excel(file_path, index=False)

                QMessageBox.information(self, "Export Complete", f"Results saved to:\n{file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")

    def _export_pdf(self):
        """Export results to PDF"""
        QMessageBox.information(
            self, "Coming Soon",
            "PDF export will be implemented in the next version."
        )
