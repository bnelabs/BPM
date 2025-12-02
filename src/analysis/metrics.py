"""
BP Variability Metrics Calculator

Implements all clinically important blood pressure variability indices
based on established methodologies (Grillo et al., J Clin Hypertens 2015).
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DippingStatus(Enum):
    """Nocturnal dipping classification"""
    EXTREME_DIPPER = "Extreme Dipper (>20%)"
    NORMAL_DIPPER = "Normal Dipper (10-20%)"
    NON_DIPPER = "Non-Dipper (<10%)"
    REVERSE_DIPPER = "Reverse Dipper (<0%)"


class HypertensionStage(Enum):
    """BP classification based on AHA/ACC guidelines"""
    NORMAL = "Normal (<120/<80)"
    ELEVATED = "Elevated (120-129/<80)"
    STAGE_1 = "Stage 1 HTN (130-139/80-89)"
    STAGE_2 = "Stage 2 HTN (>=140/>=90)"
    CRISIS = "Hypertensive Crisis (>180/>120)"


@dataclass
class BPReading:
    """Single blood pressure reading"""
    timestamp: pd.Timestamp
    sbp: float  # Systolic BP (mmHg)
    dbp: float  # Diastolic BP (mmHg)
    heart_rate: Optional[float] = None
    patient_id: Optional[str] = None


@dataclass
class VariabilityMetrics:
    """Complete set of BP variability metrics for a patient/period"""
    # Basic statistics
    mean_sbp: float
    mean_dbp: float
    min_sbp: float
    max_sbp: float
    min_dbp: float
    max_dbp: float
    reading_count: int

    # Dispersion measures
    sd_sbp: float
    sd_dbp: float
    cv_sbp: float  # Coefficient of variation
    cv_dbp: float

    # Sequence-based measures
    arv_sbp: float  # Average Real Variability
    arv_dbp: float

    # Weighted measures (if day/night available)
    weighted_sd_sbp: Optional[float] = None
    weighted_sd_dbp: Optional[float] = None

    # Derived indices
    pulse_pressure_mean: Optional[float] = None
    morning_surge: Optional[float] = None
    dipping_percentage: Optional[float] = None
    dipping_status: Optional[DippingStatus] = None

    # Classification
    mean_bp_classification: Optional[HypertensionStage] = None


class BPMetricsCalculator:
    """
    Calculator for blood pressure variability metrics.

    Handles variable time intervals (minutes to days) and
    provides both short-term and long-term variability analysis.
    """

    # Time period definitions (hours)
    DAYTIME_START = 8   # 08:00
    DAYTIME_END = 22    # 22:00
    NIGHTTIME_START = 0  # 00:00
    NIGHTTIME_END = 6    # 06:00

    def __init__(self):
        pass

    def calculate_all_metrics(
        self,
        readings: pd.DataFrame,
        sbp_col: str = 'sbp',
        dbp_col: str = 'dbp',
        time_col: str = 'timestamp',
        patient_col: Optional[str] = None
    ) -> Dict[str, VariabilityMetrics]:
        """
        Calculate all metrics for one or more patients.

        Args:
            readings: DataFrame with BP readings
            sbp_col: Column name for systolic BP
            dbp_col: Column name for diastolic BP
            time_col: Column name for timestamp
            patient_col: Column name for patient ID (if multiple patients)

        Returns:
            Dictionary mapping patient_id -> VariabilityMetrics
        """
        results = {}

        if patient_col and patient_col in readings.columns:
            # Multiple patients
            for patient_id, group in readings.groupby(patient_col):
                metrics = self._calculate_patient_metrics(
                    group, sbp_col, dbp_col, time_col
                )
                results[str(patient_id)] = metrics
        else:
            # Single patient or all data as one
            metrics = self._calculate_patient_metrics(
                readings, sbp_col, dbp_col, time_col
            )
            results['all'] = metrics

        return results

    def _calculate_patient_metrics(
        self,
        df: pd.DataFrame,
        sbp_col: str,
        dbp_col: str,
        time_col: str
    ) -> VariabilityMetrics:
        """Calculate metrics for a single patient's data."""

        # Ensure timestamp is datetime
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col)

        sbp = df[sbp_col].dropna().values
        dbp = df[dbp_col].dropna().values
        timestamps = df[time_col].values

        # Basic statistics
        mean_sbp = np.mean(sbp)
        mean_dbp = np.mean(dbp)

        # Dispersion measures
        sd_sbp = np.std(sbp, ddof=1) if len(sbp) > 1 else 0
        sd_dbp = np.std(dbp, ddof=1) if len(dbp) > 1 else 0

        cv_sbp = (sd_sbp / mean_sbp * 100) if mean_sbp > 0 else 0
        cv_dbp = (sd_dbp / mean_dbp * 100) if mean_dbp > 0 else 0

        # Average Real Variability (ARV)
        arv_sbp = self._calculate_arv(sbp)
        arv_dbp = self._calculate_arv(dbp)

        # Pulse pressure
        pulse_pressure = np.mean(sbp - dbp[:len(sbp)])

        # Try to calculate day/night metrics if we have time info
        weighted_sd_sbp = None
        weighted_sd_dbp = None
        dipping_pct = None
        dipping_status = None
        morning_surge = None

        if len(timestamps) > 0:
            day_night = self._split_day_night(df, time_col, sbp_col, dbp_col)
            if day_night:
                weighted_sd_sbp, weighted_sd_dbp = self._calculate_weighted_sd(day_night)
                dipping_pct = self._calculate_dipping(day_night)
                if dipping_pct is not None:
                    dipping_status = self._classify_dipping(dipping_pct)
                morning_surge = self._calculate_morning_surge(day_night)

        # BP classification
        bp_class = self._classify_bp(mean_sbp, mean_dbp)

        return VariabilityMetrics(
            mean_sbp=round(mean_sbp, 1),
            mean_dbp=round(mean_dbp, 1),
            min_sbp=round(np.min(sbp), 1),
            max_sbp=round(np.max(sbp), 1),
            min_dbp=round(np.min(dbp), 1),
            max_dbp=round(np.max(dbp), 1),
            reading_count=len(sbp),
            sd_sbp=round(sd_sbp, 2),
            sd_dbp=round(sd_dbp, 2),
            cv_sbp=round(cv_sbp, 2),
            cv_dbp=round(cv_dbp, 2),
            arv_sbp=round(arv_sbp, 2),
            arv_dbp=round(arv_dbp, 2),
            weighted_sd_sbp=round(weighted_sd_sbp, 2) if weighted_sd_sbp else None,
            weighted_sd_dbp=round(weighted_sd_dbp, 2) if weighted_sd_dbp else None,
            pulse_pressure_mean=round(pulse_pressure, 1),
            morning_surge=round(morning_surge, 1) if morning_surge else None,
            dipping_percentage=round(dipping_pct, 1) if dipping_pct else None,
            dipping_status=dipping_status,
            mean_bp_classification=bp_class
        )

    @staticmethod
    def _calculate_arv(values: np.ndarray) -> float:
        """
        Calculate Average Real Variability (ARV).

        ARV = sum(|BP[i+1] - BP[i]|) / (n-1)

        This measures the average absolute change between consecutive readings,
        capturing short-term variability better than SD.
        """
        if len(values) < 2:
            return 0.0

        differences = np.abs(np.diff(values))
        return np.mean(differences)

    def _split_day_night(
        self,
        df: pd.DataFrame,
        time_col: str,
        sbp_col: str,
        dbp_col: str
    ) -> Optional[Dict]:
        """Split readings into daytime and nighttime periods."""

        df = df.copy()
        df['hour'] = pd.to_datetime(df[time_col]).dt.hour

        # Daytime: 08:00 - 22:00
        daytime = df[(df['hour'] >= self.DAYTIME_START) &
                     (df['hour'] < self.DAYTIME_END)]

        # Nighttime: 00:00 - 06:00
        nighttime = df[(df['hour'] >= self.NIGHTTIME_START) &
                       (df['hour'] < self.NIGHTTIME_END)]

        if len(daytime) < 2 or len(nighttime) < 2:
            return None

        return {
            'daytime': {
                'sbp': daytime[sbp_col].values,
                'dbp': daytime[dbp_col].values,
                'hours': self.DAYTIME_END - self.DAYTIME_START  # 14 hours
            },
            'nighttime': {
                'sbp': nighttime[sbp_col].values,
                'dbp': nighttime[dbp_col].values,
                'hours': self.NIGHTTIME_END - self.NIGHTTIME_START + 24 - self.DAYTIME_END + self.DAYTIME_START  # ~10 hours
            }
        }

    def _calculate_weighted_sd(self, day_night: Dict) -> Tuple[float, float]:
        """
        Calculate weighted SD (average of day/night SD weighted by hours).

        Weighted SD = (SD_day * hours_day + SD_night * hours_night) / 24
        """
        day = day_night['daytime']
        night = day_night['nighttime']

        sd_day_sbp = np.std(day['sbp'], ddof=1)
        sd_night_sbp = np.std(night['sbp'], ddof=1)
        sd_day_dbp = np.std(day['dbp'], ddof=1)
        sd_night_dbp = np.std(night['dbp'], ddof=1)

        total_hours = day['hours'] + night['hours']

        weighted_sbp = (sd_day_sbp * day['hours'] + sd_night_sbp * night['hours']) / total_hours
        weighted_dbp = (sd_day_dbp * day['hours'] + sd_night_dbp * night['hours']) / total_hours

        return weighted_sbp, weighted_dbp

    def _calculate_dipping(self, day_night: Dict) -> Optional[float]:
        """
        Calculate nocturnal dipping percentage.

        Dipping % = ((Mean_day - Mean_night) / Mean_day) * 100
        """
        day_mean = np.mean(day_night['daytime']['sbp'])
        night_mean = np.mean(day_night['nighttime']['sbp'])

        if day_mean == 0:
            return None

        return ((day_mean - night_mean) / day_mean) * 100

    @staticmethod
    def _classify_dipping(dipping_pct: float) -> DippingStatus:
        """Classify dipping status based on percentage."""
        if dipping_pct < 0:
            return DippingStatus.REVERSE_DIPPER
        elif dipping_pct < 10:
            return DippingStatus.NON_DIPPER
        elif dipping_pct <= 20:
            return DippingStatus.NORMAL_DIPPER
        else:
            return DippingStatus.EXTREME_DIPPER

    def _calculate_morning_surge(self, day_night: Dict) -> Optional[float]:
        """
        Calculate morning surge.

        Morning Surge = Morning SBP (first 2h of daytime) - Lowest nighttime SBP
        """
        night_sbp = day_night['nighttime']['sbp']

        if len(night_sbp) == 0:
            return None

        # Use first daytime readings as "morning"
        day_sbp = day_night['daytime']['sbp']
        if len(day_sbp) == 0:
            return None

        # Morning = average of first few daytime readings
        morning_sbp = np.mean(day_sbp[:max(1, len(day_sbp)//4)])
        lowest_night = np.min(night_sbp)

        return morning_sbp - lowest_night

    @staticmethod
    def _classify_bp(sbp: float, dbp: float) -> HypertensionStage:
        """Classify BP based on AHA/ACC 2017 guidelines."""
        if sbp > 180 or dbp > 120:
            return HypertensionStage.CRISIS
        elif sbp >= 140 or dbp >= 90:
            return HypertensionStage.STAGE_2
        elif sbp >= 130 or dbp >= 80:
            return HypertensionStage.STAGE_1
        elif sbp >= 120:
            return HypertensionStage.ELEVATED
        else:
            return HypertensionStage.NORMAL


def calculate_visit_to_visit_variability(
    visits: pd.DataFrame,
    sbp_col: str = 'sbp',
    dbp_col: str = 'dbp',
    visit_col: str = 'visit_date',
    patient_col: str = 'patient_id'
) -> pd.DataFrame:
    """
    Calculate long-term (visit-to-visit) BP variability.

    For patients with multiple clinic visits over weeks/months,
    this calculates variability across visits rather than within a day.

    Returns DataFrame with per-patient long-term variability metrics.
    """
    results = []

    for patient_id, group in visits.groupby(patient_col):
        group = group.sort_values(visit_col)

        sbp_values = group[sbp_col].values
        dbp_values = group[dbp_col].values

        if len(sbp_values) >= 2:
            result = {
                'patient_id': patient_id,
                'visit_count': len(sbp_values),
                'mean_sbp': np.mean(sbp_values),
                'mean_dbp': np.mean(dbp_values),
                'sd_sbp': np.std(sbp_values, ddof=1),
                'sd_dbp': np.std(dbp_values, ddof=1),
                'cv_sbp': np.std(sbp_values, ddof=1) / np.mean(sbp_values) * 100,
                'cv_dbp': np.std(dbp_values, ddof=1) / np.mean(dbp_values) * 100,
                'arv_sbp': np.mean(np.abs(np.diff(sbp_values))),
                'arv_dbp': np.mean(np.abs(np.diff(dbp_values))),
                'max_sbp': np.max(sbp_values),
                'min_sbp': np.min(sbp_values),
                'range_sbp': np.max(sbp_values) - np.min(sbp_values)
            }
            results.append(result)

    return pd.DataFrame(results)
