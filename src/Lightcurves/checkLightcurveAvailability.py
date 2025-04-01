import pandas as pd
from lightkurve import search_lightcurve

def check_lightcurve_availability(csv_path):
    df = pd.read_csv(csv_path)
    count_found = 0
    count_not_found = 0
    total = len(df)

    for i, row in df.iterrows():
        target_id = str(row["id"]).strip()
        source = str(row["source"]).lower().strip()

        if source == "kepler":
            author = "Kepler"
        elif source == "tess":
            author = "SPOC"
        else:
            print(f"[{target_id}] Bilinmeyen kaynak: {source}")
            continue

        try:
            search_result = search_lightcurve(target_id, author=author)
            if len(search_result) > 0:
                count_found += 1
            else:
                count_not_found += 1
        except Exception as e:
            print(f"Hata ({target_id}): {e}")
            count_not_found += 1

    print("\n🔍 Işık Eğrisi Arama Sonuçları")
    print(f"Toplam geçiş adayı         : {total}")
    print(f"Işık eğrisi bulunanlar     : {count_found}")
    print(f"Işık eğrisi bulunamayanlar : {count_not_found}")

if __name__ == "__main__":
    check_lightcurve_availability("/content/drive/MyDrive/starTrace/data/multimission/MERGED/kepler_and_tess_with_sources.csv")
