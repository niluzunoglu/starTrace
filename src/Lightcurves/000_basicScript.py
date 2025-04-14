import os
import pandas as pd
from Constants import LIGHTCURVE_DIR

SUMMARY_CSV_PATH = "../../data/multimission/MERGED/kepler_and_tess.csv"
LIGHTCURVE_DIR = 'lightcurves'

def check_lightcurve_existence():
    try:
        df = pd.read_csv(SUMMARY_CSV_PATH)
    except FileNotFoundError:
        print(f"Hata: {SUMMARY_CSV_PATH} dosyası bulunamadı.")
        return

    if 'id' not in df.columns:
        print("Hata: Özet veri setinde 'id' sütunu bulunamadı.")
        return

    total_ids = len(df)
    found_ids = []
    not_found_ids = []

    # Her id için lightcurve dosyasının varlığını kontrol et
    for target_id in df['id']:
        # Varsayım: dosya adı örneğin, "12345.csv"
        filename = f"{target_id}.csv"
        filepath = os.path.join(LIGHTCURVE_DIR, filename)
        if os.path.exists(filepath):
            found_ids.append(target_id)
            print(f"Lightcurve bulundu: {target_id} -> {filepath}")
        else:
            not_found_ids.append(target_id)

    # Sonuçları raporla
    print("\n=================================")
    print(f"Toplam ID Sayısı: {total_ids}")
    print(f"Lightcurve dosyası bulunan ID sayısı: {len(found_ids)}")
    print(f"Lightcurve dosyası bulunmayan ID sayısı: {len(not_found_ids)}")
    print("=================================\n")

if __name__ == "__main__":
    check_lightcurve_existence()
