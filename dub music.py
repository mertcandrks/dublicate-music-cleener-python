#!/usr/bin/env python3
"""
🎵 Duplicate Music Cleaner
Müzik dosyalarındaki kopyaları tespit edip temizler.
"""

import os
import sys
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from collections import defaultdict
import json
import time

# --- Opsiyonel: mutagen ile ID3/metadata okuma ---
try:
    from mutagen import File as MutagenFile
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

MUSIC_EXTENSIONS = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.opus', '.aiff', '.ape'}

# ─────────────────────────────────────────────
#  Yardımcı fonksiyonlar
# ─────────────────────────────────────────────

def file_hash(path: str, chunk_size: int = 65536) -> str:
    """Dosyanın MD5 hash'ini döndürür."""
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

def get_audio_info(path: str) -> dict:
    """Dosya meta verilerini döndürür."""
    info = {
        'title': '',
        'artist': '',
        'duration': 0,
        'bitrate': 0,
        'size': os.path.getsize(path),
    }
    if HAS_MUTAGEN:
        try:
            audio = MutagenFile(path, easy=True)
            if audio:
                info['title'] = str(audio.get('title', [''])[0])
                info['artist'] = str(audio.get('artist', [''])[0])
                if hasattr(audio, 'info'):
                    info['duration'] = round(getattr(audio.info, 'length', 0), 1)
                    info['bitrate'] = getattr(audio.info, 'bitrate', 0)
        except Exception:
            pass
    return info

