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
