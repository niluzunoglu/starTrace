# build_dataset.py
import numpy as np
import pandas as pd
from lightkurve import search_lightcurve
import warnings
warnings.filterwarnings("ignore")

MAX_LENGTH = 2048  # Sabit uzunluk

df = pd.read_csv("star_labels.csv")
X = []
y = []

label2int = {"CONFIRMED": 0, "CANDIDATE": 1, "FALSE POSITIVE": 2}

for i, row in df.iterrows():
    target, label, period = row["id"], row["label"], row["period"]

    try:
        result = search_lightcurve(target, mission="TESS").download_all()
        for lc in result:
            if "quality" in lc.colnames:
                lc.remove_column("quality")

        stitched = result.stitch()
        stitched = stitched.remove_nans().remove_outliers().normalize()
        flat = stitched.flatten(window_length=401)

        if not np.isnan(period):
            flat = flat.fold(period=period)

        flux = flat.flux[:MAX_LENGTH]

        if len(flux) < MAX_LENGTH:
            flux = np.pad(flux, (0, MAX_LENGTH - len(flux)))
        
        X.append(flux)
        y.append(label2int[label])

        print(f"[✓] {target} işlendi.")

    except Exception as e:
        print(f"[✗] {target} hatalı: {e}")
        continue

X = np.array(X)
y = np.array(y)
np.savez("lightcurves.npz", X=X, y=y)
print(f"[✅] Dataset hazır: X={X.shape}, y={y.shape}")