def human_size(n: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

def scan_folder(folder: str, progress_cb=None) -> dict:
    """
    Klasörü tarar, hash'e göre gruplar.
    Döner: { hash: [path, ...], ... }  (sadece >= 2 dosya olanlar)
    """
    hash_map = defaultdict(list)
    all_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            if Path(f).suffix.lower() in MUSIC_EXTENSIONS:
                all_files.append(os.path.join(root, f))

    total = len(all_files)
    for i, path in enumerate(all_files, 1):
        try:
            h = file_hash(path)
            hash_map[h].append(path)
        except (PermissionError, OSError):
            pass
        if progress_cb:
            progress_cb(i, total)

    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎵 Duplicate Music Cleaner")
        self.geometry("950x680")
        self.minsize(760, 520)
        self.configure(bg="#0f0f14")
        self._setup_styles()
        self._build_ui()
        self.duplicates: dict = {}          # hash -> [paths]
        self.checked_vars: dict = {}        # path -> BooleanVar
        self.to_delete: list = []

    # ── Styles ──────────────────────────────
    def _setup_styles(self):
        self.colors = {
            'bg':       '#0f0f14',
            'surface':  '#1a1a24',
            'border':   '#2e2e42',
            'accent':   '#7c5cfc',
            'accent2':  '#fc5c7d',
            'text':     '#e8e6f0',
            'muted':    '#7a788a',
            'success':  '#4ade80',
            'warning':  '#fb923c',
        }
        s = ttk.Style(self)
        s.theme_use('clam')
        bg, sf, bd, acc, txt, mut = (
            self.colors['bg'], self.colors['surface'], self.colors['border'],
            self.colors['accent'], self.colors['text'], self.colors['muted']
        )
        s.configure('TFrame', background=bg)
        s.configure('Surface.TFrame', background=sf)
        s.configure('TLabel', background=bg, foreground=txt, font=('Segoe UI', 10))
        s.configure('Header.TLabel', background=bg, foreground=txt, font=('Segoe UI', 18, 'bold'))
        s.configure('Sub.TLabel', background=bg, foreground=mut, font=('Segoe UI', 9))
        s.configure('Stat.TLabel', background=sf, foreground=txt, font=('Segoe UI', 11, 'bold'))
        s.configure('StatSub.TLabel', background=sf, foreground=mut, font=('Segoe UI', 8))
        s.configure('Accent.TButton',
                    background=acc, foreground='white',
                    font=('Segoe UI', 10, 'bold'), relief='flat', padding=(16, 8))
        s.map('Accent.TButton', background=[('active', '#9b7dff'), ('pressed', '#6040e0')])
        s.configure('Danger.TButton',
                    background=self.colors['accent2'], foreground='white',
                    font=('Segoe UI', 10, 'bold'), relief='flat', padding=(16, 8))
        s.map('Danger.TButton', background=[('active', '#ff7a95')])
        s.configure('Ghost.TButton',
                    background=sf, foreground=txt,
                    font=('Segoe UI', 9), relief='flat', padding=(10, 6))
        s.map('Ghost.TButton', background=[('active', bd)])
        s.configure('TProgressbar', troughcolor=bd, background=acc, thickness=6)
        s.configure('Treeview',
                    background=sf, foreground=txt, fieldbackground=sf,
                    rowheight=28, font=('Segoe UI', 9), relief='flat', borderwidth=0)
        s.configure('Treeview.Heading',
                    background=bd, foreground=mut, font=('Segoe UI', 9, 'bold'), relief='flat')
        s.map('Treeview', background=[('selected', acc)])

    # ── UI Build ─────────────────────────────
    def _build_ui(self):
        c = self.colors

        # ── Header ──
        hdr = tk.Frame(self, bg=c['bg'], pady=18)
        hdr.pack(fill='x', padx=28)
        tk.Label(hdr, text="🎵  Duplicate Music Cleaner",
                 bg=c['bg'], fg=c['text'],
                 font=('Segoe UI', 20, 'bold')).pack(side='left')
        if not HAS_MUTAGEN:
            tk.Label(hdr, text="  mutagen yüklü değil – meta veri gösterilmeyecek",
                     bg=c['bg'], fg=c['warning'],
                     font=('Segoe UI', 8)).pack(side='left', padx=8)

        # ── Folder picker ──
        picker = tk.Frame(self, bg=c['surface'], pady=12, padx=16)
        picker.pack(fill='x', padx=28, pady=(0, 12))
        picker.columnconfigure(1, weight=1)

        tk.Label(picker, text="Klasör:", bg=c['surface'], fg=c['muted'],
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w', padx=(0, 8))
        self.folder_var = tk.StringVar(value=str(Path.home() / "Music"))
        tk.Entry(picker, textvariable=self.folder_var,
                 bg=c['bg'], fg=c['text'], insertbackground=c['text'],
                 relief='flat', font=('Segoe UI', 10),
                 highlightbackground=c['border'], highlightthickness=1
                 ).grid(row=0, column=1, sticky='ew', ipady=5)
        ttk.Button(picker, text="Gözat", style='Ghost.TButton',
                   command=self._browse).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(picker, text="▶  Tara", style='Accent.TButton',
                   command=self._start_scan).grid(row=0, column=3, padx=(8, 0))

        # ── Progress ──
        self.progress_frame = tk.Frame(self, bg=c['bg'])
        self.progress_frame.pack(fill='x', padx=28)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var,
                                            maximum=100, style='TProgressbar')
        self.progress_bar.pack(fill='x')
        self.status_var = tk.StringVar(value="Taramak için bir klasör seçin.")
        tk.Label(self.progress_frame, textvariable=self.status_var,
                 bg=c['bg'], fg=c['muted'], font=('Segoe UI', 8)
                 ).pack(anchor='w', pady=(2, 4))

        # ── Stats row ──
        self.stats_frame = tk.Frame(self, bg=c['bg'])
        self.stats_frame.pack(fill='x', padx=28, pady=(0, 10))
        self._stat_boxes = {}
        for key, label in [('groups', 'Grup'), ('files', 'Dosya'), ('waste', 'İsraf'), ('selected', 'Seçili')]:
            box = tk.Frame(self.stats_frame, bg=c['surface'], padx=20, pady=10)
            box.pack(side='left', padx=(0, 8))
            val_lbl = tk.Label(box, text="—", bg=c['surface'], fg=c['text'],
                               font=('Segoe UI', 18, 'bold'))
            val_lbl.pack()
            tk.Label(box, text=label, bg=c['surface'], fg=c['muted'],
                     font=('Segoe UI', 8)).pack()
            self._stat_boxes[key] = val_lbl

        # ── Main pane ──
        pane = tk.PanedWindow(self, orient='horizontal', bg=c['bg'],
                               sashwidth=6, sashpad=0, relief='flat')
        pane.pack(fill='both', expand=True, padx=28, pady=(0, 10))

        # Left: group list
        left = tk.Frame(pane, bg=c['surface'])
        pane.add(left, minsize=260)
        tk.Label(left, text="Kopya Grupları", bg=c['surface'], fg=c['muted'],
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=10, pady=(8, 4))
        self.group_list = tk.Listbox(left, bg=c['surface'], fg=c['text'],
                                     selectbackground=c['accent'], activestyle='none',
                                     relief='flat', borderwidth=0, font=('Segoe UI', 9),
                                     highlightthickness=0)
        self.group_list.pack(fill='both', expand=True, padx=6, pady=(0, 6))
        self.group_list.bind('<<ListboxSelect>>', self._on_group_select)

        # Right: file list
        right = tk.Frame(pane, bg=c['bg'])
        pane.add(right, minsize=400)

        top_right = tk.Frame(right, bg=c['bg'])
        top_right.pack(fill='x', pady=(0, 6))
        tk.Label(top_right, text="Grup İçindeki Dosyalar", bg=c['bg'], fg=c['muted'],
                 font=('Segoe UI', 9, 'bold')).pack(side='left')
        ttk.Button(top_right, text="Tümünü İşaretle", style='Ghost.TButton',
                   command=lambda: self._select_all_in_group(True)).pack(side='right', padx=(4, 0))
        ttk.Button(top_right, text="İşareti Kaldır", style='Ghost.TButton',
                   command=lambda: self._select_all_in_group(False)).pack(side='right')
        ttk.Button(top_right, text="En İyisini Tut", style='Ghost.TButton',
                   command=self._keep_best).pack(side='right', padx=(0, 4))

        cols = ('check', 'name', 'size', 'duration', 'bitrate', 'path')
        self.tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
        self.tree.heading('check',    text='✓',        anchor='center')
        self.tree.heading('name',     text='Dosya Adı')
        self.tree.heading('size',     text='Boyut',     anchor='center')
        self.tree.heading('duration', text='Süre',      anchor='center')
        self.tree.heading('bitrate',  text='Bitrate',   anchor='center')
        self.tree.heading('path',     text='Yol')
        self.tree.column('check',    width=32,  minwidth=32,  stretch=False, anchor='center')
        self.tree.column('name',     width=180, minwidth=100)
        self.tree.column('size',     width=72,  minwidth=60,  anchor='center')
        self.tree.column('duration', width=60,  minwidth=50,  anchor='center')
        self.tree.column('bitrate',  width=70,  minwidth=60,  anchor='center')
        self.tree.column('path',     width=300, minwidth=120)
        vsb = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<ButtonRelease-1>', self._on_tree_click)

        # ── Bottom bar ──
        bot = tk.Frame(self, bg=c['bg'], pady=10)
        bot.pack(fill='x', padx=28)
        ttk.Button(bot, text="Tümünü Seç (1 bırak)", style='Ghost.TButton',
                   command=self._auto_select_all).pack(side='left')
        ttk.Button(bot, text="Seçimi Temizle", style='Ghost.TButton',
                   command=self._clear_selection).pack(side='left', padx=8)
        ttk.Button(bot, text="Raporu Kaydet (JSON)", style='Ghost.TButton',
                   command=self._export_report).pack(side='left')
        ttk.Button(bot, text="🗑  Seçilileri Sil", style='Danger.TButton',
                   command=self._delete_selected).pack(side='right')

    # ── Helpers ──────────────────────────────
    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.folder_var.get())
        if d:
            self.folder_var.set(d)

    def _set_stat(self, key, val):
        self._stat_boxes[key].config(text=str(val))

    def _update_selected_stat(self):
        n = sum(1 for v in self.checked_vars.values() if v.get())
        self._set_stat('selected', n)

    # ── Scan ─────────────────────────────────
    def _start_scan(self):
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Hata", "Geçerli bir klasör seçin.")
            return
        self._clear_ui()
        self.status_var.set("Taranıyor…")
        self.progress_var.set(0)
        threading.Thread(target=self._scan_worker, args=(folder,), daemon=True).start()

    def _scan_worker(self, folder):
        def progress(i, total):
            pct = i / total * 100 if total else 0
            self.after(0, lambda: self.progress_var.set(pct))
            self.after(0, lambda: self.status_var.set(f"Taranan: {i}/{total}"))

        dupes = scan_folder(folder, progress_cb=progress)
        self.after(0, lambda: self._show_results(dupes))

    def _show_results(self, dupes):
        self.duplicates = dupes
        self.checked_vars = {}

        total_files = sum(len(v) for v in dupes.values())
        wasted = 0
        for paths in dupes.values():
            sizes = sorted(os.path.getsize(p) for p in paths)
            wasted += sum(sizes[1:])   # en büyüğü tut, kalanlar israf

        self._set_stat('groups', len(dupes))
        self._set_stat('files',  total_files)
        self._set_stat('waste',  human_size(wasted))
        self._set_stat('selected', 0)

        self.group_list.delete(0, 'end')
        for i, (h, paths) in enumerate(dupes.items(), 1):
            name = Path(paths[0]).stem[:30]
            self.group_list.insert('end', f"  {i}. {name}… ({len(paths)} kopya)")

        if dupes:
            self.group_list.selection_set(0)
            self._on_group_select(None)
            self.status_var.set(f"✅  {len(dupes)} grup bulundu — {total_files} dosya")
        else:
            self.status_var.set("✅  Kopya bulunamadı!")
        self.progress_var.set(100)

    # ── Group / Tree ─────────────────────────
    def _on_group_select(self, _event):
        sel = self.group_list.curselection()
        if not sel:
            return
        idx = sel[0]
        h, paths = list(self.duplicates.items())[idx]
        self._populate_tree(paths)

    def _populate_tree(self, paths):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for path in paths:
            info = get_audio_info(path)
            if path not in self.checked_vars:
                self.checked_vars[path] = tk.BooleanVar(value=False)
            var = self.checked_vars[path]
            check = '☑' if var.get() else '☐'
            dur = f"{int(info['duration']//60)}:{int(info['duration']%60):02d}" if info['duration'] else '—'
            br  = f"{info['bitrate']//1000}k" if info['bitrate'] else '—'
            self.tree.insert('', 'end', iid=path, values=(
                check,
                Path(path).name,
                human_size(info['size']),
                dur,
                br,
                path
            ))

    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        col    = self.tree.identify_column(event.x)
        iid    = self.tree.identify_row(event.y)
        if not iid:
            return
        if col == '#1' or region == 'cell':
            if iid in self.checked_vars:
                v = self.checked_vars[iid]
                v.set(not v.get())
                self.tree.set(iid, 'check', '☑' if v.get() else '☐')
                self._update_selected_stat()

    # ── Selection helpers ─────────────────────
    def _select_all_in_group(self, state: bool):
        for iid in self.tree.get_children():
            if iid in self.checked_vars:
                self.checked_vars[iid].set(state)
                self.tree.set(iid, 'check', '☑' if state else '☐')
        self._update_selected_stat()

    def _keep_best(self):
        """En yüksek bitrate'li / en büyük dosya dışındakileri işaretle."""
        children = self.tree.get_children()
        if not children:
            return
        best = max(children, key=lambda p: (
            get_audio_info(p)['bitrate'] or 0,
            get_audio_info(p)['size']
        ))
        for iid in children:
            state = iid != best
            if iid in self.checked_vars:
                self.checked_vars[iid].set(state)
                self.tree.set(iid, 'check', '☑' if state else '☐')
        self._update_selected_stat()

    def _auto_select_all(self):
        """Her grupta en iyisi dışındakileri işaretle."""
        for h, paths in self.duplicates.items():
            best = max(paths, key=lambda p: (
                get_audio_info(p)['bitrate'] or 0,
                get_audio_info(p)['size']
            ))
            for p in paths:
                if p not in self.checked_vars:
                    self.checked_vars[p] = tk.BooleanVar()
                self.checked_vars[p].set(p != best)
        # Mevcut grubu yenile
        self._on_group_select(None)
        self._update_selected_stat()

    def _clear_selection(self):
        for v in self.checked_vars.values():
            v.set(False)
        self._on_group_select(None)
        self._update_selected_stat()

    # ── Delete ───────────────────────────────
    def _delete_selected(self):
        to_del = [p for p, v in self.checked_vars.items() if v.get()]
        if not to_del:
            messagebox.showinfo("Bilgi", "Silinecek dosya seçilmedi.")
            return
        msg = f"{len(to_del)} dosya kalıcı olarak silinecek.\n\nDevam etmek istiyor musunuz?"
        if not messagebox.askyesno("Onay", msg, icon='warning'):
            return
        errors = []
        deleted = 0
        for path in to_del:
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                errors.append(f"{path}: {e}")
        # Remove deleted from duplicates
        for h in list(self.duplicates.keys()):
            self.duplicates[h] = [p for p in self.duplicates[h] if p not in to_del]
            if len(self.duplicates[h]) < 2:
                del self.duplicates[h]
        # Refresh
        self._show_results(self.duplicates)
        msg2 = f"✅ {deleted} dosya silindi."
        if errors:
            msg2 += f"\n\n⚠ {len(errors)} hata:\n" + "\n".join(errors[:5])
        messagebox.showinfo("Tamamlandı", msg2)

    # ── Export ───────────────────────────────
    def _export_report(self):
        if not self.duplicates:
            messagebox.showinfo("Bilgi", "Önce tarama yapın.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON', '*.json')],
            initialfile='duplicate_report.json'
        )
        if not path:
            return
        report = {h: paths for h, paths in self.duplicates.items()}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Kaydedildi", f"Rapor kaydedildi:\n{path}")

    # ── Clear UI ─────────────────────────────
    def _clear_ui(self):
        self.group_list.delete(0, 'end')
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.duplicates = {}
        self.checked_vars = {}
        for key in self._stat_boxes:
            self._set_stat(key, '—')


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == '__main__':
    app = App()
    app.mainloop()