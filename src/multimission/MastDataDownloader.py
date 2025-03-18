import pandas as pd
from astroquery.mast import Observations
from astropy.coordinates import SkyCoord
import astropy.units as u
import os

class MastDataDownloader:

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)  # Dizini oluştur

    def download_data(self, target_name, radius=0.02, units="deg", mission="TESS", product_type="LC"):
        """
        MAST'tan hedef yıldızın verilerini indirir.

        Args:
            target_name (str): Hedef yıldızın adı.
            radius (float, optional): Arama yarıçapı. Varsayılan: 0.02.
            units (str, optional): Yarıçapın birimi (deg veya arcmin). Varsayılan: "deg".
            mission (str, optional): Teleskop görevi (TESS, Kepler, vb.). Varsayılan: "TESS".
            product_type (str, optional): Veri ürün tipi (LC, spectra, images). Varsayılan: "LC".
        """
        try:
            coord = SkyCoord.from_name(target_name)
            radius_unit = u.Unit(units)
            radius_value = radius * radius_unit

            observations = Observations.query_region(coord, radius=radius_value)

            lightcurve_products = Observations.get_product_list(observations)
            filtered_products = Observations.filter_products(lightcurve_products, productType=[product_type])

            data_urls = Observations.get_download_links(filtered_products)
            mission_dir = os.path.join(self.data_dir, mission)
            os.makedirs(mission_dir, exist_ok=True)
            Observations.download_products(filtered_products, download_dir=mission_dir)
            print(f"{target_name} için {mission} görevine ait veriler başarıyla {mission_dir} dizinine indirildi.")

        except Exception as e:
            print(f"{target_name} için {mission} görevine ait veri indirme sırasında bir hata oluştu: {e}")


if __name__ == "__main__":

    downloader = MastDataDownloader(data_dir="mast_data")  # Verilerin kaydedileceği ana dizin
    downloader.download_data(target_name="Kepler-10", mission="TESS")
    downloader.download_data(target_name="Kepler-10", mission="Kepler")

    #downloader.download_data(target_name="M31", mission="HST", product_type="images")