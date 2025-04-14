import pandas as pd
from astroquery.mast import Observations
import time # Olası hız limitleri için gerekebilir

def fast_check_data_availability(csv_path, limit=100):
    """
    Verilen CSV dosyasındaki hedefler için MAST arşivinde veri olup olmadığını
    hızlıca kontrol eder. Sadece varlık kontrolü yapar, veri indirmez.

    Args:
        csv_path (str): Hedef listesini içeren CSV dosyasının yolu.
                        'id', 'source' kolonlarını içermelidir.
        limit (int, optional): İşlenecek maksimum satır sayısı. 
                               None ise tüm satırlar işlenir. Defaults to 100.
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ CSV dosyası okundu: {csv_path} ({len(df)} satır)")
    except FileNotFoundError:
        print(f"❌ Hata: CSV dosyası bulunamadı: {csv_path}")
        return
    except Exception as e:
        print(f"❌ CSV okuma hatası: {e}")
        return

    count_found = 0
    count_not_found = 0
    count_error = 0
    count_unknown_source = 0
    total_processed = 0

    # Daha verimli satır iterasyonu için itertuples kullan
    # index=False -> Tuple içinde index istemiyoruz
    # name=None -> Standart tuple döndürür (Pandas Row değil)
    for i, row_tuple in enumerate(df.itertuples(index=False, name=None)):
        
        # Sütun adlarına göre index'leri bul (güvenli yöntem)
        try:
            id_index = df.columns.get_loc('id')
            source_index = df.columns.get_loc('source')
            target_id_raw = row_tuple[id_index]
            source = str(row_tuple[source_index]).lower().strip()
        except KeyError as e:
            print(f"❌ Hata: CSV dosyasında gerekli sütun bulunamadı: {e}")
            return # Fonksiyondan çıkalım, format yanlış
        except Exception as e:
            print(f"❌ Satır {i+1} işlenirken hata: {e}")
            count_error += 1
            continue # Sonraki satıra geç

        if limit is not None and i >= limit:
            print(f"\n⚠️ İşlem limiti ({limit} satır) doldu.")
            break

        total_processed += 1
        target_name = None
        obs_collection = None

        # Hedef ID ve Misyon (obs_collection) belirleme
        if source == "kepler":
            try:
                # Kepler ID'leri genellikle integer'dır. CSV'den float gelmişse çevir.
                target_name = str(int(target_id_raw))
                obs_collection = "Kepler"
            except ValueError:
                print(f"⚠️ [{target_id_raw}] Geçersiz Kepler ID formatı.")
                count_not_found += 1 # Hatalı formatı bulunamadı sayalım
                continue
        elif source == "tess":
            # TESS ID'leri genellikle TIC ID'leridir (integer).
            # Sizin verinizdeki '1000.01' gibi ID'ler TOI olabilir.
            # MAST sorgusu için genellikle 'TIC <ID>' veya sadece ID (TESS collection ile) kullanılır.
            # TOI sorgusu da bazen çalışır: 'TOI <ID>'
            # Verinizdeki ID'nin tam olarak neyi temsil ettiğine göre ayarlamak gerekebilir.
            # Örnek: Verideki ID'nin TOI olduğunu varsayalım (sizin kodunuzdaki gibi)
            # target_name = f"TOI {target_id_raw}" 
            # VEYA daha yaygın: Sadece TESS ID (genellikle TIC)
            try:
                 # Eğer TESS ID'leriniz aslında TIC ID ise ve float olarak okunduysa:
                 tic_id = str(int(float(target_id_raw))) 
                 target_name = tic_id # Sadece ID vermek TESS collection ile genelde yeterli
                 # VEYA target_name = f"TIC {tic_id}"
                 obs_collection = "TESS"
            except ValueError:
                 # Belki de ID gerçekten '1000.01' gibi özel bir formattadır? O zaman string bırakalım.
                 # Veya TOI formatını deneyelim:
                 target_name = f"TOI {str(target_id_raw).replace('.01', '')}" # .01'i temizlemeyi deneyelim?
                 print(f"ℹ️ [{target_id_raw}] TESS ID formatı belirsiz, '{target_name}' olarak deneniyor.")
                 obs_collection = "TESS"
            # target_name = str(target_id_raw) # En basit haliyle ID'yi string yapalım
            # obs_collection = "TESS"
        else:
            print(f"❓ [{target_id_raw}] Bilinmeyen kaynak: {source}")
            count_unknown_source += 1
            count_not_found += 1 # Bilinmeyen kaynağı bulunamadı sayalım
            continue

        print(f"🔍 {i+1}. MAST Sorgulama: Hedef='{target_name}', Misyon='{obs_collection}'")

        try:
            # Observations.query_criteria en temel sorgu yöntemidir.
            # Sadece hedef adı ve misyon bilgisi ile sorguluyoruz.
            # dataproduct_type='timeseries' eklemeden sorgu daha genel ve hızlı olabilir.
            # Bu sorgu, o hedefe ait o misyondan *herhangi bir* gözlem (LC, TPF, FFI vb.) var mı diye bakar.
            obs_table = Observations.query_criteria(
                target_name=target_name,
                obs_collection=obs_collection
                # Kesinlikle sadece işlenmiş ışık eğrisi var mı diye bakmak isterseniz:
                # dataproduct_type="timeseries"
            )

            if len(obs_table) > 0:
                # print(f"✅ Bulundu ({len(obs_table)} gözlem kaydı)")
                count_found += 1
            else:
                # print(f"❌ Bulunamadı")
                count_not_found += 1

            # MAST'a çok hızlı istek atmamak için küçük bir bekleme (opsiyonel)
            # time.sleep(0.05) # 50 milisaniye bekle

        except Exception as e:
            # Bağlantı hataları, sorgu hataları vb. yakala
            print(f"❌ Hata (Hedef: {target_name}, Kaynak: {source}): {e}")
            count_error += 1
            count_not_found += 1 # Hata durumunda bulunamadı sayalım

    print("\n📊 MAST Veri Varlık Kontrol Sonuçları")
    print(f"-----------------------------------------")
    print(f"İşlenen Toplam Satır       : {total_processed}")
    print(f"Veri Bulunan Hedef Sayısı  : {count_found}")
    print(f"Veri Bulunamayan Hedef Say.: {count_not_found}")
    print(f"   (Bilinmeyen kaynaklar)  : {count_unknown_source}")
    print(f"   (Sorgu/Format Hataları) : {count_error}")
    print(f"-----------------------------------------")
    print(f"(Not: 'Bulunan', hedef için ilgili misyondan *herhangi bir* MAST gözleminin bulunduğunu gösterir.)")

if __name__ == "__main__":
    # Kendi dosya yolunuzla değiştirin
    #csv_file_path = "/content/drive/MyDrive/starTrace/data/multimission/MERGED/kepler_and_tess_with_sources.csv" 
    
    csv_file_path = "../../data/multimission/MERGED/kepler_and_tess_with_sources.csv" 

    # İlk 100 hedefi test etmek için:
    fast_check_data_availability(csv_file_path, limit=100)

    # Tüm veriyi işlemek için:
    # fast_check_data_availability(csv_file_path, limit=None)