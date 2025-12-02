"""
BPM Main Window

Apple-style wizard interface for BP data analysis.
Bilingual support: English and Turkish.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QFileDialog, QTableWidget,
    QTableWidgetItem, QComboBox, QProgressBar, QMessageBox,
    QHeaderView, QScrollArea, QSplitter, QTextEdit, QApplication,
    QMenu, QToolButton
)
from PySide6.QtCore import Qt, Signal, QThread, QSize, QLocale
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon, QAction

import pandas as pd

# Import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from io.excel_reader import ExcelReader, ColumnType, DataPreview
from io.report_generator import PDFReportGenerator
from analysis.metrics import BPMetricsCalculator, VariabilityMetrics
from core.translations import tr, Translator, Language


class AnalysisWorker(QThread):
    """Worker thread for running analysis without blocking UI"""

    progress = Signal(int, str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, excel_reader, calculator, mapping, normalized_data=None):
        super().__init__()
        self.excel_reader = excel_reader
        self.calculator = calculator
        self.mapping = mapping
        self.normalized_data = normalized_data

    def run(self):
        try:
            self.progress.emit(10, tr("applying_mapping"))

            # Apply mapping if not already done
            if self.normalized_data is None:
                self.normalized_data = self.excel_reader.apply_mapping(self.mapping)

            self.progress.emit(30, tr("calculating_metrics"))

            # Determine patient column
            patient_col = 'patient_id' if 'patient_id' in self.normalized_data.columns else None

            # Calculate metrics
            results = self.calculator.calculate_all_metrics(
                self.normalized_data,
                sbp_col='sbp',
                dbp_col='dbp',
                time_col='datetime' if 'datetime' in self.normalized_data.columns else None,
                patient_col=patient_col
            )

            self.progress.emit(100, tr("analysis_complete"))
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


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
        self.icon_label = QLabel("📁")
        self.icon_label.setFont(QFont("", 48))
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.title = QLabel(tr("drop_title"))
        self.title.setProperty("class", "section-header")
        self.title.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel(tr("drop_subtitle"))
        self.subtitle.setProperty("class", "subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)

        self.formats = QLabel(tr("drop_formats"))
        self.formats.setProperty("class", "caption")
        self.formats.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addSpacing(8)
        layout.addWidget(self.formats)

    def update_translations(self):
        """Update all translatable text"""
        self.title.setText(tr("drop_title"))
        self.subtitle.setText(tr("drop_subtitle"))
        self.formats.setText(tr("drop_formats"))

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
                    self, tr("invalid_file"),
                    tr("invalid_file_msg")
                )

    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("select_bp_file"),
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
        self.field_labels: Dict[str, QLabel] = {}

    def set_preview(self, preview: DataPreview):
        """Set up column mapper from data preview"""
        self.column_names = preview.columns

        # Clear existing layout
        if self.layout():
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout(self)

        # Header
        self.header = QLabel(tr("map_columns"))
        self.header.setProperty("class", "section-header")
        layout.addWidget(self.header)

        self.desc = QLabel(tr("map_desc"))
        self.desc.setProperty("class", "subtitle")
        self.desc.setWordWrap(True)
        layout.addWidget(self.desc)

        layout.addSpacing(16)

        # Create mapping rows
        fields = [
            (ColumnType.PATIENT_ID, "col_patient_id", "tip_patient_id"),
            (ColumnType.DATETIME, "col_datetime", "tip_datetime"),
            (ColumnType.DATE, "col_date", "tip_date"),
            (ColumnType.TIME, "col_time", "tip_time"),
            (ColumnType.SBP, "col_sbp", "tip_sbp"),
            (ColumnType.DBP, "col_dbp", "tip_dbp"),
            (ColumnType.HEART_RATE, "col_heart_rate", "tip_heart_rate"),
        ]

        # Create detection map
        detected = {m.source_column: m.target_type for m in preview.detected_mappings}
        reverse_detected = {}
        for col, col_type in detected.items():
            if col_type not in reverse_detected:
                reverse_detected[col_type] = col

        self.field_labels = {}
        for col_type, label_key, tooltip_key in fields:
            row = QHBoxLayout()

            field_label = QLabel(tr(label_key))
            field_label.setFixedWidth(140)
            field_label.setToolTip(tr(tooltip_key))
            self.field_labels[label_key] = field_label

            combo = QComboBox()
            combo.addItem(tr("not_mapped"), None)
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

            self.issues_header = QLabel("⚠️ " + tr("data_quality_notes"))
            self.issues_header.setProperty("class", "status-warning")
            issues_layout.addWidget(self.issues_header)

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
        self.header = QLabel(tr("results_title"))
        self.header.setProperty("class", "title")
        layout.addWidget(self.header)

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

        self.export_excel_btn = QPushButton(tr("btn_export_excel"))
        self.export_excel_btn.setProperty("class", "secondary")

        self.export_pdf_btn = QPushButton(tr("btn_export_pdf"))

        btn_layout.addWidget(self.export_excel_btn)
        btn_layout.addWidget(self.export_pdf_btn)
        layout.addLayout(btn_layout)

    def update_translations(self):
        """Update all translatable text"""
        self.header.setText(tr("results_title"))
        self.export_excel_btn.setText(tr("btn_export_excel"))
        self.export_pdf_btn.setText(tr("btn_export_pdf"))

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
                (tr("patients"), str(len(results)), "#007AFF"),
                (tr("avg_sbp"), f"{first_result.mean_sbp:.0f}", "#34C759"),
                (tr("avg_dbp"), f"{first_result.mean_dbp:.0f}", "#5856D6"),
                (tr("readings"), str(first_result.reading_count), "#FF9500"),
            ]

            for title, value, color in cards_data:
                card = self._create_metric_card(title, value, color)
                self.summary_layout.addWidget(card)

            self.summary_layout.addStretch()

        # Table headers (translated)
        columns = [
            tr("tbl_patient_id"), tr("tbl_readings"), tr("tbl_mean_sbp"), tr("tbl_mean_dbp"),
            tr("tbl_sd_sbp"), tr("tbl_sd_dbp"), tr("tbl_cv_sbp"), tr("tbl_cv_dbp"),
            tr("tbl_arv_sbp"), tr("tbl_arv_dbp"), tr("tbl_dipping"), tr("tbl_classification")
        ]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(results))

        # Get locale for number formatting
        locale = QLocale(QLocale.Turkish, QLocale.Turkey) if Translator.get_language() == Language.TURKISH else QLocale(QLocale.English, QLocale.UnitedStates)

        for row, (patient_id, metrics) in enumerate(results.items()):
            values = [
                patient_id,
                str(metrics.reading_count),
                locale.toString(metrics.mean_sbp, 'f', 1),
                locale.toString(metrics.mean_dbp, 'f', 1),
                locale.toString(metrics.sd_sbp, 'f', 2),
                locale.toString(metrics.sd_dbp, 'f', 2),
                locale.toString(metrics.cv_sbp, 'f', 1),
                locale.toString(metrics.cv_dbp, 'f', 1),
                locale.toString(metrics.arv_sbp, 'f', 2),
                locale.toString(metrics.arv_dbp, 'f', 2),
                locale.toString(metrics.dipping_percentage, 'f', 1) if metrics.dipping_percentage else "N/A",
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
        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(1000, 700)

        # Data
        self.excel_reader = ExcelReader()
        self.calculator = BPMetricsCalculator()
        self.pdf_generator = PDFReportGenerator()
        self.preview: Optional[DataPreview] = None
        self.normalized_data: Optional[pd.DataFrame] = None
        self.results: Optional[Dict[str, VariabilityMetrics]] = None
        self.analysis_worker: Optional[AnalysisWorker] = None

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

        self.title_label = QLabel(tr("app_title"))
        self.title_label.setProperty("class", "title")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Language selector
        self.lang_btn = QToolButton()
        self.lang_btn.setText("🌐")
        self.lang_btn.setToolTip(tr("language"))
        self.lang_btn.setPopupMode(QToolButton.InstantPopup)

        lang_menu = QMenu(self)
        self.action_english = QAction("English", self)
        self.action_english.setCheckable(True)
        self.action_english.triggered.connect(lambda: self.change_language(Language.ENGLISH))

        self.action_turkish = QAction("Türkçe", self)
        self.action_turkish.setCheckable(True)
        self.action_turkish.triggered.connect(lambda: self.change_language(Language.TURKISH))

        # Set initial check state
        if Translator.get_language() == Language.TURKISH:
            self.action_turkish.setChecked(True)
        else:
            self.action_english.setChecked(True)

        lang_menu.addAction(self.action_english)
        lang_menu.addAction(self.action_turkish)
        self.lang_btn.setMenu(lang_menu)
        header_layout.addWidget(self.lang_btn)

        # Step indicator
        self.step_label = QLabel(tr("step_of", current=1, total=4))
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

        self.back_btn = QPushButton(tr("btn_back"))
        self.back_btn.setProperty("class", "secondary")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()

        self.next_btn = QPushButton(tr("btn_continue"))
        self.next_btn.clicked.connect(self.go_next)
        self.next_btn.setEnabled(False)

        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

    def change_language(self, language: Language):
        """Change application language"""
        Translator.set_language(language)

        # Update check states
        self.action_english.setChecked(language == Language.ENGLISH)
        self.action_turkish.setChecked(language == Language.TURKISH)

        # Update all UI text
        self.update_translations()

    def update_translations(self):
        """Update all translatable text in the UI"""
        self.setWindowTitle(tr("app_title"))
        self.title_label.setText(tr("app_title"))
        self.lang_btn.setToolTip(tr("language"))

        # Update step label
        current_step = self.stack.currentIndex() + 1
        self.step_label.setText(tr("step_of", current=current_step, total=4))

        # Update buttons
        if self.stack.currentIndex() == 3:
            self.next_btn.setText(tr("btn_new_analysis"))
        else:
            self.next_btn.setText(tr("btn_continue"))
        self.back_btn.setText(tr("btn_back"))

        # Update drop zone
        self.drop_zone.update_translations()

        # Update welcome text
        self.welcome_title.setText(tr("welcome_title"))
        self.welcome_desc.setText(tr("welcome_desc"))

        # Update processing page
        self.processing_title.setText(tr("analyzing"))
        self.processing_status.setText(tr("calculating_metrics"))

        # Update preview header
        self.preview_header.setText(tr("data_preview"))

        # Update results widget
        self.results_widget.update_translations()

    def _create_upload_page(self):
        """Create file upload page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        # Welcome message
        welcome = QFrame()
        welcome.setProperty("class", "welcome-card")
        welcome_layout = QVBoxLayout(welcome)

        self.welcome_title = QLabel(tr("welcome_title"))
        self.welcome_title.setStyleSheet("font-size: 24px; font-weight: 600;")
        welcome_layout.addWidget(self.welcome_title)

        self.welcome_desc = QLabel(tr("welcome_desc"))
        self.welcome_desc.setWordWrap(True)
        welcome_layout.addWidget(self.welcome_desc)

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

        self.preview_header = QLabel(tr("data_preview"))
        self.preview_header.setProperty("class", "section-header")
        preview_layout.addWidget(self.preview_header)

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

        self.processing_title = QLabel(tr("analyzing"))
        self.processing_title.setProperty("class", "section-header")
        self.processing_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.processing_title)

        self.processing_status = QLabel(tr("calculating_metrics"))
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
                self, tr("file_loaded"),
                tr("loaded_rows", count=self.preview.row_count, filename=Path(file_path).name)
            )

        except Exception as e:
            QMessageBox.critical(self, tr("error"), tr("load_error", error=str(e)))

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
            self.step_label.setText(tr("step_of", current=2, total=4))
            self.progress.setValue(2)

        elif current == 1:  # Mapping -> Processing
            self.stack.setCurrentIndex(2)
            self.next_btn.setVisible(False)
            self.back_btn.setVisible(False)
            self.step_label.setText(tr("step_of", current=3, total=4))
            self.progress.setValue(3)

            # Start processing
            self._run_analysis()

        elif current == 2:  # Processing -> Results
            self.stack.setCurrentIndex(3)
            self.back_btn.setVisible(True)
            self.next_btn.setText(tr("btn_new_analysis"))
            self.next_btn.setVisible(True)
            self.step_label.setText(tr("step_of", current=4, total=4))
            self.progress.setValue(4)

        elif current == 3:  # Results -> Start over
            self.stack.setCurrentIndex(0)
            self.back_btn.setVisible(False)
            self.next_btn.setText(tr("btn_continue"))
            self.next_btn.setEnabled(False)
            self.step_label.setText(tr("step_of", current=1, total=4))
            self.progress.setValue(1)

    def go_back(self):
        """Go to previous wizard page"""
        current = self.stack.currentIndex()

        if current == 1:
            self.stack.setCurrentIndex(0)
            self.back_btn.setVisible(False)
            self.step_label.setText(tr("step_of", current=1, total=4))
            self.progress.setValue(1)

        elif current == 3:
            self.stack.setCurrentIndex(1)
            self.next_btn.setText(tr("btn_continue"))
            self.step_label.setText(tr("step_of", current=2, total=4))
            self.progress.setValue(2)

    def _run_analysis(self):
        """Run BP variability analysis in background thread"""
        # Get mapping
        mapping = self.column_mapper.get_mapping()

        # Update progress bar to determinate mode
        self.processing_progress.setMaximum(100)
        self.processing_progress.setValue(0)

        # Create and start worker thread
        self.analysis_worker = AnalysisWorker(
            self.excel_reader,
            self.calculator,
            mapping
        )
        self.analysis_worker.progress.connect(self._on_analysis_progress)
        self.analysis_worker.finished.connect(self._on_analysis_finished)
        self.analysis_worker.error.connect(self._on_analysis_error)
        self.analysis_worker.start()

    def _on_analysis_progress(self, percent: int, status: str):
        """Handle analysis progress update"""
        self.processing_progress.setValue(percent)
        self.processing_status.setText(status)

    def _on_analysis_finished(self, results: Dict[str, VariabilityMetrics]):
        """Handle analysis completion"""
        self.results = results

        # Get normalized data from worker
        if self.analysis_worker:
            self.normalized_data = self.analysis_worker.normalized_data

        # Display results
        self.results_widget.display_results(self.results)

        # Reset progress bar to indeterminate for next time
        self.processing_progress.setMaximum(0)

        # Go to results page
        self.go_next()

    def _on_analysis_error(self, error_msg: str):
        """Handle analysis error"""
        # Reset progress bar
        self.processing_progress.setMaximum(0)

        QMessageBox.critical(self, tr("error"), tr("analysis_error", error=error_msg))
        self.stack.setCurrentIndex(1)
        self.back_btn.setVisible(True)
        self.next_btn.setVisible(True)

    def _export_excel(self):
        """Export results to Excel"""
        if not self.results:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, tr("export_results"), "kb_analiz_sonuclari.xlsx",
            "Excel Files (*.xlsx)"
        )

        if file_path:
            try:
                # Get locale for number formatting
                is_turkish = Translator.get_language() == Language.TURKISH

                # Convert results to DataFrame with translated headers
                rows = []
                for patient_id, metrics in self.results.items():
                    row = {
                        tr('excel_patient_id'): patient_id,
                        tr('excel_reading_count'): metrics.reading_count,
                        tr('excel_mean_sbp'): metrics.mean_sbp,
                        tr('excel_mean_dbp'): metrics.mean_dbp,
                        tr('excel_min_sbp'): metrics.min_sbp,
                        tr('excel_max_sbp'): metrics.max_sbp,
                        tr('excel_min_dbp'): metrics.min_dbp,
                        tr('excel_max_dbp'): metrics.max_dbp,
                        tr('excel_sd_sbp'): metrics.sd_sbp,
                        tr('excel_sd_dbp'): metrics.sd_dbp,
                        tr('excel_cv_sbp'): metrics.cv_sbp,
                        tr('excel_cv_dbp'): metrics.cv_dbp,
                        tr('excel_arv_sbp'): metrics.arv_sbp,
                        tr('excel_arv_dbp'): metrics.arv_dbp,
                        tr('excel_weighted_sd_sbp'): metrics.weighted_sd_sbp,
                        tr('excel_weighted_sd_dbp'): metrics.weighted_sd_dbp,
                        tr('excel_pulse_pressure'): metrics.pulse_pressure_mean,
                        tr('excel_dipping'): metrics.dipping_percentage,
                        tr('excel_dipping_status'): metrics.dipping_status.value if metrics.dipping_status else None,
                        tr('excel_bp_class'): metrics.mean_bp_classification.value if metrics.mean_bp_classification else None,
                    }
                    rows.append(row)

                df = pd.DataFrame(rows)
                df.to_excel(file_path, index=False)

                QMessageBox.information(self, tr("export_complete"), tr("results_saved", path=file_path))

            except Exception as e:
                QMessageBox.critical(self, tr("error"), tr("export_error", error=str(e)))

    def _export_pdf(self):
        """Export results to PDF"""
        if not self.results:
            return

        is_turkish = Translator.get_language() == Language.TURKISH
        default_name = "kb_analiz_raporu.pdf" if is_turkish else "bp_analysis_report.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self, tr("export_results"), default_name,
            "PDF Files (*.pdf)"
        )

        if file_path:
            try:
                self.pdf_generator.generate_cohort_report(
                    self.results,
                    file_path
                )
                QMessageBox.information(
                    self, tr("export_complete"),
                    tr("results_saved", path=file_path)
                )
            except Exception as e:
                QMessageBox.critical(
                    self, tr("error"),
                    tr("export_error", error=str(e))
                )
