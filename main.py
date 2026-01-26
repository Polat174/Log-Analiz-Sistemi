import yaml
import re
import csv
import time
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#--- KURALLARIN HAZIRLANMASI ---
def kural_yukle(kural_dosya="kurallar.yaml"):
    try:
        with open (kural_dosya,"r",encoding='utf-8')as f:
            config = yaml.safe_load(f)
            if config is None or 'rules' not in config:
                print(f"[!] {kural_dosya} içinde 'rules' bulunamadı!")
                return []
            
            kurallar = config['rules']
            for kural in kurallar:
                kural['re_obj'] = re.compile(kural['pattern'], re.IGNORECASE)
            return kurallar
    except FileNotFoundError:
        print(f"[!] {kural_dosya} dosyası dizinde bulunamadı!")
        return []
    except Exception as e:
        print(f"[!] Kurallar yükleneriken hata: {e}")
        return []
    
#--- ANALİZ MOTORU ---
def satir_analiz_et(satir, kurallar):
    for kural in kurallar:
        if kural['re_obj'].search(satir):
            return{
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "kural": kural['name'],
                "derece": kural['severity'],
                "mesaj": satir.strip()
            }
    return None

#--- RAPORLAMA (CSV) ---
def rapor_kaydet(tespitler, dosya_adi="Analiz_Raporu.csv"):
    if not tespitler: return
    anahtarlar = tespitler[0].keys()
    with open(dosya_adi,"a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=anahtarlar)
        writer.writeheader()
        writer.writerows(tespitler)
    print(f"\n[+] Rapor Kaydedildi: {os.path.abspath(dosya_adi)}")

#--- GERÇEK ZAMANLI İZLEME (WATCHDOG) ---
class LogIzleyici(FileSystemEventHandler):
    def __init__(self, kurallar):
        self.kurallar = kurallar
    def on_modified(self,event):
        if not event.is_directory:
            with open(event.src_path, "r") as f:
                satirlar = f.seek(0, os.SEEK_END)
                if satirlar:
                    son_satir = satirlar[-1]
                    sonuc = satir_analiz_et(son_satir, self.kurallar)
                    if sonuc:
                        print(f"\n[!] YENİ TESPİT: {sonuc['kural']} ({sonuc['derece']})")
                        print(f"--> {sonuc['mesaj']}")

#--- ANA MENÜ ---
def menu():
    kurallar = kural_yukle()
    print(f"[*] {len(kurallar)} adet kural yüklendi.")

    while True:
        print("\n--- LOG ANALİZ SİSTEMİ ---")
        print("1. Dosya Bazlı Analiz Yap (Özet & CSV)")
        print("2. Gerçek Zamanlı İzlemeyi Başlat")
        print("3. Çıkış")

        secim = input("Seçiminiz: ")

        if secim == "1":
            dosya = input("Analiz edilecek log dosya yolu: ")
            if os.path.exists(dosya):
                tespitler =[]
                with open(dosya,"r") as f:
                    for satir in f:
                        res = satir_analiz_et(satir, kurallar)
                        if res: tespitler.append(res)

                print(f"\n Analiz bitti. {len(tespitler)}zafiyet bulundu.")
                rapor_kaydet(tespitler)
            else:
                print("[!] Dosya Bulunamadi!")

        elif secim == "2":
            dizin = input("İzlenecek dizin (örn: ./logs): ")
            print("[*] İzleme başlatıldı (Durdurmak için Ctrl+C)...")
            handler = LogIzleyici(kurallar)
            obs = Observer()
            obs.schedule(handler, path=dizin, recursive=False)
            obs.start()
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt:
                obs.stop()
            obs.join()
        
        elif secim == "3":
            break

if __name__ == "__main__":
    menu()
