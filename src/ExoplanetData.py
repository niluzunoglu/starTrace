import pandas as pd
import numpy as np
import pywt

from scipy.fft import fft 

from Constants import EXOPLANET_DATA_FILE

class ExoplanetData:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.file_path, comment='#')
        return df

    def show_head(self, n: int = 5):
        print(self.df.head(n))

    def summary(self) -> pd.DataFrame:
        return self.df.describe()

    def filter_by_disposition(self, disposition: str) -> pd.DataFrame:
        return self.df[self.df['koi_disposition'] == disposition]
    
    def get_columns(self) -> list:
        return list(self.df.columns)

    def get_dataframe_with_columns(self, columns: list) -> pd.DataFrame:
        existing_columns = [col for col in columns if col in self.df.columns]
        return self.df[existing_columns]

    def extract_statistical_features(self, columns: list) -> pd.DataFrame:
        feature_df = pd.DataFrame(index=self.df.index)
        for col in columns:
            if col in self.df.columns:
                mean_val = self.df[col].mean()
                std_val = self.df[col].std()
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                median_val = self.df[col].median()

                feature_df[f'{col}_mean'] = mean_val
                feature_df[f'{col}_std'] = std_val
                feature_df[f'{col}_min'] = min_val
                feature_df[f'{col}_max'] = max_val
                feature_df[f'{col}_median'] = median_val
        return feature_df

    def extract_fourier_features(self, columns: list) -> pd.DataFrame:
        feature_df = pd.DataFrame(index=self.df.index)
        for col in columns:
            if col in self.df.columns:
                fft_values = np.abs(fft(self.df[col]))
                feature_df[f'{col}_fft_mean'] = np.mean(fft_values)
                feature_df[f'{col}_fft_std'] = np.std(fft_values)
                feature_df[f'{col}_fft_max'] = np.max(fft_values)
        return feature_df

    def extract_wavelet_features(self, columns: list, wavelet='haar') -> pd.DataFrame:
        feature_df = pd.DataFrame(index=self.df.index)
        for col in columns:
            if col in self.df.columns:
                # Her satır için Wavelet dönüşümü uygula
                coeffs = pywt.wavedec(self.df[col], wavelet, level=1)  # 1 seviyeli ayrıştırma
                # Detay katsayılarının istatistiksel özelliklerini al
                feature_df[f'{col}_wavelet_detail_mean'] = np.mean(coeffs[0])
                feature_df[f'{col}_wavelet_detail_std'] = np.std(coeffs[0])
                feature_df[f'{col}_wavelet_approx_mean'] = np.mean(coeffs[1])
                feature_df[f'{col}_wavelet_approx_std'] = np.std(coeffs[1])
        return feature_df

    def extract_manual_features(self) -> pd.DataFrame:
        feature_df = pd.DataFrame(index=self.df.index)

        if 'koi_depth' in self.df.columns and 'koi_period' in self.df.columns:
            feature_df['depth_period_ratio'] = self.df['koi_depth'] / self.df['koi_period']

        if 'koi_steff' in self.df.columns:
            feature_df['koi_steff_squared'] = self.df['koi_steff'] ** 2

        return feature_df
    

    def show_target_distribution(self, target_column: str):
        if target_column in self.df.columns:
            print(self.df[target_column].value_counts())
        else:
            print(f"Hata: '{target_column}' sütunu bulunamadı.")
    
    def remove_candidates(self, target_column: str) -> None:
        if target_column in self.df.columns:
            self.df = self.df[self.df[target_column] != 'CANDIDATE']
            print("CANDIDATE etiketli satırlar temizlendi.")
        else:
            print(f"Hata: '{target_column}' sütunu bulunamadı.")

if __name__ == "__main__":

    try:
        data = ExoplanetData(EXOPLANET_DATA_FILE)
        data.show_head()

        summary_df = data.summary()
        print(summary_df)

        confirmed_df = data.filter_by_disposition("CONFIRMED")
        print(f"Bulunan CONFIRMED gezegen satır sayısı: {len(confirmed_df)}")
    
        #all_columns = data.get_columns()
        #print("Tüm sütun isimleri:")
        #print(all_columns)

        desired_columns = ["koi_disposition", "koi_period", "koi_depth"]
        subset_df = data.get_dataframe_with_columns(desired_columns)
        print("Seçilen sütunlardan oluşan DataFrame'in ilk 5 satırı:")
        print(subset_df.head()) 

        data.show_target_distribution("koi_disposition")

    except FileNotFoundError:
        print(f"Error: File not found -> {EXOPLANET_DATA_FILE}")
    
    except pd.errors.ParserError:
        print(f"Error: Could not parse the file -> {EXOPLANET_DATA_FILE}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")