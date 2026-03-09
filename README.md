# 🎵 Duplicate Music Cleaner

> **Find, review, and delete duplicate music files — fast, safe, and smart.**

A desktop application built with Python that scans your music library, detects exact duplicate audio files using MD5 hashing, and lets you review them with metadata before deciding what to delete.

---

## ✨ Features

- 🔍 **Exact duplicate detection** via MD5 hash — works regardless of file name
- 🎧 **Supports all major audio formats** — MP3, FLAC, WAV, AAC, OGG, M4A, WMA, OPUS, AIFF, APE
- 📊 **Metadata display** — file size, duration, bitrate (requires `mutagen`)
- 🏆 **Smart auto-select** — automatically marks lower-quality copies for deletion, keeps the best
- 📁 **Group view** — browse duplicate groups and inspect each file before acting
- 📤 **JSON report export** — save a full duplicate report without deleting anything
- 🗑️ **Safe deletion** — confirmation dialog before any file is permanently removed
- 🌑 **Dark UI** — clean, modern interface built with Tkinter

---

## 📸 Screenshot

> *Coming soon — feel free to add a screenshot here!*

---

## 🚀 Getting Started

### Requirements

- Python 3.8+
- `mutagen` *(optional, but recommended for metadata)*

### Installation

```bash
git clone https://github.com/yourusername/duplicate-music-cleaner.git
cd duplicate-music-cleaner

# Optional: install mutagen for bitrate/duration info
pip install mutagen
```

### Run

```bash
python duplicate_music_cleaner.py
```

---

## 🛠️ How It Works

1. **Select a folder** — choose the root of your music library
2. **Scan** — the app recursively walks the folder and hashes every audio file
3. **Review** — duplicate groups are listed; click a group to inspect files
4. **Select** — manually check files, or use *"Keep Best"* / *"Auto-select All"*
5. **Delete** — confirm and remove the selected files permanently

---

## 📦 Supported Formats

| Format | Extension |
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

## ⚠️ Disclaimer

Deleted files are **permanently removed** from disk (not sent to trash). Always review your selection carefully before confirming deletion.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome! Feel free to open an issue for bugs, feature requests, or ideas.
