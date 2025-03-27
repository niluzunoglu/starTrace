import pandas as pd
from ObservationSource import ObservationSource
import numpy as np
import pywt
from scipy.fft import fft
from Constants import KEPLER_CSV_PATH, TESS_CSV_PATH
from mappingTable import COLUMN_MAPPING

class ExoplanetData:

    def __init__(self, file_path: str, observation_source: ObservationSource = ObservationSource):
        self.file_path = file_path
        self.observation_source = observation_source
        self.df = self._load_data()
        self.target_column = "disposition"  
        self.df = self._clean_data(self.df)

    def _load_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.file_path, comment='#')
        df = self._refactor_columns(df)  
        return df

    def _refactor_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        mapping = COLUMN_MAPPING.get(str(self.observation_source))
        if mapping:
            existing_columns = set(df.columns)
            rename_dict = {target_col: source_col for source_col, target_col in mapping.items() if target_col in existing_columns}

            # Sütun isimlerinin ortaklaştırılması
            df = df.rename(columns=rename_dict)
            # Verilen sütun isimleri dışında kalan sütunların silinmesi.
            filtered_df = df[list(rename_dict.values())]
            print("Filtered dataframe : \n", filtered_df)

            if 'disposition' in df.columns:
                print("Disposition sütunundaki unique değerler:", df['disposition'].unique())

            return filtered_df
        
        else:
            raise ValueError(f"Bilinmeyen gözlem kaynağı: {self.observation_source}")
        
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:

        if str(self.observation_source).lower() == "tess":

            # Known planet, Ambigious Planet Candidate ve False Alarmları sil.
            df = df[~df["disposition"].isin(["KP", "APC", "FA"])].copy()

            # 2. Geri kalanları yeniden adlandır
            df["disposition"] = df["disposition"].replace({
                "PC": "CANDIDATE",
                "FP": "FALSE POSITIVE",
                "CP": "CONFIRMED"
            })

        return df

    def show_head(self, n: int = 5):
        print(self.df.head(n))

    def summary(self) -> pd.DataFrame:
        return self.df.describe()

    def filter_by_disposition(self, disposition: str) -> pd.DataFrame:
        return self.df[self.df[self.target_column] == disposition]
    
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
                coeffs = pywt.wavedec(self.df[col], wavelet, level=1)
                feature_df[f'{col}_wavelet_detail_mean'] = np.mean(coeffs[0])
                feature_df[f'{col}_wavelet_detail_std'] = np.std(coeffs[0])
                feature_df[f'{col}_wavelet_approx_mean'] = np.mean(coeffs[1])
                feature_df[f'{col}_wavelet_approx_std'] = np.std(coeffs[1])
        return feature_df

    def extract_manual_features(self) -> pd.DataFrame:
        feature_df = pd.DataFrame(index=self.df.index)

        period_col = "period"  
        depth_col = "depth"   
        steff_col = "steff"

        if period_col in self.df.columns and depth_col in self.df.columns:
            feature_df['depth_period_ratio'] = self.df[depth_col] / self.df[period_col]

        if steff_col in self.df.columns:
            feature_df['steff_squared'] = self.df[steff_col] ** 2

        return feature_df

    def show_target_distribution(self):
        if self.target_column in self.df.columns:
            print(self.df[self.target_column].value_counts())
        else:
            print(f"Hata: '{self.target_column}' sütunu bulunamadı.")
    
    def remove_candidates(self):
        if self.target_column in self.df.columns:
            self.df = self.df[self.df[self.target_column] != 'CANDIDATE'] #Buraya Kanditat olup olmama durumunu nasıl yapacaz
            print("CANDIDATE etiketli satırlar temizlendi.")
        else:
            print(f"Hata: '{self.target_column}' sütunu bulunamadı.")

def merge_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, 
                         common_columns: list) -> pd.DataFrame:
    """İki DataFrame'i ortak sütunlara göre birleştirir."""
    merged_df = pd.merge(df1, df2, on=common_columns, how='inner')
    return merged_df

if __name__ == "__main__":

    try:
        kepler_data = ExoplanetData(KEPLER_CSV_PATH, ObservationSource.KEPLER)
        #print("\nKepler Verisi Özeti:")
        #kepler_data.show_head()
        kepler_data.show_target_distribution()
        #print(kepler_data.get_columns())

        tess_data = ExoplanetData(TESS_CSV_PATH, ObservationSource.TESS)
        #print("\nTESS Verisi Özeti:")
        #tess_data.show_head()
        tess_data.show_target_distribution()
        #print(tess_data.get_columns())

        """ 
        common_columns = ["period", "depth", "duration", "steff", "srad", "slogg", "model_snr", "ra", "dec"]
        existing_kepler_columns = [col for col in common_columns if col in kepler_data.df.columns]
        existing_tess_columns = [col for col in common_columns if col in tess_data.df.columns]
        
        # Veriyi hazırla
        kepler_subset = kepler_data.get_dataframe_with_columns(existing_kepler_columns)
        tess_subset = tess_data.get_dataframe_with_columns(existing_tess_columns)

        common_cols = list(set(kepler_subset.columns) & set(tess_subset.columns))
        print(f"\nOrtak sütunlar: {common_cols}")
        """
    except FileNotFoundError:
        print(f"Error: File not found -> {KEPLER_CSV_PATH}")
    
    except pd.errors.ParserError:
        print(f"Error: Could not parse the file -> {KEPLER_CSV_PATH}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")