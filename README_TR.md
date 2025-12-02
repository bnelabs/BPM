# BPM - Kan Basıncı Değişkenlik Analiz Aracı

<p align="center">
  <img src="resources/icons/logo.png" alt="BPM Logo" width="128" height="128">
</p>

<p align="center">
  <strong>Excel verilerinizden kan basıncı değişkenlik analizini saniyeler içinde yapın</strong>
</p>

<p align="center">
  <a href="#hekimler-için">Hekimler İçin</a> •
  <a href="#kullanım-kılavuzu">Kullanım Kılavuzu</a> •
  <a href="#kurulum">Kurulum</a> •
  <a href="#teknik-bilgiler">Teknik Bilgiler</a> •
  <a href="README.md">🇬🇧 English</a>
</p>

---

## Bu Uygulama Ne İşe Yarar?

BPM, kardiyologlar ve sağlık profesyonelleri için geliştirilmiş bir **kan basıncı değişkenlik analiz** aracıdır. Sadece ortalama tansiyon değerlerine bakmak yerine, tansiyonun nasıl dalgalandığını analiz eder - bu da kardiyovasküler risk değerlendirmesinde kritik bir parametredir.

### Problem

Geleneksel tansiyon analizi sadece ortalamalara odaklanır. Oysa güncel araştırmalar, **tansiyonun ne kadar dalgalandığının** (değişkenlik) kardiyovasküler riski öngörmede en az ortalama değerler kadar önemli olduğunu göstermektedir.

Bu değişkenlik metriklerini Excel'den elle hesaplamak:

- **Çok zaman alır** (özellikle yüzlerce hasta için)
- **Hata riski yüksektir**
- **İstatistik bilgisi gerektirir**

### Çözüm

BPM, tüm klinik öneme sahip kan basıncı değişkenlik metriklerini Excel dosyanızdan otomatik olarak hesaplar. Sürükle-bırak arayüzü sayesinde herkes kolayca kullanabilir.

---

## Hekimler İçin

### Hesaplanan Metrikler

| Metrik | Açıklama | Klinik Önemi |
|--------|----------|--------------|
| **Ortalama SKB/DKB** | Ortalama sistolik/diyastolik basınç | Bazal tansiyon düzeyi |
| **SD (Standart Sapma)** | Ölçümlerin ortalamadan sapması | Genel değişkenlik göstergesi |
| **CV (Varyasyon Katsayısı)** | SD'nin ortalamaya oranı (%) | Hastalar arası karşılaştırma |
| **ARV (Ortalama Gerçek Değişkenlik)** | Ardışık ölçümler arası ortalama fark | Kısa dönem dalgalanmalar |
| **Ağırlıklı SD** | Gündüz/gece SD'nin saat ağırlıklı ortalaması | Dipping etkisini nötralize eder |
| **Noktürnal Dipping %** | Gece/gündüz tansiyon düşüşü | Kardiyovasküler risk belirteci |
| **Sabah Atağı** | Gece en düşük değerden sabah yükselişi | İnme ve MI riski |
| **HT Evresi** | AHA/ACC sınıflandırması | Tedavi planlaması |

### Noktürnal Dipping Sınıflandırması

| Kategori | Tanım | Risk Durumu |
|----------|-------|-------------|
| Normal Dipper | %10-20 gece düşüşü | Normal |
| Non-Dipper | <%10 düşüş | Artmış KV risk |
| Extreme Dipper | >%20 düşüş | Noktürnal hipotansiyon riski |
| Reverse Dipper | Gece > Gündüz | En yüksek KV risk |

### Bilimsel Dayanak

Uygulama, aşağıdaki kaynaklara dayanan metodoloji kullanmaktadır:

- Grillo ve ark., J Clin Hypertens 2015 (DOI: 10.1111/jch.12551)
- Parati ve ark., J Clin Hypertens 2018 (DOI: 10.1111/jch.13304)
- ESH/ESC Ambulatuvar Kan Basıncı İzleme Kılavuzları

---

## Kullanım Kılavuzu

### Adım Adım Kullanım

