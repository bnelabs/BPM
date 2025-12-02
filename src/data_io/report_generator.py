"""
PDF Report Generator for BP Analysis Results

Generates professional clinical reports using reportlab.
"""

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from analysis.metrics import VariabilityMetrics, DippingStatus, HypertensionStage
from core.translations import tr, Translator, Language


class PDFReportGenerator:
    """Generate professional PDF reports for BP analysis results."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1D1D1F')
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#007AFF')
        ))

        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=5,
            textColor=colors.HexColor('#1D1D1F')
        ))

        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor('#1D1D1F')
        ))

        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#86868B')
        ))

    def generate_cohort_report(
        self,
        results: Dict[str, VariabilityMetrics],
        output_path: str,
        title: Optional[str] = None
    ) -> str:
        """
        Generate a cohort summary PDF report.

        Args:
            results: Dictionary of patient_id -> VariabilityMetrics
            output_path: Path to save PDF
            title: Optional custom title

        Returns:
            Path to generated PDF
        """
        is_turkish = Translator.get_language() == Language.TURKISH

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Title
        report_title = title or (
            "Kan Basıncı Değişkenlik Analizi Raporu" if is_turkish
            else "Blood Pressure Variability Analysis Report"
        )
        story.append(Paragraph(report_title, self.styles['ReportTitle']))

        # Date
        date_str = datetime.now().strftime("%d.%m.%Y %H:%M" if is_turkish else "%Y-%m-%d %H:%M")
        date_label = "Rapor Tarihi" if is_turkish else "Report Date"
        story.append(Paragraph(f"{date_label}: {date_str}", self.styles['ReportBody']))
        story.append(Spacer(1, 20))

        # Summary Section
        summary_title = "Özet İstatistikler" if is_turkish else "Summary Statistics"
        story.append(Paragraph(summary_title, self.styles['SectionHeader']))

        # Calculate summary stats
        total_patients = len(results)
        total_readings = sum(m.reading_count for m in results.values())
        avg_sbp = sum(m.mean_sbp for m in results.values()) / total_patients if total_patients > 0 else 0
        avg_dbp = sum(m.mean_dbp for m in results.values()) / total_patients if total_patients > 0 else 0

        summary_data = [
            [
                "Toplam Hasta" if is_turkish else "Total Patients",
                str(total_patients)
            ],
            [
                "Toplam Ölçüm" if is_turkish else "Total Readings",
                str(total_readings)
            ],
            [
                "Ortalama SKB" if is_turkish else "Mean SBP",
                f"{avg_sbp:.1f} mmHg"
            ],
            [
                "Ortalama DKB" if is_turkish else "Mean DBP",
                f"{avg_dbp:.1f} mmHg"
            ],
        ]

        summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1D1D1F')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E5EA')),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Patient Results Table
        results_title = "Hasta Sonuçları" if is_turkish else "Patient Results"
        story.append(Paragraph(results_title, self.styles['SectionHeader']))

        # Table headers
        if is_turkish:
            headers = ['Hasta No', 'Ölçüm', 'Ort. SKB', 'Ort. DKB', 'SS SKB', 'DK SKB%', 'Düşüş %', 'Sınıf']
        else:
            headers = ['Patient ID', 'Readings', 'Mean SBP', 'Mean DBP', 'SD SBP', 'CV SBP%', 'Dipping %', 'Class']

        table_data = [headers]

        for patient_id, metrics in results.items():
            dipping = f"{metrics.dipping_percentage:.1f}" if metrics.dipping_percentage else "-"
            classification = self._get_short_classification(metrics.mean_bp_classification, is_turkish)

            row = [
                str(patient_id),
                str(metrics.reading_count),
                f"{metrics.mean_sbp:.1f}",
                f"{metrics.mean_dbp:.1f}",
                f"{metrics.sd_sbp:.2f}",
                f"{metrics.cv_sbp:.1f}",
                dipping,
                classification
            ]
            table_data.append(row)

        # Create table with appropriate column widths
        col_widths = [2.5*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2.5*cm]
        results_table = Table(table_data, colWidths=col_widths)

        results_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Body style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F7')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E5EA')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(results_table)
        story.append(Spacer(1, 30))

        # Classification Distribution
        dist_title = "KB Sınıflandırma Dağılımı" if is_turkish else "BP Classification Distribution"
        story.append(Paragraph(dist_title, self.styles['SectionHeader']))

        # Count classifications
        class_counts = {}
        for metrics in results.values():
            if metrics.mean_bp_classification:
                class_name = self._get_classification_name(metrics.mean_bp_classification, is_turkish)
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

        class_data = [[
            "Sınıflandırma" if is_turkish else "Classification",
            "Hasta Sayısı" if is_turkish else "Patient Count",
            "Yüzde" if is_turkish else "Percentage"
        ]]

        for class_name, count in class_counts.items():
            pct = (count / total_patients * 100) if total_patients > 0 else 0
            class_data.append([class_name, str(count), f"{pct:.1f}%"])

        class_table = Table(class_data, colWidths=[7*cm, 4*cm, 3*cm])
        class_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34C759')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E5EA')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F7')]),
        ]))

        story.append(class_table)
        story.append(Spacer(1, 30))

        # Dipping Status Distribution
        dip_title = "Gece Düşüş Durumu Dağılımı" if is_turkish else "Nocturnal Dipping Distribution"
        story.append(Paragraph(dip_title, self.styles['SectionHeader']))

        dip_counts = {}
        for metrics in results.values():
            if metrics.dipping_status:
                dip_name = self._get_dipping_name(metrics.dipping_status, is_turkish)
                dip_counts[dip_name] = dip_counts.get(dip_name, 0) + 1

        dip_data = [[
            "Düşüş Durumu" if is_turkish else "Dipping Status",
            "Hasta Sayısı" if is_turkish else "Patient Count",
            "Yüzde" if is_turkish else "Percentage"
        ]]

        for dip_name, count in dip_counts.items():
            pct = (count / total_patients * 100) if total_patients > 0 else 0
            dip_data.append([dip_name, str(count), f"{pct:.1f}%"])

        if len(dip_data) > 1:
            dip_table = Table(dip_data, colWidths=[7*cm, 4*cm, 3*cm])
            dip_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9500')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E5EA')),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F7')]),
            ]))
            story.append(dip_table)
        else:
            no_data = "Gece düşüş verisi mevcut değil" if is_turkish else "No dipping data available"
            story.append(Paragraph(no_data, self.styles['ReportBody']))

        # Footer
        story.append(Spacer(1, 40))
        footer_text = (
            "Bu rapor BPM (Kan Basıncı İzleme) uygulaması tarafından oluşturulmuştur."
            if is_turkish else
            "This report was generated by BPM (Blood Pressure Monitoring) application."
        )
        story.append(Paragraph(footer_text, self.styles['Footer']))

        # Build PDF
        doc.build(story)

        return output_path

    def _get_short_classification(self, stage: Optional[HypertensionStage], is_turkish: bool) -> str:
        """Get short classification label."""
        if stage is None:
            return "-"

        mapping = {
            HypertensionStage.NORMAL: ("Normal", "Normal"),
            HypertensionStage.ELEVATED: ("Yüksek", "Elevated"),
            HypertensionStage.STAGE_1: ("Evre 1", "Stage 1"),
            HypertensionStage.STAGE_2: ("Evre 2", "Stage 2"),
            HypertensionStage.CRISIS: ("Kriz", "Crisis"),
        }

        tr_label, en_label = mapping.get(stage, ("-", "-"))
        return tr_label if is_turkish else en_label

    def _get_classification_name(self, stage: HypertensionStage, is_turkish: bool) -> str:
        """Get full classification name."""
        mapping = {
            HypertensionStage.NORMAL: ("Normal (<120/<80)", "Normal (<120/<80)"),
            HypertensionStage.ELEVATED: ("Yüksek (120-129/<80)", "Elevated (120-129/<80)"),
            HypertensionStage.STAGE_1: ("Evre 1 HT (130-139/80-89)", "Stage 1 HTN (130-139/80-89)"),
            HypertensionStage.STAGE_2: ("Evre 2 HT (≥140/≥90)", "Stage 2 HTN (≥140/≥90)"),
            HypertensionStage.CRISIS: ("Hipertansif Kriz (>180/>120)", "Hypertensive Crisis (>180/>120)"),
        }

        tr_label, en_label = mapping.get(stage, ("-", "-"))
        return tr_label if is_turkish else en_label

    def _get_dipping_name(self, status: DippingStatus, is_turkish: bool) -> str:
        """Get dipping status name."""
        mapping = {
            DippingStatus.NORMAL_DIPPER: ("Normal Düşüş (10-20%)", "Normal Dipper (10-20%)"),
            DippingStatus.NON_DIPPER: ("Düşüş Yok (<10%)", "Non-Dipper (<10%)"),
            DippingStatus.EXTREME_DIPPER: ("Aşırı Düşüş (>20%)", "Extreme Dipper (>20%)"),
            DippingStatus.REVERSE_DIPPER: ("Ters Düşüş (<0%)", "Reverse Dipper (<0%)"),
        }

        tr_label, en_label = mapping.get(status, ("-", "-"))
        return tr_label if is_turkish else en_label
