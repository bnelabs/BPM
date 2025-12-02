"""
BPM Translations Module

Provides bilingual support for English and Turkish.
"""

from typing import Dict
from enum import Enum


class Language(Enum):
    ENGLISH = "en"
    TURKISH = "tr"


# All UI strings with translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Application
    "app_name": {
        "en": "BPM - Blood Pressure Analysis",
        "tr": "BPM - Kan Basıncı Analizi"
    },
    "app_title": {
        "en": "Blood Pressure Analysis",
        "tr": "Kan Basıncı Analizi"
    },

    # Main Window
    "welcome_title": {
        "en": "Welcome to BPM",
        "tr": "BPM'e Hoş Geldiniz"
    },
    "welcome_desc": {
        "en": "Analyze blood pressure variability from your patient data. Upload an Excel file to get started.",
        "tr": "Hasta verilerinizden kan basıncı değişkenliğini analiz edin. Başlamak için bir Excel dosyası yükleyin."
    },

    # Step indicator
    "step_of": {
        "en": "Step {current} of {total}",
        "tr": "Adım {current} / {total}"
    },

    # Drop zone
    "drop_title": {
        "en": "Drop your Excel file here",
        "tr": "Excel dosyanızı buraya bırakın"
    },
    "drop_subtitle": {
        "en": "or click to browse",
        "tr": "veya dosya seçmek için tıklayın"
    },
    "drop_formats": {
        "en": "Supports .xlsx, .xls, .csv",
        "tr": ".xlsx, .xls, .csv desteklenir"
    },

    # Column mapping
    "map_columns": {
        "en": "Map Your Columns",
        "tr": "Sütunlarınızı Eşleştirin"
    },
    "map_desc": {
        "en": "Match your Excel columns to the required data fields. We've auto-detected some - please verify.",
        "tr": "Excel sütunlarınızı gerekli veri alanlarıyla eşleştirin. Bazılarını otomatik tespit ettik - lütfen doğrulayın."
    },
    "not_mapped": {
        "en": "-- Not mapped --",
        "tr": "-- Eşleştirilmedi --"
    },
    "data_preview": {
        "en": "Data Preview",
        "tr": "Veri Önizleme"
    },
    "data_quality_notes": {
        "en": "Data Quality Notes",
        "tr": "Veri Kalitesi Notları"
    },

    # Column names
    "col_patient_id": {
        "en": "Patient ID",
        "tr": "Hasta No"
    },
    "col_datetime": {
        "en": "Date/Time",
        "tr": "Tarih/Saat"
    },
    "col_date": {
        "en": "Date Only",
        "tr": "Sadece Tarih"
    },
    "col_time": {
        "en": "Time Only",
        "tr": "Sadece Saat"
    },
    "col_sbp": {
        "en": "Systolic BP *",
        "tr": "Sistolik KB *"
    },
    "col_dbp": {
        "en": "Diastolic BP *",
        "tr": "Diastolik KB *"
    },
    "col_heart_rate": {
        "en": "Heart Rate",
        "tr": "Nabız"
    },

    # Column tooltips
    "tip_patient_id": {
        "en": "Unique identifier for each patient",
        "tr": "Her hasta için benzersiz tanımlayıcı"
    },
    "tip_datetime": {
        "en": "When the reading was taken",
        "tr": "Ölçümün alındığı zaman"
    },
    "tip_date": {
        "en": "If date and time are separate",
        "tr": "Tarih ve saat ayrı ise"
    },
    "tip_time": {
        "en": "If date and time are separate",
        "tr": "Tarih ve saat ayrı ise"
    },
    "tip_sbp": {
        "en": "Required - upper BP number (mmHg)",
        "tr": "Zorunlu - üst KB değeri (mmHg)"
    },
    "tip_dbp": {
        "en": "Required - lower BP number (mmHg)",
        "tr": "Zorunlu - alt KB değeri (mmHg)"
    },
    "tip_heart_rate": {
        "en": "Optional - beats per minute",
        "tr": "İsteğe bağlı - dakikadaki atım sayısı"
    },

    # Processing
    "analyzing": {
        "en": "Analyzing Your Data",
        "tr": "Verileriniz Analiz Ediliyor"
    },
    "calculating_metrics": {
        "en": "Calculating BP variability metrics...",
        "tr": "KB değişkenlik metrikleri hesaplanıyor..."
    },

    # Results
    "results_title": {
        "en": "Analysis Results",
        "tr": "Analiz Sonuçları"
    },
    "patients": {
        "en": "Patients",
        "tr": "Hastalar"
    },
    "readings": {
        "en": "Readings",
        "tr": "Ölçümler"
    },
    "avg_sbp": {
        "en": "Avg SBP",
        "tr": "Ort. SKB"
    },
    "avg_dbp": {
        "en": "Avg DBP",
        "tr": "Ort. DKB"
    },

    # Table headers
    "tbl_patient_id": {
        "en": "Patient ID",
        "tr": "Hasta No"
    },
    "tbl_readings": {
        "en": "Readings",
        "tr": "Ölçüm"
    },
    "tbl_mean_sbp": {
        "en": "Mean SBP",
        "tr": "Ort. SKB"
    },
    "tbl_mean_dbp": {
        "en": "Mean DBP",
        "tr": "Ort. DKB"
    },
    "tbl_sd_sbp": {
        "en": "SD SBP",
        "tr": "SS SKB"
    },
    "tbl_sd_dbp": {
        "en": "SD DBP",
        "tr": "SS DKB"
    },
    "tbl_cv_sbp": {
        "en": "CV SBP%",
        "tr": "DK SKB%"
    },
    "tbl_cv_dbp": {
        "en": "CV DBP%",
        "tr": "DK DKB%"
    },
    "tbl_arv_sbp": {
        "en": "ARV SBP",
        "tr": "OGD SKB"
    },
    "tbl_arv_dbp": {
        "en": "ARV DBP",
        "tr": "OGD DKB"
    },
    "tbl_dipping": {
        "en": "Dipping %",
        "tr": "Düşüş %"
    },
    "tbl_classification": {
        "en": "Classification",
        "tr": "Sınıflandırma"
    },

    # Buttons
    "btn_continue": {
        "en": "Continue",
        "tr": "Devam"
    },
    "btn_back": {
        "en": "Back",
        "tr": "Geri"
    },
    "btn_new_analysis": {
        "en": "New Analysis",
        "tr": "Yeni Analiz"
    },
    "btn_export_excel": {
        "en": "Export to Excel",
        "tr": "Excel'e Aktar"
    },
    "btn_export_pdf": {
        "en": "Export PDF Report",
        "tr": "PDF Raporu Aktar"
    },

    # Settings
    "settings": {
        "en": "Settings",
        "tr": "Ayarlar"
    },
    "language": {
        "en": "Language",
        "tr": "Dil"
    },
    "english": {
        "en": "English",
        "tr": "İngilizce"
    },
    "turkish": {
        "en": "Turkish",
        "tr": "Türkçe"
    },

    # Messages
    "file_loaded": {
        "en": "File Loaded",
        "tr": "Dosya Yüklendi"
    },
    "loaded_rows": {
        "en": "Loaded {count} rows from {filename}",
        "tr": "{filename} dosyasından {count} satır yüklendi"
    },
    "error": {
        "en": "Error",
        "tr": "Hata"
    },
    "invalid_file": {
        "en": "Invalid File",
        "tr": "Geçersiz Dosya"
    },
    "invalid_file_msg": {
        "en": "Please select an Excel file (.xlsx, .xls) or CSV file.",
        "tr": "Lütfen bir Excel dosyası (.xlsx, .xls) veya CSV dosyası seçin."
    },
    "load_error": {
        "en": "Failed to load file:\n{error}",
        "tr": "Dosya yüklenemedi:\n{error}"
    },
    "analysis_error": {
        "en": "Failed to analyze data:\n{error}",
        "tr": "Veri analiz edilemedi:\n{error}"
    },
    "export_complete": {
        "en": "Export Complete",
        "tr": "Dışa Aktarım Tamamlandı"
    },
    "results_saved": {
        "en": "Results saved to:\n{path}",
        "tr": "Sonuçlar kaydedildi:\n{path}"
    },
    "export_error": {
        "en": "Failed to export:\n{error}",
        "tr": "Dışa aktarılamadı:\n{error}"
    },
    "coming_soon": {
        "en": "Coming Soon",
        "tr": "Yakında"
    },
    "pdf_coming_soon": {
        "en": "PDF export will be implemented in the next version.",
        "tr": "PDF dışa aktarımı bir sonraki sürümde eklenecektir."
    },
    "select_bp_file": {
        "en": "Select BP Data File",
        "tr": "KB Veri Dosyası Seçin"
    },
    "export_results": {
        "en": "Export Results",
        "tr": "Sonuçları Dışa Aktar"
    },

    # BP Classifications (Turkish medical terms)
    "class_normal": {
        "en": "Normal (<120/<80)",
        "tr": "Normal (<120/<80)"
    },
    "class_elevated": {
        "en": "Elevated (120-129/<80)",
        "tr": "Yüksek (120-129/<80)"
    },
    "class_stage1": {
        "en": "Stage 1 HTN (130-139/80-89)",
        "tr": "Evre 1 HT (130-139/80-89)"
    },
    "class_stage2": {
        "en": "Stage 2 HTN (>=140/>=90)",
        "tr": "Evre 2 HT (>=140/>=90)"
    },
    "class_crisis": {
        "en": "Hypertensive Crisis (>180/>120)",
        "tr": "Hipertansif Kriz (>180/>120)"
    },

    # Dipping Status
    "dip_extreme": {
        "en": "Extreme Dipper (>20%)",
        "tr": "Aşırı Düşüş (>20%)"
    },
    "dip_normal": {
        "en": "Normal Dipper (10-20%)",
        "tr": "Normal Düşüş (10-20%)"
    },
    "dip_non": {
        "en": "Non-Dipper (<10%)",
        "tr": "Düşüş Yok (<10%)"
    },
    "dip_reverse": {
        "en": "Reverse Dipper (<0%)",
        "tr": "Ters Düşüş (<0%)"
    },

    # Excel Export Headers
    "excel_patient_id": {
        "en": "Patient ID",
        "tr": "Hasta No"
    },
    "excel_reading_count": {
        "en": "Reading Count",
        "tr": "Ölçüm Sayısı"
    },
    "excel_mean_sbp": {
        "en": "Mean SBP",
        "tr": "Ortalama SKB"
    },
    "excel_mean_dbp": {
        "en": "Mean DBP",
        "tr": "Ortalama DKB"
    },
    "excel_min_sbp": {
        "en": "Min SBP",
        "tr": "Min SKB"
    },
    "excel_max_sbp": {
        "en": "Max SBP",
        "tr": "Maks SKB"
    },
    "excel_min_dbp": {
        "en": "Min DBP",
        "tr": "Min DKB"
    },
    "excel_max_dbp": {
        "en": "Max DBP",
        "tr": "Maks DKB"
    },
    "excel_sd_sbp": {
        "en": "SD SBP",
        "tr": "SS SKB"
    },
    "excel_sd_dbp": {
        "en": "SD DBP",
        "tr": "SS DKB"
    },
    "excel_cv_sbp": {
        "en": "CV SBP (%)",
        "tr": "DK SKB (%)"
    },
    "excel_cv_dbp": {
        "en": "CV DBP (%)",
        "tr": "DK DKB (%)"
    },
    "excel_arv_sbp": {
        "en": "ARV SBP",
        "tr": "OGD SKB"
    },
    "excel_arv_dbp": {
        "en": "ARV DBP",
        "tr": "OGD DKB"
    },
    "excel_weighted_sd_sbp": {
        "en": "Weighted SD SBP",
        "tr": "Ağırlıklı SS SKB"
    },
    "excel_weighted_sd_dbp": {
        "en": "Weighted SD DBP",
        "tr": "Ağırlıklı SS DKB"
    },
    "excel_pulse_pressure": {
        "en": "Pulse Pressure",
        "tr": "Nabız Basıncı"
    },
    "excel_dipping": {
        "en": "Dipping (%)",
        "tr": "Düşüş (%)"
    },
    "excel_dipping_status": {
        "en": "Dipping Status",
        "tr": "Düşüş Durumu"
    },
    "excel_bp_class": {
        "en": "BP Classification",
        "tr": "KB Sınıflandırması"
    },
}


class Translator:
    """Simple translator class for the application."""

    _instance = None
    _language = Language.TURKISH  # Default to Turkish

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_language(cls) -> Language:
        return cls._language

    @classmethod
    def set_language(cls, language: Language):
        cls._language = language

    @classmethod
    def get(cls, key: str, **kwargs) -> str:
        """Get translated string with optional format parameters."""
        lang_code = cls._language.value

        if key not in TRANSLATIONS:
            return key

        text = TRANSLATIONS[key].get(lang_code, TRANSLATIONS[key].get("en", key))

        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass

        return text


# Convenience function
def tr(key: str, **kwargs) -> str:
    """Shorthand for Translator.get()"""
    return Translator.get(key, **kwargs)
