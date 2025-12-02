#!/usr/bin/env python3
"""
Generate sample BP data for testing BPM application.
Creates realistic blood pressure readings with various patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_patient_readings(patient_id: str, num_days: int = 3, readings_per_day: int = 8) -> list:
    """Generate realistic BP readings for one patient."""
    readings = []

    # Base BP values (varies by patient)
    base_sbp = random.randint(110, 160)
    base_dbp = random.randint(65, 95)
    base_hr = random.randint(60, 85)

    # Patient characteristics
    is_dipper = random.random() > 0.3  # 70% are dippers
    dip_amount = random.uniform(10, 20) if is_dipper else random.uniform(-5, 10)

    start_date = datetime(2024, 1, 15)

    for day in range(num_days):
        current_date = start_date + timedelta(days=day)

        # Reading times spread throughout 24h
        hours = [6, 8, 10, 12, 15, 18, 21, 23][:readings_per_day]

        for hour in hours:
            reading_time = current_date.replace(hour=hour, minute=random.randint(0, 59))

            # Apply circadian rhythm
            is_night = hour < 6 or hour >= 22

            # Calculate BP with variation
            if is_night:
                sbp = base_sbp * (1 - dip_amount/100) + np.random.normal(0, 5)
                dbp = base_dbp * (1 - dip_amount/100 * 0.8) + np.random.normal(0, 3)
            else:
                # Morning surge
                if 6 <= hour <= 9:
                    sbp = base_sbp + random.randint(5, 15) + np.random.normal(0, 6)
                else:
                    sbp = base_sbp + np.random.normal(0, 8)
                dbp = base_dbp + np.random.normal(0, 5)

            hr = base_hr + np.random.normal(0, 8)

            readings.append({
                'Hasta_No': patient_id,
                'Tarih': reading_time.strftime('%d.%m.%Y'),
                'Saat': reading_time.strftime('%H:%M'),
                'SKB': int(max(80, min(220, sbp))),
                'DKB': int(max(50, min(130, dbp))),
                'Nabiz': int(max(45, min(140, hr)))
            })

    return readings

def main():
    all_readings = []

    # Generate data for 20 patients
    num_patients = 20

    print(f"Generating sample data for {num_patients} patients...")

    for i in range(1, num_patients + 1):
        patient_id = f"H{i:03d}"
        num_days = random.randint(2, 5)
        readings_per_day = random.randint(6, 12)

        patient_readings = generate_patient_readings(
            patient_id,
            num_days=num_days,
            readings_per_day=readings_per_day
        )
        all_readings.extend(patient_readings)

    # Create DataFrame
    df = pd.DataFrame(all_readings)

    # Sort by patient and time
    df = df.sort_values(['Hasta_No', 'Tarih', 'Saat'])

    # Save to Excel
    output_file = '/app/data/ornek_kb_verileri.xlsx'
    df.to_excel(output_file, index=False)

    print(f"Generated {len(df)} readings for {num_patients} patients")
    print(f"Saved to: {output_file}")

    # Also save a summary
    print("\nSample data preview:")
    print(df.head(10).to_string())

    # Also create English version
    df_en = df.copy()
    df_en.columns = ['Patient_ID', 'Date', 'Time', 'SBP', 'DBP', 'HR']
    df_en['Date'] = pd.to_datetime(df_en['Date'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
    df_en.to_excel('/app/data/sample_bp_data.xlsx', index=False)
    print(f"\nEnglish version saved to: /app/data/sample_bp_data.xlsx")

if __name__ == '__main__':
    main()
