from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

def load_fits_data(fits_url):
    """
    Verilen FITS dosyası URL'sinden TIME ve PDCSAP_FLUX verilerini okur.

    Parameters:
        fits_url (str): FITS dosyasının URL'si.

    Returns:
        tuple: (tess_bjds, pdcsap_fluxes)
    """
    with fits.open(fits_url, mode="readonly") as hdulist:
        data = hdulist[1].data
        tess_bjds = data['TIME']
        pdcsap_fluxes = data['PDCSAP_FLUX']
    return tess_bjds, pdcsap_fluxes

def plot_light_curve(time, flux, t0, output_filename):
    """
    Işık eğrisi verilerini çizerek, transit zamanı olan t0 noktasını vurgular.

    Parameters:
        time (array-like): Zaman değerleri (TBJD).
        flux (array-like): PDCSAP flux değerleri (e-/s).
        t0 (float): Transit zamanının merkezi.
        output_filename (str): Kaydedilecek grafik dosyasının adı.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Veri noktalarını siyah dairelerle çiziyoruz.
    ax.plot(time, flux, 'ko', markersize=2, label="Flux")
    
    # x eksenini t0 etrafında +/- 1 gün olacak şekilde sınırlandırıyoruz.
    ax.set_xlim(t0 - 1.0, t0 + 1.0)
    
    # Transit zamanını kırmızı dikey çizgiyle gösteriyoruz.
    ax.axvline(x=t0, color="red", label="Transit Zamanı")
    
    # Grafik etiketleri ve başlığı.
    ax.set_xlabel("Time (TBJD)")
    ax.set_ylabel("PDCSAP Flux (e-/s)")
    ax.set_title("WASP-126 b Light Curve - Sector 1")
    ax.legend()
    
    # Sol kenar boşluğunu düzenleyerek y-etiketin görünmesini sağlıyoruz.
    plt.subplots_adjust(left=0.15)
    
    # Grafiği dosyaya kaydediyoruz.
    plt.savefig(output_filename)
    plt.close()
    print(f"Grafik '{output_filename}' dosyası olarak kaydedildi.")

def main():
    # FITS dosyasının URL'si.
    fits_file = 'https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/tess2018292075959-s0004-0000000025155310-0124-s_lc.fits'
    
    # FITS dosyası bilgilerini ve kolon isimlerini yazdırma.
    print("FITS Dosya Bilgileri:")
    fits.info(fits_file)
    data = fits.getdata(fits_file, ext=1)
    print("KOLONLAR:", data.columns)
    
    # Verileri yükle.
    tess_bjds, pdcsap_fluxes = load_fits_data(fits_file)
    
    # Transit zamanı; ihtiyaca göre değiştirilebilir.
    t0 = 1413.03

    # Grafiği çiz ve kaydet.
    output_filename = "lightcurve.png"
    plot_light_curve(tess_bjds, pdcsap_fluxes, t0, output_filename)

if __name__ == '__main__':
    main()
