from lightkurve import search_lightcurve

class LightCurveData:
    def __init__(self, target_name, author="Kepler", cadence="long"):
        self.target_name = target_name
        self.author = author
        self.cadence = cadence
        self.search_result = search_lightcurve(self.target_name, author=self.author, cadence=self.cadence)
        self.lc = None
    
    def describe_search_result(self):
        return self.search_result

    def download_lightcurve(self):
        lc_collection = self.search_result.download_all()
        stitched = lc_collection.stitch()
        self.lc = stitched
    
    def plot(self):
        if self.lc:
            self.lc.plot()
    
    def normalize(self):
        if self.lc:
            self.lc = self.lc.normalize()
    
    def remove_outliers(self, sigma=5):
        if self.lc:
            self.lc = self.lc.remove_outliers(sigma=sigma)
    
    def flatten(self, window_length=401):
        if self.lc:
            self.lc = self.lc.flatten(window_length=window_length)
    
    def summary(self):
        if self.lc:
            print(self.lc)

    def save_csv(self, filename="lightcurve.csv"):
        if self.lc:
            df = self.lc.to_pandas()
            df.to_csv(filename, index=False)


def process_targets(target_list, author="Kepler", cadence="long", output_dir="lightcurves"):
    os.makedirs(output_dir, exist_ok=True)
    for target in target_list:
        try:
            print(f"İşleniyor: {target}")
            lc = LightCurveData(target, author=author, cadence=cadence)
            if len(lc.describe_search_result()) == 0:
                print(f"Uyarı: {target} için veri bulunamadı.")
                continue
            lc.download_lightcurve()
            lc.normalize()
            lc.remove_outliers()
            lc.flatten()
            save_path = os.path.join(output_dir, f"{target.replace('-', '_')}.csv")
            lc.save_csv(save_path)
            print(f"{target} başarıyla kaydedildi → {save_path}")
        except Exception as e:
            print(f"Hata: {target} işlenemedi. Sebep: {e}")

if __name__ == "__main__":
    target_ids = [
        "Kepler-8",
        "Kepler-10",
        "Kepler-22"
    ]

    # Kepler için: author="Kepler", cadence="long"
    # TESS için: author="SPOC" veya "QLP", cadence="short" genellikle
    process_targets(target_ids, author="Kepler", cadence="long")
