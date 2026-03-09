# 🎵 Duplicate Music Cleaner — Kopya Müzik Temizleyici

> **Müzik kütüphanenizdeki kopya dosyaları bulun, inceleyin ve güvenle silin.**

Python ile geliştirilmiş bir masaüstü uygulamasıdır. MD5 hash algoritmasını kullanarak birebir aynı ses dosyalarını tespit eder; metadata bilgileriyle birlikte görüntüleyip hangi kopyaları sileceğinize karar vermenizi sağlar.

---

## ✨ Özellikler

- 🔍 **Kesin kopya tespiti** — MD5 hash ile, dosya adından bağımsız olarak çalışır
- 🎧 **Tüm popüler ses formatlarını destekler** — MP3, FLAC, WAV, AAC, OGG, M4A, WMA, OPUS, AIFF, APE
- 📊 **Metadata görüntüleme** — dosya boyutu, süre, bitrate (`mutagen` gerektirir)
- 🏆 **Akıllı otomatik seçim** — düşük kaliteli kopyaları otomatik işaretler, en iyisini tutar
- 📁 **Grup görünümü** — kopya gruplarına göz atın, silmeden önce her dosyayı inceleyin
- 📤 **JSON rapor dışa aktarma** — hiçbir şeyi silmeden tüm kopya raporunu kaydedin
- 🗑️ **Güvenli silme** — kalıcı silme işlemi öncesinde onay ekranı gösterilir
- 🌑 **Karanlık arayüz** — Tkinter ile oluşturulmuş sade ve modern tasarım

---

## 📸 Ekran Görüntüsü

> *Yakında eklenecek — buraya bir ekran görüntüsü ekleyebilirsiniz!*

---

## 🚀 Başlangıç

### Gereksinimler

- Python 3.8 veya üzeri
- `mutagen` *(isteğe bağlı, metadata için tavsiye edilir)*

### Kurulum

```bash
git clone https://github.com/kullaniciadi/duplicate-music-cleaner.git
cd duplicate-music-cleaner

# İsteğe bağlı: bitrate ve süre bilgisi için mutagen
pip install mutagen
```

### Çalıştırma

```bash
python duplicate_music_cleaner.py
```

---

## 🛠️ Nasıl Çalışır?

1. **Klasör seçin** — müzik kütüphanenizin ana klasörünü seçin
2. **Tarayın** — uygulama tüm ses dosyalarını özyinelemeli olarak tarar ve hash'ler
3. **İnceleyin** — kopya grupları listelenir; bir gruba tıklayarak dosyaları görüntüleyin
4. **Seçin** — dosyaları manuel olarak işaretleyin ya da *"En İyisini Tut"* / *"Tümünü Seç"* butonlarını kullanın
5. **Silin** — onaylayın ve seçili dosyaları kalıcı olarak kaldırın

---

## 📦 Desteklenen Formatlar

| Format | Uzantı    |
|--------|-----------|
| MP3    | `.mp3`    |
| FLAC   | `.flac`   |
| WAV    | `.wav`    |
| AAC    | `.aac`    |
| OGG    | `.ogg`    |
| M4A    | `.m4a`    |
| WMA    | `.wma`    |
| OPUS   | `.opus`   |
| AIFF   | `.aiff`   |
| APE    | `.ape`    |

---

## ⚠️ Uyarı

Silinen dosyalar **kalıcı olarak diskten kaldırılır** (çöp kutusuna gönderilmez). Silme işlemini onaylamadan önce seçiminizi dikkatlice gözden geçirin.

---

## 📄 Lisans

MIT Lisansı — özgürce kullanabilir, değiştirebilir ve dağıtabilirsiniz.

---

## 🤝 Katkı

Pull request'ler memnuniyetle kabul edilir! Hata, öneri veya fikir için issue açabilirsiniz.
