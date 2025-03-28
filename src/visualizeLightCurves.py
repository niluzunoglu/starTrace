from lightkurve import search_lightcurve
import matplotlib.pyplot as plt

target = "TIC 25155310"
lc_collection = search_lightcurve(target, mission="TESS")
print("LC Collection : ", lc_collection)
lc = lc_collection.stitch()

lc.plot()
plt.title("Light Curve for {}".format(target))
plt.show()
