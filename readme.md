

# YOLO Görsel Kontrol & Hızlı Ayırma Aracı

Bu betik, bir klasördeki görselleri **YOLO** ile (Ultralytics) anlık olarak işler, tespitleri ekranda gösterir ve klavye kısayollarıyla görselleri hızlıca:

* **silinenler** klasörüne (`w`)
* **revize** klasörüne (`s`)

taşımana olanak sağlar. Görselle aynı ada sahip **YOLO formatı** `.txt` label dosyası da **aynı işlemle birlikte** taşınır.

## Özellikler

* Ultralytics **YOLO** modeliyle tek tek görseller üzerinde inference
* Tespit kutularını ve sınıf/olasılık etiketlerini çizerek gösterim
* Klavye ile gezinme ve dosya taşıma:

  * `a` → önceki görsel
  * `d` → sonraki görsel
  * `w` → görsel + label’ı `deleted/` klasörüne taşı
  * `s` → görsel + label’ı `revise/` klasörüne taşı
  * `q` → çıkış
* Görsel taşındığında liste güncellenir; sonraki/önceki görsele otomatik geçilir

## Klasör Yapısı

```
.
├── best1.pt                # YOLO model dosyası (örnek ad)
├── images/                 # Kaynak görseller
│   ├── img_001.jpg
│   └── ...
├── labels/                 # YOLO label dosyaları (aynı isim tabanı)
│   ├── img_001.txt
│   └── ...
├── deleted/                # (Betik oluşturur) w ile taşınanlar buraya
├── revise/                 # (Betik oluşturur) s ile taşınanlar buraya
└── kontrol.py              # Bu betik (örnek isim)
```

> **Önemli:** `labels/` içindeki dosya adı, görsel dosya adıyla **taban adı** aynı olmalıdır.
> Örn. `images/img_001.jpg` ↔ `labels/img_001.txt`

## Gereksinimler

* Python 3.8+
* Paketler:

  * `ultralytics`
  * `opencv-python`

Kurulum:

```bash
pip install ultralytics opencv-python
```

> NVIDIA GPU kullanımı için ek sürücü/torch kurulumları gerekebilir; bu betik CPU’da da çalışır.

## Ayarlar

Betik başındaki parametreleri kendi yapına göre güncelle:

```python
MODEL_PATH = "best1.pt"        # YOLO model dosyası
IMAGE_DIR = "images"           # Görsellerin klasörü
LABEL_DIR = "labels"           # Label dosyalarının klasörü
DELETE_DIR = "deleted"         # Silinenlerin taşınacağı klasör
REVISE_DIR = "revise"          # Revizeye gidenlerin klasörü
CONFIDENCE_THRESHOLD = 0.5     # Tespit güven eşiği
```

## Çalıştırma

```bash
python kontrol.py
```

Pencere açıldıktan sonra kısayolları kullan:

* `a` : geri
* `d` : ileri
* `w` : **sil** (görsel + varsa label → `deleted/`)
* `s` : **revize** (görsel + varsa label → `revise/`)
* `q` : çık

Taşıma işlemi sonrası dosyalar hedef klasöre **fiziksel olarak taşınır** (kopyalanmaz).

## Nasıl Çalışır? (Kısa Akış)

1. Model yüklenir ve **sınıf isimleri** konsola yazdırılır.
2. `images/` klasöründeki tüm `.jpg/.jpeg/.png` dosyaları sıralanır.
3. Her görsel için YOLO inference yapılır, bulunan kutular ekranda çizilir.
4. Kullanıcı tuşuna göre:

   * **Geçiş** (`a/d`): sıradaki/önceki görsel yüklenir.
   * **Taşıma** (`w/s`): görsel ve eşleşen label `.txt` dosyası ilgili klasöre **shutil.move** ile taşınır.
   * **Çıkış** (`q`): pencere kapatılır, döngü sonlanır.

## Sorun Giderme

* **Pencere açılmıyor / Hata alıyorum**
  GUI gereksinimleri için sistemde masaüstü oturumu açık olmalı (headless ise `opencv-python-headless` yerine tam `opencv-python` kullan).
* **Tespit yok / sınıf isimleri boş**
  Model dosyan (ör. `best1.pt`) doğru mu, `model.names` dolu mu kontrol et.
* **Label taşınmıyor**
  Görsel ve label taban adlarının eşleştiğine emin ol (`img_001.jpg` ↔ `img_001.txt`).
  Label bulunamazsa yalnızca görsel taşınır; bu bir hataya sebep olmaz.
* **Performans yavaş**
  Büyük görsellerde inference yavaştır. Gerekirse görselleri önce küçült, ya da `CONFIDENCE_THRESHOLD` ayarla.

## Güvenlik Notu

* Taşıma işlemi **geri alınmaz**. Taşınan dosyaları geri almak için `deleted/` veya `revise/` klasörlerinden **manuel** olarak eski yerine taşıyabilirsin.

## Yol Haritası (İsteğe Bağlı İyileştirmeler)

* **Undo (Geri Al)**: Son işlemi `z` ile geri taşıma.
* **Zoom/Pan**: Yakınlaştırma ve sürükleme.
* **Oturum Kaydı**: Son kaldığın index’i `.state.json`’a yazma.
* **Loglama**: Her hareketi CSV’ye kaydetme (timestamp, action, file).
* **Sınıf/Skor Filtresi**: Belirli sınıfları veya skor aralığını gösterme.

---

İhtiyaç olursa bu betiğe **undo**, **zoom/pan**, **oturum kaydı** gibi özellikleri eklenmiş bir sürümünü de hazırlayabilirim.
