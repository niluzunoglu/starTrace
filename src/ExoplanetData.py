import pandas as pd
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

if __name__ == "__main__":

    try:
        data = ExoplanetData(EXOPLANET_DATA_FILE)
        data.show_head()

        summary_df = data.summary()
        print(summary_df)

        confirmed_df = data.filter_by_disposition("CONFIRMED")
        print(f"Bulunan CONFIRMED gezegen satır sayısı: {len(confirmed_df)}")
    
        all_columns = data.get_columns()
        print("Tüm sütun isimleri:")
        print(all_columns)

        desired_columns = ["koi_disposition", "koi_period", "koi_depth"]
        subset_df = data.get_dataframe_with_columns(desired_columns)
        print("Seçilen sütunlardan oluşan DataFrame'in ilk 5 satırı:")
        print(subset_df.head()) 

    except FileNotFoundError:
        print(f"Error: File not found -> {EXOPLANET_DATA_FILE}")
    
    except pd.errors.ParserError:
        print(f"Error: Could not parse the file -> {EXOPLANET_DATA_FILE}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")