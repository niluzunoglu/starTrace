from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

def load_fits_data(fits_url):
    """
    Verilen FITS dosyası URL'sinden ilgili sütunları okur.
    
    Parametreler:
        fits_url (str): FITS dosyasının URL'si.
        
    Dönüşler:
        tuple: (tess_bjds, qual_flags, sap_fluxes, pdcsap_fluxes)
    """
    with fits.open(fits_url, mode="readonly") as hdulist:
        data = hdulist[1].data
        qual_flags = data['QUALITY']
        tess_bjds = data['TIME']
        sap_fluxes = data['SAP_FLUX']
        pdcsap_fluxes = data['PDCSAP_FLUX']
    return tess_bjds, qual_flags, sap_fluxes, pdcsap_fluxes

def plot_light_curve_with_quality(time, flux, quality, output_filename):
    """
    Işık eğrisi verilerini çizip, kalite bayrağı (QUALITY > 0) olan noktaları vurgular.
    
    Parametreler:
        time (array-like): Zaman verileri (TBJD).
        flux (array-like): PDCSAP flux değerleri (e-/s).
        quality (array-like): Kalite bayrağı değerleri.
        output_filename (str): Kaydedilecek grafik dosyasının adı.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Tüm flux verilerini siyah dairelerle çiz.
    ax.plot(time, flux, 'ko', markersize=2, label="PDCSAP Flux")
    
    # Kalite bayrağı 0'dan büyük olan indeksleri belirle.
    bad_indices = np.where(quality > 0)[0]
    
    # Kalite bayrağı olan flux değerlerini kırmızı dairelerle işaretle.
    ax.plot(time[bad_indices], flux[bad_indices], 'ro', markersize=2, label="Kalite Bayrağı (QUALITY > 0)")
    
    # Grafik başlığı, etiketler ve lejand ayarları.
    fig.suptitle("WASP-126 b Light Curve - Sector 1")
    ax.set_xlabel("Time (TBJD)")
    ax.set_ylabel("PDCSAP Flux (e-/s)")
    ax.legend()
    
    # Sol kenar boşluğunu düzenleyerek y-ekseninin etiketinin görünmesini sağla.
    plt.subplots_adjust(left=0.15)
    
    # Grafiği belirtilen dosya ismiyle kaydet.
    plt.savefig(output_filename)
    plt.close()
    print(f"Grafik '{output_filename}' dosyası olarak kaydedildi.")

def main():
    # FITS dosyasının URL'si.
    fits_file = 'https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/tess2018292075959-s0004-0000000025155310-0124-s_lc.fits'
    
    # FITS dosyası hakkında bilgi yazdır ve kolonları listele.
    print("FITS Dosya Bilgileri:")
    fits.info(fits_file)
    data = fits.getdata(fits_file, ext=1)
    print("KOLONLAR:", data.columns)
    
    # Verileri yükle.
    tess_bjds, qual_flags, sap_fluxes, pdcsap_fluxes = load_fits_data(fits_file)
    
    # Grafiği çiz ve kaydet.
    output_filename = "lightcurve2.png"
    plot_light_curve_with_quality(tess_bjds, pdcsap_fluxes, qual_flags, output_filename)

if __name__ == '__main__':
    main()
