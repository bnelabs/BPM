"""
Flexible Excel Reader for BP Data

Handles variable Excel formats with intelligent column detection
and user-assisted column mapping.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re


class ColumnType(Enum):
    """Expected column types for BP data"""
    PATIENT_ID = "patient_id"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    SBP = "sbp"
    DBP = "dbp"
    HEART_RATE = "heart_rate"
    NOTES = "notes"
    IGNORE = "ignore"


@dataclass
class ColumnMapping:
    """Mapping between source column and target type"""
    source_column: str
    target_type: ColumnType
    confidence: float  # 0-1 confidence in auto-detection


@dataclass
class DataPreview:
    """Preview of loaded data for user verification"""
    columns: List[str]
    sample_rows: pd.DataFrame  # First N rows
    row_count: int
    detected_mappings: List[ColumnMapping]
    issues: List[str]


class ExcelReader:
    """
    Flexible Excel reader with intelligent column detection.

    Features:
    - Auto-detects common column names
    - Suggests mappings with confidence scores
    - Allows manual override
    - Handles multiple date/time formats
    - Validates data quality
    """

    # Common column name patterns (case-insensitive regex)
    COLUMN_PATTERNS = {
        ColumnType.PATIENT_ID: [
            r'patient.*id', r'id', r'mrn', r'subject', r'hasta.*no',
            r'participant', r'record.*id', r'case.*id'
        ],
        ColumnType.DATE: [
            r'^date$', r'measurement.*date', r'reading.*date', r'visit.*date',
            r'tarih', r'datum'
        ],
        ColumnType.TIME: [
            r'^time$', r'measurement.*time', r'reading.*time', r'saat'
        ],
        ColumnType.DATETIME: [
            r'datetime', r'timestamp', r'date.*time', r'when'
        ],
        ColumnType.SBP: [
            r'sbp', r'systolic', r'sys', r'sistolik', r'upper',
            r'systolic.*bp', r'sys.*pressure'
        ],
        ColumnType.DBP: [
            r'dbp', r'diastolic', r'dia', r'diastolik', r'lower',
            r'diastolic.*bp', r'dia.*pressure'
        ],
        ColumnType.HEART_RATE: [
            r'hr', r'heart.*rate', r'pulse', r'bpm', r'nabiz', r'kalp'
        ],
        ColumnType.NOTES: [
            r'note', r'comment', r'remark', r'observation', r'not'
        ]
    }

    def __init__(self):
        self.raw_data: Optional[pd.DataFrame] = None
        self.file_path: Optional[Path] = None
        self.mappings: Dict[str, ColumnType] = {}

    def load_file(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        preview_rows: int = 10
    ) -> DataPreview:
        """
        Load Excel file and return preview with auto-detected mappings.

        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet to load (None = first sheet)
            preview_rows: Number of rows to include in preview

        Returns:
            DataPreview with columns, sample data, and detected mappings
        """
        self.file_path = Path(file_path)

        # Determine file type and load
        if self.file_path.suffix.lower() in ['.xlsx', '.xls']:
            self.raw_data = pd.read_excel(
                file_path,
                sheet_name=sheet_name or 0,
                engine='openpyxl' if self.file_path.suffix == '.xlsx' else None
            )
        elif self.file_path.suffix.lower() == '.csv':
            self.raw_data = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {self.file_path.suffix}")

        # Clean column names
        self.raw_data.columns = [
            str(col).strip() for col in self.raw_data.columns
        ]

        # Auto-detect column mappings
        detected = self._auto_detect_columns()

        # Validate data and find issues
        issues = self._validate_data(detected)

        return DataPreview(
            columns=list(self.raw_data.columns),
            sample_rows=self.raw_data.head(preview_rows),
            row_count=len(self.raw_data),
            detected_mappings=detected,
            issues=issues
        )

    def _auto_detect_columns(self) -> List[ColumnMapping]:
        """Auto-detect column types based on name patterns and content."""
        mappings = []

        for col in self.raw_data.columns:
            col_lower = col.lower().strip()
            best_match: Optional[ColumnType] = None
            best_confidence = 0.0

            # Try pattern matching on column name
            for col_type, patterns in self.COLUMN_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, col_lower):
                        confidence = 0.8  # High confidence for name match
                        if confidence > best_confidence:
                            best_match = col_type
                            best_confidence = confidence
                        break

            # If no name match, try content analysis
            if best_match is None:
                content_match, content_conf = self._analyze_column_content(col)
                if content_match:
                    best_match = content_match
                    best_confidence = content_conf

            # Default to IGNORE if no match
            if best_match is None:
                best_match = ColumnType.IGNORE
                best_confidence = 0.0

            mappings.append(ColumnMapping(
                source_column=col,
                target_type=best_match,
                confidence=best_confidence
            ))

        return mappings

    def _analyze_column_content(
        self,
        column: str
    ) -> Tuple[Optional[ColumnType], float]:
        """Analyze column content to guess type."""
        sample = self.raw_data[column].dropna().head(100)

        if len(sample) == 0:
            return None, 0.0

        # Check if numeric
        if pd.api.types.is_numeric_dtype(sample):
            values = sample.values
            mean_val = np.mean(values)
            min_val = np.min(values)
            max_val = np.max(values)

            # SBP typically 80-220
            if 80 <= mean_val <= 200 and min_val >= 50 and max_val <= 250:
                # Could be SBP or DBP, check range
                if mean_val > 100:
                    return ColumnType.SBP, 0.5
                else:
                    return ColumnType.DBP, 0.5

            # Heart rate typically 40-200
            if 40 <= mean_val <= 120 and min_val >= 30 and max_val <= 220:
                return ColumnType.HEART_RATE, 0.4

        # Check if datetime-like
        try:
            parsed = pd.to_datetime(sample, errors='coerce')
            valid_ratio = parsed.notna().sum() / len(sample)
            if valid_ratio > 0.8:
                # Check if has time component
                if parsed.dropna().dt.time.nunique() > 1:
                    return ColumnType.DATETIME, 0.7
                else:
                    return ColumnType.DATE, 0.6
        except:
            pass

        return None, 0.0

    def _validate_data(self, mappings: List[ColumnMapping]) -> List[str]:
        """Validate data quality and return list of issues."""
        issues = []

        mapping_dict = {m.source_column: m.target_type for m in mappings}

        # Check for required columns
        required = {ColumnType.SBP, ColumnType.DBP}
        found = set(mapping_dict.values())

        missing = required - found
        if missing:
            issues.append(f"Missing required columns: {[m.value for m in missing]}")

        # Check for date/time
        has_datetime = ColumnType.DATETIME in found
        has_date = ColumnType.DATE in found
        has_time = ColumnType.TIME in found

        if not has_datetime and not has_date:
            issues.append("No date/time column detected - temporal analysis limited")

        # Check data quality for BP columns
        for mapping in mappings:
            if mapping.target_type == ColumnType.SBP:
                sbp = self.raw_data[mapping.source_column]
                null_count = sbp.isna().sum()
                if null_count > 0:
                    issues.append(f"SBP has {null_count} missing values")

                # Check for outliers
                if pd.api.types.is_numeric_dtype(sbp):
                    outliers = ((sbp < 50) | (sbp > 300)).sum()
                    if outliers > 0:
                        issues.append(f"SBP has {outliers} potential outliers (<50 or >300)")

            elif mapping.target_type == ColumnType.DBP:
                dbp = self.raw_data[mapping.source_column]
                null_count = dbp.isna().sum()
                if null_count > 0:
                    issues.append(f"DBP has {null_count} missing values")

                if pd.api.types.is_numeric_dtype(dbp):
                    outliers = ((dbp < 30) | (dbp > 200)).sum()
                    if outliers > 0:
                        issues.append(f"DBP has {outliers} potential outliers (<30 or >200)")

        return issues

    def apply_mapping(
        self,
        mappings: Dict[str, ColumnType]
    ) -> pd.DataFrame:
        """
        Apply column mappings and return normalized DataFrame.

        Args:
            mappings: Dict of {source_column: target_type}

        Returns:
            Normalized DataFrame with standard column names
        """
        if self.raw_data is None:
            raise ValueError("No data loaded. Call load_file first.")

        self.mappings = mappings

        # Create normalized dataframe
        result = pd.DataFrame()

        for source_col, target_type in mappings.items():
            if target_type == ColumnType.IGNORE:
                continue

            if source_col not in self.raw_data.columns:
                continue

            target_col = target_type.value
            result[target_col] = self.raw_data[source_col].copy()

        # Combine date + time if separate
        if 'date' in result.columns and 'time' in result.columns:
            result['datetime'] = pd.to_datetime(
                result['date'].astype(str) + ' ' + result['time'].astype(str),
                errors='coerce'
            )
            result.drop(['date', 'time'], axis=1, inplace=True)
        elif 'date' in result.columns and 'datetime' not in result.columns:
            result['datetime'] = pd.to_datetime(result['date'], errors='coerce')
            result.drop('date', axis=1, inplace=True)
        elif 'datetime' in result.columns:
            result['datetime'] = pd.to_datetime(result['datetime'], errors='coerce')

        # Convert BP columns to numeric
        for col in ['sbp', 'dbp', 'heart_rate']:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce')

        return result

    def get_sheet_names(self, file_path: str) -> List[str]:
        """Get list of sheet names in Excel file."""
        try:
            xl = pd.ExcelFile(file_path)
            return xl.sheet_names
        except Exception:
            return []


def create_sample_template() -> pd.DataFrame:
    """
    Create a sample Excel template showing expected format.

    Returns DataFrame that can be saved as example template.
    """
    np.random.seed(42)

    # Generate sample data for 5 patients, 10 readings each
    data = []
    for patient_id in range(1, 6):
        base_sbp = np.random.randint(110, 150)
        base_dbp = np.random.randint(70, 95)

        for reading in range(10):
            timestamp = pd.Timestamp('2024-01-01') + pd.Timedelta(hours=reading * 2)
            data.append({
                'Patient_ID': f'P{patient_id:03d}',
                'Date': timestamp.date(),
                'Time': timestamp.time(),
                'SBP': base_sbp + np.random.randint(-15, 15),
                'DBP': base_dbp + np.random.randint(-10, 10),
                'Heart_Rate': np.random.randint(60, 90),
                'Notes': ''
            })

    return pd.DataFrame(data)
