import pandas as pd
from Constants import *

def analyze_data(cumulative_path, confirmed_path, false_positive_path):

    try:
        cumulative_df = pd.read_csv(cumulative_path, comment="#")
        confirmed_df = pd.read_csv(confirmed_path, comment="#")
        false_positive_df = pd.read_csv(false_positive_path, comment="#")

        common_confirmed = pd.merge(cumulative_df, confirmed_df, on="kepid", how="inner")["kepid"].nunique()
        common_false_positive = pd.merge(cumulative_df, false_positive_df, on="kepid", how="inner")["kepid"].nunique()

        not_in_cumulative_confirmed = confirmed_df[~confirmed_df["kepid"].isin(cumulative_df["kepid"])]["kepid"].nunique()
        not_in_cumulative_false_positive = false_positive_df[~false_positive_df["kepid"].isin(cumulative_df["kepid"])]["kepid"].nunique()

        total_cumulative = cumulative_df["kepid"].nunique()

        print(f"cumulative dosyasında toplam {total_cumulative} kayıt var, bu kayıtlardan {common_confirmed} tanesi CONFIRMED csv'sinde, {common_false_positive} tanesi de FALSE POSITIVE csv'sinde var.")
        print(f"cumulative.csv dosyasında olmayan {not_in_cumulative_confirmed} CONFIRMED var.")
        print(f"cumulative csv dosyasında olmayan {not_in_cumulative_false_positive} FALSE POSITIVE var.")

    except FileNotFoundError as e:
        print(f"Dosya bulunamadı. Lütfen dosya yollarını kontrol edin. {e}")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    analyze_data(EXOPLANET_DATA_FILE, CONFIRMED_EXOPLANET_DATA_FILE, FALSE_POSITIVE_EXOPLANET_DATA_FILE)