#### 1. Uygulamayı Başlatın
Masaüstündeki BPM simgesine çift tıklayın.

#### 2. Excel Dosyasını Yükleyin
- Excel dosyanızı uygulama penceresine **sürükleyip bırakın**
- Ya da **"Dosya Seç"** butonuna tıklayın

#### 3. Sütunları Eşleştirin
Uygulama sütunları otomatik algılar. Kontrol edin:
- **Hasta No** sütunu
- **Tarih/Saat** sütunu
- **Sistolik KB** sütunu (büyük değer)
- **Diyastolik KB** sütunu (küçük değer)

Yanlış eşleşme varsa açılır menüden düzeltin.

#### 4. Analizi Başlatın
**"Analiz Et"** butonuna tıklayın. Tüm hastalar otomatik işlenir.

#### 5. Sonuçları Kaydedin
- **"Excel'e Aktar"** - Detaylı sonuç tablosu
- **"PDF Rapor"** - Yazdırılabilir özet rapor

### Desteklenen Excel Formatları

BPM her türlü Excel dosyasıyla çalışır. Gerekli sütunlar:

| Alan | Örnek Sütun Adları |
|------|-------------------|
| Hasta No | "Hasta No", "Protokol", "TC", "ID" |
| Tarih/Saat | "Tarih", "Saat", "Ölçüm Zamanı" |
| Sistolik | "SKB", "Sistolik", "Büyük Tansiyon" |
| Diyastolik | "DKB", "Diyastolik", "Küçük Tansiyon" |

**Opsiyonel:** Nabız, Not

### Örnek Veri Formatı

| Hasta_No | Tarih | Saat | SKB | DKB | Nabız |
|----------|-------|------|-----|-----|-------|
| H001 | 15.01.2024 | 08:00 | 142 | 88 | 72 |
| H001 | 15.01.2024 | 12:00 | 138 | 85 | 68 |
| H001 | 15.01.2024 | 18:00 | 145 | 90 | 75 |
| H002 | 15.01.2024 | 09:30 | 128 | 82 | 65 |

---

## Kurulum

### Seçenek 1: Hazır Uygulama (Önerilen)

