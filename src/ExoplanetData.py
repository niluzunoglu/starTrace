import pandas as pd
import numpy as np
import pywt
from tabulate import tabulate

from scipy.fft import fft
from Constants import KEPLER_CSV_PATH, TESS_CSV_PATH
from mappingTable import COLUMN_MAPPING
from ObservationSource import ObservationSource

class ExoplanetData:

    def __init__(self, file_path: str, observation_source: ObservationSource = ObservationSource):
        
        if(observation_source != ObservationSource.MERGED):
            self.file_path = file_path
            self.observation_source = observation_source
            self.df = self._load_data()
            self.target_column = "disposition"  
            self.df = self._clean_data(self.df)
            self.common_columns = []
            self.df["id"] = self.df["id"].astype(str)
        
        else:
            self.file_path = file_path
            self.df = self._load_data()


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

            # Yeni bir teleskop verisi eklenirken kullanılabileceği için yorum satırında.
            #if 'disposition' in df.columns:
            #    print("Disposition sütunundaki unique değerler:", df['disposition'].unique())
            self.common_columns = filtered_df.columns
            return filtered_df
        
        else:
            raise ValueError(f"Bilinmeyen gözlem kaynağı: {self.observation_source}")
        
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:

        if self.observation_source == ObservationSource.TESS:

            # Known planet, Ambigious Planet Candidate ve False Alarmları sil.
            df = df[~df["disposition"].isin(["KP", "APC", "FA"])].copy()

            # 2. Geri kalanları yeniden adlandır
            df["disposition"] = df["disposition"].replace({
                "PC": "CANDIDATE",
                "FP": "FALSE POSITIVE",
                "CP": "CONFIRMED"
            })

        return df
    
    def show(self, max_rows: int = 10):

        pd.set_option('display.max_columns', None)
        print("\n🔭 {} Exoplanet Verisi (ilk {} satır):\n".format(str(self.observation_source), max_rows))
        print(tabulate(self.df.head(max_rows), headers='keys', tablefmt='fancy_grid', showindex=False))
        print(f"\n📏 Toplam Satır: {len(self.df)} | Sütun: {len(self.df.columns)}")


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


def merge_exoplanet_data(data1: ExoplanetData, data2: ExoplanetData, common_columns:list, output_path: str) -> pd.DataFrame:
    """
    İki ExoplanetData nesnesinin verisini (df) ortak sütunlara göre birleştirir 
    ve sonucu belirtilen dosya yoluna kaydeder.

    Args:
        data1 (ExoplanetData): Birinci veri nesnesi.
        data2 (ExoplanetData): İkinci veri nesnesi.
        common_columns (list): Ortak sütun adları.
        output_path (str): Kaydedilecek CSV dosyasının yolu.

    Returns:
        pd.DataFrame: Birleştirilmiş veri çerçevesi.
    """
    df1 = data1.df
    df2 = data2.df

    print(df1)
    print(df2)

    print("Common columns : ", common_columns)
    merged_df = pd.merge(df1, df2, on = common_columns, how='outer')
    print(merged_df)

    print(f"✅ Merge sonucu: {len(merged_df)} satır")
    merged_df.to_csv(output_path, index=False)
    print(f"✅ Birleştirilmiş veri kaydedildi: {output_path}")
    return merged_df

if __name__ == "__main__":

    try:
        kepler_data = ExoplanetData(KEPLER_CSV_PATH, ObservationSource.KEPLER)
        #print("\nKepler Verisi Özeti:")
        #kepler_data.show_head()
        kepler_data.show_target_distribution()
        kepler_data.show()
        #print(kepler_data.get_columns())

        tess_data = ExoplanetData(TESS_CSV_PATH, ObservationSource.TESS)
        #print("\nTESS Verisi Özeti:")
        #tess_data.show_head()
        tess_data.show_target_distribution()
        tess_data.show()
        #print(tess_data.get_columns())

        common_columns = list(COLUMN_MAPPING.get(str(ObservationSource.TESS)).keys())
        merge_exoplanet_data(kepler_data, tess_data, common_columns=common_columns, output_path="../data/multimission/MERGED/kepler_and_tess.csv")



    except FileNotFoundError:
        print(f"Error: File not found -> {KEPLER_CSV_PATH}")
    
    except pd.errors.ParserError:
        print(f"Error: Could not parse the file -> {KEPLER_CSV_PATH}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")