import os
import json
import csv
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import ctypes

from extractor import collect_archive_info
from pdf_generator import make_pdf
from locales import TRANSLATIONS
from themes import get_theme

try:
    myappid = '3dmark.extractor.app.1.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

APP_TITLE = "3DMark Result → PDF"

class StatCard(tk.Frame):
    def __init__(self, parent, title, icon, value="—", accent="#38bdf8", theme=None):
        super().__init__(parent, bg=theme["panel"], highlightthickness=1, highlightbackground=theme["border"])
        self.theme = theme
        self.accent = accent
        self.configure(padx=14, pady=12)

        self.top = tk.Frame(self, bg=theme["panel"])
        self.top.pack(fill="x")

        self.icon_lbl = tk.Label(self.top, text=icon, font=("Segoe UI Emoji", 12), fg=accent, bg=theme["panel"])
        self.icon_lbl.pack(side="left")
        
        self.title_lbl = tk.Label(self.top, text=title, font=("Segoe UI", 9), fg=theme["muted"], bg=theme["panel"])
        self.title_lbl.pack(side="left", padx=(8, 0))

        self.value_label = tk.Label(self, text=value, font=("Segoe UI", 15, "bold"), fg=theme["text"], bg=theme["panel"], anchor="w", justify="left", wraplength=200)
        self.value_label.pack(anchor="w", pady=(10, 0))

    def set(self, value):
        self.value_label.config(text=value if value not in (None, "") else "—")
        
    def update_theme(self, theme):
        self.theme = theme
        self.configure(bg=theme["panel"], highlightbackground=theme["border"])
        self.top.configure(bg=theme["panel"])
        self.icon_lbl.configure(bg=theme["panel"])
        self.title_lbl.configure(bg=theme["panel"], fg=theme["muted"])
        self.value_label.configure(bg=theme["panel"], fg=theme["text"])

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, theme, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.theme = theme
        
        self.canvas = tk.Canvas(self, bg=theme["panel2"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=theme["panel2"])

        self.scrollable_frame.bind("<Configure>", self._configure_scrollregion)
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

    def _configure_scrollregion(self, event):
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)
            
    def update_theme(self, theme):
        self.theme = theme
        self.canvas.configure(bg=theme["panel2"])
        self.scrollable_frame.configure(bg=theme["panel2"])

class ModernApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        self.is_dark = True
        self.current_lang = tk.StringVar(value="fr")
        self.current_lang.trace_add("write", self.update_language)
        self.theme = get_theme(self.is_dark)
        
        self.title(APP_TITLE)
        self.geometry("1280x850")
        self.minsize(1080, 720)
        self.configure(bg=self.theme["bg"])
        
        try:
            if os.path.exists("icon.ico"):
                self.iconbitmap("icon.ico")
            elif os.path.exists("logo.png"):
                img = tk.PhotoImage(file="logo.png")
                self.iconphoto(True, img)
        except Exception:
            pass

        self.file_path = None
        self.current_data = None
        
        self.icons = {"import": "📁", "activity": "📜", "summary": "📊", "score": "🏆", "fps": "⚡", "stability": "🎯", "loops": "🔄", "gpu": "🎮", "cpu": "🧠", "ram": "💾"}
        self._build_ui()
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def tr(self, key):
        return TRANSLATIONS.get(self.current_lang.get(), TRANSLATIONS["en"]).get(key, key)

    def _on_mousewheel(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget and str(widget).startswith(str(self.summary_container)):
            self.scroll_wrapper.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme = get_theme(self.is_dark)
        self.configure(bg=self.theme["bg"])
        
        self.btn_theme.config(text="🌞" if self.is_dark else "🌙", bg=self.theme["bg"], fg=self.theme["text"], activebackground=self.theme["bg"])
        self.title_lbl.config(fg=self.theme["text"], bg=self.theme["bg"])
        self.desc_lbl.config(fg=self.theme["muted"], bg=self.theme["bg"])
        
        for w in [self.root_frame, self.header, self.left_head, self.title_frame, self.lang_frame, self.stats_row, self.content, self.left, self.right]:
            w.config(bg=self.theme["bg"])
            
        for w in [self.rb_fr, self.rb_en]:
            w.config(bg=self.theme["bg"], fg=self.theme["text"], activebackground=self.theme["bg"], selectcolor=self.theme["accent"])

        # Update cards
        self.top_score.update_theme(self.theme)
        self.top_fps.update_theme(self.theme)
        self.top_stability.update_theme(self.theme)
        self.top_loops.update_theme(self.theme)
        self.top_gpu.update_theme(self.theme)
        
        self.summary_card.config(bg=self.theme["panel2"], highlightbackground=self.theme["border2"])
        self.sum_header.config(bg=self.theme["panel2"])
        self.sum_icon.config(bg=self.theme["panel2"])
        self.sum_text_f.config(bg=self.theme["panel2"])
        self.summary_title_lbl.config(bg=self.theme["panel2"], fg=self.theme["text"])
        self.summary_desc_lbl.config(bg=self.theme["panel2"], fg=self.theme["muted"])
        
        self.import_card.config(bg=self.theme["panel2"], highlightbackground=self.theme["border2"])
        self.imp_header.config(bg=self.theme["panel2"])
        self.imp_icon.config(bg=self.theme["panel2"])
        self.imp_text_f.config(bg=self.theme["panel2"])
        self.import_title.config(bg=self.theme["panel2"], fg=self.theme["text"])
        self.import_desc.config(bg=self.theme["panel2"], fg=self.theme["muted"])
        
        self.drop.config(bg=self.theme["panel3"], highlightbackground=self.theme["border2"])
        self.lbl_drag.config(bg=self.theme["panel3"], fg=self.theme["text"])
        self.lbl_click.config(bg=self.theme["panel3"], fg=self.theme["muted"])
        self.lbl_drag_desc.config(bg=self.theme["panel3"], fg=self.theme["muted"])
        
        self.action_row.config(bg=self.theme["panel2"])
        self.export_row.config(bg=self.theme["panel2"])
        
        self.convert_btn.config(bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"])
        self.btn_json.config(bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"])
        self.btn_csv.config(bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"])
        self.btn_batch.config(bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"])
        
        self.path_lbl.config(bg=self.theme["panel2"], fg=self.theme["subtle"])
        
        self.activity_card.config(bg=self.theme["panel2"], highlightbackground=self.theme["border2"])
        self.act_header.config(bg=self.theme["panel2"])
        self.act_icon.config(bg=self.theme["panel2"])
        self.act_text_f.config(bg=self.theme["panel2"])
        self.activity_title.config(bg=self.theme["panel2"], fg=self.theme["text"])
        self.activity_desc.config(bg=self.theme["panel2"], fg=self.theme["muted"])
        
        self.log.config(bg=self.theme["log_bg"], fg=self.theme["log_fg"])
        
        self.scroll_wrapper.update_theme(self.theme)
        if hasattr(self, "current_data") and self.current_data:
            self.update_summary_panel(self.current_data)
        else:
            self.update_summary_panel({})

    def update_language(self, *args):
        self.title_lbl.config(text=self.tr("title_extractor"))
        self.desc_lbl.config(text=self.tr("desc_main"))
        self.choose_btn.config(text=self.tr("btn_load"))
        self.convert_btn.config(text=self.tr("btn_pdf"))
        self.btn_batch.config(text=self.tr("btn_batch"))
        self.btn_json.config(text=self.tr("btn_json"))
        self.btn_csv.config(text=self.tr("btn_csv"))
        self.lbl_drag.config(text=self.tr("drag_drop"))
        self.lbl_click.config(text=self.tr("or_click"))
        self.lbl_drag_desc.config(text=self.tr("drag_desc"))
        
        self.import_title.config(text=self.tr("import_title"))
        self.import_desc.config(text=self.tr("import_desc"))
        self.activity_title.config(text=self.tr("activity_title"))
        self.activity_desc.config(text=self.tr("activity_desc"))
        self.summary_title_lbl.config(text=self.tr("summary_title"))
        self.summary_desc_lbl.config(text=self.tr("summary_desc"))
        
        for sec_key, lbl in getattr(self, "sec_labels", {}).items():
            lbl.config(text=self.tr(sec_key).upper())
            
        for key_text, lbl in getattr(self, "item_labels", {}).items():
            lbl.config(text=self.tr("lbl_" + key_text.lower().replace(" ", "_").replace("%", "").strip()))
            
        self.top_score.title_lbl.config(text=self.tr("lbl_best_score"))
        self.top_fps.title_lbl.config(text=self.tr("lbl_average_fps"))
        self.top_stability.title_lbl.config(text=self.tr("lbl_stability"))
        self.top_loops.title_lbl.config(text=self.tr("lbl_loop_count"))
        self.top_gpu.title_lbl.config(text=self.tr("lbl_gpu"))
        
        if self.path_var.get() in ["Aucun fichier sélectionné", "No file selected"]:
            self.path_var.set(self.tr("no_file"))

    def _build_ui(self):
        self.root_frame = tk.Frame(self, bg=self.theme["bg"])
        self.root_frame.pack(fill="both", expand=True, padx=20, pady=18)

        self.header = tk.Frame(self.root_frame, bg=self.theme["bg"])
        self.header.pack(fill="x", pady=(0, 14))

        self.left_head = tk.Frame(self.header, bg=self.theme["bg"])
        self.left_head.pack(side="left", fill="x", expand=True)

        self.title_frame = tk.Frame(self.left_head, bg=self.theme["bg"])
        self.title_frame.pack(side="left", fill="y")
        self.title_lbl = tk.Label(self.title_frame, text=self.tr("title_extractor"), font=("Segoe UI", 28, "bold"), fg=self.theme["text"], bg=self.theme["bg"])
        self.title_lbl.pack(anchor="w")
        self.desc_lbl = tk.Label(self.title_frame, text=self.tr("desc_main"), font=("Segoe UI", 10), fg=self.theme["muted"], bg=self.theme["bg"])
        self.desc_lbl.pack(anchor="w", pady=(4, 0))

        self.lang_frame = tk.Frame(self.header, bg=self.theme["bg"])
        self.lang_frame.pack(side="right", padx=(16, 0))
        
        self.btn_theme = tk.Button(self.lang_frame, text="🌞", command=self.toggle_theme, bg=self.theme["bg"], fg=self.theme["text"], relief="flat", bd=0, font=("Segoe UI Emoji", 14), cursor="hand2")
        self.btn_theme.pack(side="left", padx=10)
        
        self.rb_fr = tk.Radiobutton(self.lang_frame, text="FR", variable=self.current_lang, value="fr", bg=self.theme["bg"], fg=self.theme["text"], selectcolor=self.theme["accent"], activebackground=self.theme["bg"], activeforeground=self.theme["accent"], indicatoron=False, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=10, pady=5)
        self.rb_fr.pack(side="left", padx=2)
        
        self.rb_en = tk.Radiobutton(self.lang_frame, text="EN", variable=self.current_lang, value="en", bg=self.theme["bg"], fg=self.theme["text"], selectcolor=self.theme["accent"], activebackground=self.theme["bg"], activeforeground=self.theme["accent"], indicatoron=False, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=10, pady=5)
        self.rb_en.pack(side="left", padx=2)

        self.status_badge = tk.Label(self.lang_frame, text="NO FILE", font=("Segoe UI", 10, "bold"), fg="#0b1220", bg="#64748b", padx=18, pady=10)
        self.status_badge.pack(side="left", padx=(16, 0))

        self.stats_row = tk.Frame(self.root_frame, bg=self.theme["bg"])
        self.stats_row.pack(fill="x", pady=(0, 14))

        self.top_score = StatCard(self.stats_row, self.tr("lbl_best_score"), self.icons["score"], "—", accent=self.theme["success"], theme=self.theme)
        self.top_score.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_fps = StatCard(self.stats_row, self.tr("lbl_average_fps"), self.icons["fps"], "—", accent=self.theme["info"], theme=self.theme)
        self.top_fps.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_stability = StatCard(self.stats_row, self.tr("lbl_stability"), self.icons["stability"], "—", accent=self.theme["accent"], theme=self.theme)
        self.top_stability.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_loops = StatCard(self.stats_row, self.tr("lbl_loop_count"), self.icons["loops"], "—", accent="#a78bfa", theme=self.theme)
        self.top_loops.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_gpu = StatCard(self.stats_row, self.tr("lbl_gpu"), self.icons["gpu"], "—", accent=self.theme["danger"], theme=self.theme)
        self.top_gpu.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.root_frame, bg=self.theme["bg"])
        self.content.pack(fill="both", expand=True)

        self.left = tk.Frame(self.content, bg=self.theme["bg"])
        self.left.pack(side="left", fill="both", expand=True)

        self.right = tk.Frame(self.content, bg=self.theme["bg"], width=350)
        self.right.pack(side="right", fill="y", padx=(16, 0))
        self.right.pack_propagate(False)

        # Summary
        self.summary_card = tk.Frame(self.left, bg=self.theme["panel2"], highlightthickness=1, highlightbackground=self.theme["border2"], bd=0)
        self.summary_card.pack(fill="both", expand=True)
        
        self.sum_header = tk.Frame(self.summary_card, bg=self.theme["panel2"])
        self.sum_header.pack(fill="x", padx=18, pady=(18, 10))
        self.sum_icon = tk.Label(self.sum_header, text=self.icons["summary"], font=("Segoe UI Emoji", 16), fg=self.theme["accent"], bg=self.theme["panel2"])
        self.sum_icon.pack(side="left", padx=(0, 10))
        self.sum_text_f = tk.Frame(self.sum_header, bg=self.theme["panel2"])
        self.sum_text_f.pack(side="left", fill="x", expand=True)
        self.summary_title_lbl = tk.Label(self.sum_text_f, text=self.tr("summary_title"), font=("Segoe UI", 12, "bold"), fg=self.theme["text"], bg=self.theme["panel2"])
        self.summary_title_lbl.pack(anchor="w")
        self.summary_desc_lbl = tk.Label(self.sum_text_f, text=self.tr("summary_desc"), font=("Segoe UI", 9), fg=self.theme["muted"], bg=self.theme["panel2"], justify="left")
        self.summary_desc_lbl.pack(anchor="w")

        self.scroll_wrapper = ScrollableFrame(self.summary_card, theme=self.theme)
        self.scroll_wrapper.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.summary_container = self.scroll_wrapper.scrollable_frame
        
        self.sec_labels = {}
        self.item_labels = {}
        
        self.sections_layout = {
            "sec_result": [("Status", "Passed"), ("Overall Score", "Average score"), ("Best score", "Best score"), ("Worst score", "Worst score"), ("Stability", "Stability %"), ("Average FPS", "Average FPS")],
            "sec_system": [("GPU", "GPU"), ("CPU", "CPU"), ("RAM", "RAM"), ("VRAM", "VRAM"), ("OS", "OS"), ("Driver", "Driver"), ("Computer", "Computer"), ("User", "User")],
            "sec_test": [("Benchmark", "Benchmark name"), ("API", "API"), ("Resolution", "Resolution"), ("Loop count", "Loop count"), ("Benchmark ID", "Benchmark ID")]
        }

        # Import Card
        self.import_card = tk.Frame(self.right, bg=self.theme["panel2"], highlightthickness=1, highlightbackground=self.theme["border2"], bd=0)
        self.import_card.pack(fill="x", pady=(0, 14))
        
        self.imp_header = tk.Frame(self.import_card, bg=self.theme["panel2"])
        self.imp_header.pack(fill="x", padx=18, pady=(18, 10))
        self.imp_icon = tk.Label(self.imp_header, text=self.icons["import"], font=("Segoe UI Emoji", 16), fg=self.theme["accent"], bg=self.theme["panel2"])
        self.imp_icon.pack(side="left", padx=(0, 10))
        self.imp_text_f = tk.Frame(self.imp_header, bg=self.theme["panel2"])
        self.imp_text_f.pack(side="left", fill="x", expand=True)
        self.import_title = tk.Label(self.imp_text_f, text=self.tr("import_title"), font=("Segoe UI", 12, "bold"), fg=self.theme["text"], bg=self.theme["panel2"])
        self.import_title.pack(anchor="w")
        self.import_desc = tk.Label(self.imp_text_f, text=self.tr("import_desc"), font=("Segoe UI", 9), fg=self.theme["muted"], bg=self.theme["panel2"], wraplength=280, justify="left")
        self.import_desc.pack(anchor="w")

        self.drop = tk.Frame(self.import_card, bg=self.theme["panel3"], highlightthickness=1, highlightbackground=self.theme["border2"], height=140)
        self.drop.pack(fill="x", padx=18, pady=(0, 16))
        self.drop.pack_propagate(False)
        
        # Configure DND
        self.drop.drop_target_register(DND_FILES)
        self.drop.dnd_bind('<<Drop>>', self.on_drop)

        self.lbl_drag = tk.Label(self.drop, text=self.tr("drag_drop"), font=("Segoe UI", 14, "bold"), fg=self.theme["text"], bg=self.theme["panel3"])
        self.lbl_drag.pack(pady=(25, 6))
        self.lbl_click = tk.Label(self.drop, text=self.tr("or_click"), font=("Segoe UI", 10), fg=self.theme["muted"], bg=self.theme["panel3"])
        self.lbl_click.pack()
        self.lbl_drag_desc = tk.Label(self.drop, text=self.tr("drag_desc"), font=("Segoe UI", 9), fg=self.theme["muted"], bg=self.theme["panel3"], wraplength=280, justify="center")
        self.lbl_drag_desc.pack(pady=(8, 0))

        self.action_row = tk.Frame(self.import_card, bg=self.theme["panel2"])
        self.action_row.pack(fill="x", padx=18, pady=(0, 5))

        self.choose_btn = tk.Button(self.action_row, text=self.tr("btn_load"), command=self.pick_file, font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="#111827", activebackground=self.theme["accent_hover"], activeforeground="#111827", relief="flat", bd=0, padx=8, pady=8, cursor="hand2")
        self.choose_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.convert_btn = tk.Button(self.action_row, text=self.tr("btn_pdf"), command=self.convert_file, font=("Segoe UI", 10, "bold"), bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"], relief="flat", bd=0, padx=8, pady=8, cursor="hand2")
        self.convert_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        self.export_row = tk.Frame(self.import_card, bg=self.theme["panel2"])
        self.export_row.pack(fill="x", padx=18, pady=(0, 10))
        
        self.btn_json = tk.Button(self.export_row, text="JSON", command=self.export_json, font=("Segoe UI", 9, "bold"), bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"], relief="flat", bd=0, padx=5, pady=5, cursor="hand2")
        self.btn_json.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        self.btn_csv = tk.Button(self.export_row, text="CSV", command=self.export_csv, font=("Segoe UI", 9, "bold"), bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"], relief="flat", bd=0, padx=5, pady=5, cursor="hand2")
        self.btn_csv.pack(side="left", fill="x", expand=True, padx=(2, 2))
        
        self.btn_batch = tk.Button(self.export_row, text=self.tr("btn_batch"), command=self.batch_export, font=("Segoe UI", 9, "bold"), bg=self.theme["button_dark"], fg=self.theme["text"], activebackground=self.theme["button_dark_hover"], activeforeground=self.theme["text"], relief="flat", bd=0, padx=5, pady=5, cursor="hand2")
        self.btn_batch.pack(side="left", fill="x", expand=True, padx=(2, 0))

        self.path_var = tk.StringVar(value=self.tr("no_file"))
        self.path_lbl = tk.Label(self.import_card, textvariable=self.path_var, font=("Segoe UI", 9), fg=self.theme["subtle"], bg=self.theme["panel2"], wraplength=300, justify="left")
        self.path_lbl.pack(anchor="w", padx=18, pady=(0, 16))

        # Activity Card
        self.activity_card = tk.Frame(self.right, bg=self.theme["panel2"], highlightthickness=1, highlightbackground=self.theme["border2"], bd=0)
        self.activity_card.pack(fill="both", expand=True)
        
        self.act_header = tk.Frame(self.activity_card, bg=self.theme["panel2"])
        self.act_header.pack(fill="x", padx=18, pady=(18, 10))
        self.act_icon = tk.Label(self.act_header, text=self.icons["activity"], font=("Segoe UI Emoji", 16), fg=self.theme["accent"], bg=self.theme["panel2"])
        self.act_icon.pack(side="left", padx=(0, 10))
        self.act_text_f = tk.Frame(self.act_header, bg=self.theme["panel2"])
        self.act_text_f.pack(side="left", fill="x", expand=True)
        self.activity_title = tk.Label(self.act_text_f, text=self.tr("activity_title"), font=("Segoe UI", 12, "bold"), fg=self.theme["text"], bg=self.theme["panel2"])
        self.activity_title.pack(anchor="w")
        self.activity_desc = tk.Label(self.act_text_f, text=self.tr("activity_desc"), font=("Segoe UI", 9), fg=self.theme["muted"], bg=self.theme["panel2"], justify="left")
        self.activity_desc.pack(anchor="w")

        self.log = tk.Text(self.activity_card, bg=self.theme["log_bg"], fg=self.theme["log_fg"], insertbackground="white", relief="flat", bd=0, wrap="word", font=("Consolas", 10), padx=14, pady=14)
        self.log.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.log.insert("end", self.tr("log_ready"))
        self.log.configure(state="disabled")
        
        self.update_summary_panel({})

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def update_badge(self, status):
        if status == "PASS": self.status_badge.config(text="PASS", bg=self.theme["success"], fg="#052e16" if self.is_dark else "#FFFFFF")
        elif status == "FAIL": self.status_badge.config(text="FAIL", bg=self.theme["danger"], fg="#220a0a" if self.is_dark else "#FFFFFF")
        elif status == "READY": self.status_badge.config(text="READY", bg=self.theme["accent"], fg="#111827" if self.is_dark else "#FFFFFF")
        else: self.status_badge.config(text=status, bg=self.theme["muted"], fg="#0b1220" if self.is_dark else "#FFFFFF")

    def update_summary_panel(self, data):
        summary = data.get("summary", {})
        for widget in self.summary_container.winfo_children(): widget.destroy()
        self.sec_labels = {}
        self.item_labels = {}

        for section, items in self.sections_layout.items():
            sec_frame = tk.Frame(self.summary_container, bg=self.theme["panel2"])
            sec_frame.pack(fill="x", pady=(0, 16))
            lbl_sec = tk.Label(sec_frame, text=self.tr(section).upper(), font=("Segoe UI", 10, "bold"), fg=self.theme["accent"], bg=self.theme["panel2"])
            lbl_sec.pack(anchor="w", pady=(0, 8))
            self.sec_labels[section] = lbl_sec
            
            grid_frame = tk.Frame(sec_frame, bg=self.theme["panel2"])
            grid_frame.pack(fill="x")
            grid_frame.columnconfigure(0, weight=1, uniform="col")
            grid_frame.columnconfigure(1, weight=1, uniform="col")
            grid_frame.columnconfigure(2, weight=1, uniform="col")
            
            row, col = 0, 0
            for label, key in items:
                val = summary.get(key)
                if val is None: val = "—"
                
                item_frame = tk.Frame(grid_frame, bg=self.theme["panel3"])
                item_frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
                
                lbl_title = tk.Label(item_frame, text=self.tr("lbl_" + label.lower().replace(" ", "_").replace("%", "").strip()), font=("Segoe UI", 9), fg=self.theme["muted"], bg=self.theme["panel3"])
                lbl_title.pack(anchor="w", padx=10, pady=(8, 0))
                self.item_labels[label] = lbl_title
                
                tk.Label(item_frame, text=str(val), font=("Segoe UI", 10, "bold"), fg=self.theme["text"], bg=self.theme["panel3"]).pack(anchor="w", padx=10, pady=(0, 8))
                
                col += 1
                if col > 2:
                    col = 0; row += 1

        self.top_score.set(str(summary.get("Best score") or "—"))
        self.top_fps.set(str(summary.get("Average FPS") or "—"))
        self.top_stability.set(f"{summary.get('Stability %')} %" if summary.get("Stability %") not in (None, "") else "—")
        self.top_loops.set(str(summary.get("Loop count") or "—"))
        self.top_gpu.set(summary.get("GPU") or "—")

        if summary.get("Passed"): self.update_badge(summary.get("Passed"))
        else: self.update_badge("READY")

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            self.load_file(files[0])

    def pick_file(self):
        path = filedialog.askopenfilename(title=self.tr("import_title"), filetypes=[("3DMark Result", "*.3dmark-result"), ("ZIP", "*.zip"), ("Tous les fichiers", "*.*")])
        if path:
            self.load_file(path)

    def load_file(self, path):
        self.file_path = path
        self.path_var.set(path)
        self.write_log(self.tr("log_success").format(path))
        try:
            data = collect_archive_info(path)
            self.current_data = data
            self.update_summary_panel(data)
        except Exception as e:
            self.write_log(self.tr("log_err_read").format(e))
            self.update_badge("ERROR")

    def convert_file(self):
        if not self.file_path or not self.current_data: return
        try:
            output = filedialog.asksaveasfilename(title=self.tr("btn_pdf"), defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=os.path.splitext(os.path.basename(self.file_path))[0] + "-clean.pdf")
            if not output: return
            make_pdf(self.current_data, output, self.tr)
            self.write_log(self.tr("log_pdf_ok").format(output))
            messagebox.showinfo(APP_TITLE, self.tr("log_pdf_ok").format(output))
        except Exception as e:
            self.write_log(self.tr("log_err_pdf").format(e))
            self.write_log(traceback.format_exc())
            messagebox.showerror(APP_TITLE, self.tr("log_err_pdf").format(e))
            self.update_badge("ERROR")
            
    def export_json(self):
        if not self.current_data: return
        output = filedialog.asksaveasfilename(title="Export JSON", defaultextension=".json", filetypes=[("JSON", "*.json")], initialfile=os.path.splitext(os.path.basename(self.file_path))[0] + ".json")
        if not output: return
        try:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(self.current_data["summary"], f, indent=4, ensure_ascii=False)
            self.write_log(f"Export JSON réussi : {output}")
        except Exception as e:
            self.write_log(f"Erreur export JSON : {e}")

    def export_csv(self):
        if not self.current_data: return
        output = filedialog.asksaveasfilename(title="Export CSV", defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile=os.path.splitext(os.path.basename(self.file_path))[0] + ".csv")
        if not output: return
        try:
            with open(output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Key", "Value"])
                for k, v in self.current_data["summary"].items():
                    writer.writerow([k, v])
            self.write_log(f"Export CSV réussi : {output}")
        except Exception as e:
            self.write_log(f"Erreur export CSV : {e}")

    def batch_export(self):
        folder = filedialog.askdirectory(title="Choisir le dossier contenant les fichiers .3dmark-result")
        if not folder: return
        
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".3dmark-result") or f.endswith(".zip")]
        if not files:
            messagebox.showinfo("Batch", "Aucun fichier trouvé dans ce dossier.")
            return
            
        success_count = 0
        for f in files:
            self.write_log(f"Batch processing: {f}")
            try:
                data = collect_archive_info(f)
                out_pdf = os.path.splitext(f)[0] + "-clean.pdf"
                make_pdf(data, out_pdf, self.tr)
                self.write_log(f" -> OK: {out_pdf}")
                success_count += 1
            except Exception as e:
                self.write_log(f" -> ERREUR: {e}")
                
        messagebox.showinfo("Batch Terminé", f"{success_count} fichiers traités sur {len(files)}.")

if __name__ == "__main__":
    ModernApp().mainloop()