[GitHub Releases](https://github.com/bnelabs/BPM/releases) sayfasından işletim sisteminize uygun dosyayı indirin.

**Windows:**
1. `BPM-Windows.exe` dosyasını indirin
2. Çift tıklayarak çalıştırın

**macOS:**
1. `BPM-macOS.zip` dosyasını indirin
2. Zip'i açın, BPM'i Uygulamalar klasörüne taşıyın
3. İlk açılışta sağ tık → "Aç" seçin (Gatekeeper uyarısı için)

**Linux:**
1. `BPM-Linux` dosyasını indirin
2. Çalıştırma izni verin: `chmod +x BPM-Linux`
3. Çalıştırın: `./BPM-Linux`

### Seçenek 2: Kurulum Betikleri

**Linux (Ubuntu/Debian/Fedora/Arch):**
```bash
git clone https://github.com/bnelabs/BPM.git
cd BPM
./scripts/install-linux.sh
```

**macOS:**
```bash
git clone https://github.com/bnelabs/BPM.git
cd BPM
./scripts/install-macos.sh
```

**Windows (PowerShell - Yönetici):**
```powershell
git clone https://github.com/bnelabs/BPM.git
cd BPM
.\scripts\install-windows.ps1
```

### Seçenek 3: Python ile Kurulum

```bash
git clone https://github.com/bnelabs/BPM.git
cd BPM

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
python src/main.py
```

### Seçenek 4: Docker

#### Web Tarayıcı ile Erişim (Her Platformda Çalışır)

```bash
docker compose -f docker-compose.vnc.yml up -d
```

Tarayıcıda açın: **http://localhost:6080/vnc.html**

Bu yöntem Windows, macOS ve Linux'ta çalışır. Aynı ağdaki başka bilgisayarlardan da erişilebilir.

#### X11 ile (Sadece Linux)

```bash
docker build -t bpm .
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/data:/app/data \
    bpm
```

---

## Teknik Bilgiler

### Proje Yapısı

```
BPM/
├── src/
│   ├── main.py                 # Ana giriş noktası
│   ├── core/
│   │   └── translations.py     # Türkçe/İngilizce dil desteği
│   ├── analysis/
│   │   └── metrics.py          # KB değişkenlik hesaplamaları
│   ├── data_io/
│   │   ├── excel_reader.py     # Excel okuyucu
│   │   └── report_generator.py # PDF rapor oluşturucu
│   └── ui/
│       ├── main_window.py      # Kullanıcı arayüzü
│       └── styles.qss          # Görsel tema
├── .github/workflows/
│   └── build.yml               # Otomatik derleme (CI/CD)
├── Dockerfile.vnc              # Docker VNC yapılandırması
└── requirements.txt            # Python bağımlılıkları
```

### Kullanılan Teknolojiler

| Bileşen | Teknoloji |
|---------|-----------|
| Programlama Dili | Python 3.10+ |
| Arayüz | PySide6 (Qt 6) |
| Veri İşleme | Pandas, NumPy |
| İstatistik | SciPy |
| Excel | openpyxl |
| Grafikler | Matplotlib |
| PDF | ReportLab |

### Formüller

**Standart Sapma (SD):**
```
SD = √[Σ(xi - x̄)² / (n-1)]
```

**Varyasyon Katsayısı (CV):**
```
CV = (SD / Ortalama) × 100
```

**Ortalama Gerçek Değişkenlik (ARV):**
```
ARV = Σ|KB[i+1] - KB[i]| / (n-1)
```

**Ağırlıklı SD:**
```
Ağırlıklı SD = (SD_gündüz × saat_gündüz + SD_gece × saat_gece) / 24
```

**Noktürnal Dipping:**
```
Dipping % = ((Ort_gündüz - Ort_gece) / Ort_gündüz) × 100
```

### Zaman Dilimleri

- **Gündüz:** 08:00 - 22:00
- **Gece:** 00:00 - 06:00
- **Sabah periyodu:** 06:00 - 10:00

### Veri Güvenliği

- **Tamamen yerel çalışır** - Verileriniz bilgisayarınızdan çıkmaz
- **İnternet gerektirmez** - Çevrimdışı kullanılabilir
- **Veri toplamaz** - Hiçbir telemetri yoktur
- **Açık kaynak** - Kodu inceleyebilirsiniz

---

## Derleme

### Windows

```powershell
cd BPM
.\scripts\build-windows.ps1
# Çıktı: dist\BPM.exe
```

### Linux / macOS

```bash
cd BPM
./scripts/build.sh
# Çıktı: dist/BPM (Linux) veya dist/BPM.app (macOS)
```

---

## Otomatik Derleme (GitHub Actions)

Her yeni sürüm etiketi (`v1.0.0` gibi) oluşturulduğunda GitHub Actions otomatik olarak:

1. Windows, macOS ve Linux için derleme yapar
2. Çalıştırılabilir dosyaları oluşturur
3. GitHub Releases sayfasına yükler

Manuel derleme için GitHub'da **Actions** sekmesinden tetikleyebilirsiniz.

---

## Dil Seçenekleri

Uygulama **Türkçe** ve **İngilizce** destekler. Dil değiştirmek için arayüzdeki 🌐 butonunu kullanın.

**Türkçe ayarları:**
- Ondalık ayırıcı: virgül (,)
- Binlik ayırıcı: nokta (.)
- Tarih formatı: GG.AA.YYYY

**İngilizce ayarları:**
- Ondalık ayırıcı: nokta (.)
- Binlik ayırıcı: virgül (,)
- Tarih formatı: YYYY-MM-DD

---

## Lisans

MIT Lisansı - Detaylar için LICENSE dosyasına bakın.

---

## Destek ve İletişim

- **Hata bildirimi:** [GitHub Issues](https://github.com/bnelabs/BPM/issues)
- **Dokümantasyon:** [GitHub Wiki](https://github.com/bnelabs/BPM/wiki)

---

<p align="center">
  <em>Kardiyovasküler sağlık için geliştirildi</em>
</p>
