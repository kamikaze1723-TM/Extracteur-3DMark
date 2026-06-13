import os
import zipfile
import tempfile
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
from statistics import mean
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk
import re
import ctypes

try:
    myappid = '3dmark.extractor.app.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
except Exception:
    raise SystemExit("ReportLab est requis : py -m pip install reportlab")

APP_TITLE = "3DMark Result → PDF"

COLORS = {
    "bg": "#0B0E14",
    "bg2": "#11151F",
    "panel": "#151A27",
    "panel2": "#1A2132",
    "panel3": "#1F283C",
    "border": "#2A3650",
    "border2": "#3B4764",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
    "subtle": "#CBD5E1",
    "accent": "#8B5CF6",
    "accent_hover": "#7C3AED",
    "button_dark": "#1E293B",
    "button_dark_hover": "#334155",
    "success": "#10B981",
    "danger": "#F43F5E",
    "info": "#3B82F6",
}

PDF_COLORS = {
    "bg_dark": colors.HexColor("#151A27"),
    "bg_light": colors.HexColor("#F8FAFC"),
    "border": colors.HexColor("#CBD5E1"),
    "text_dark": colors.HexColor("#0F172A"),
    "text_light": colors.white,
    "accent": colors.HexColor("#8B5CF6"),
    "success": colors.HexColor("#10B981"),
    "danger": colors.HexColor("#F43F5E"),
    "muted": colors.HexColor("#64748B"),
    "alt_row": colors.HexColor("#F1F5F9")
}

TRANSLATIONS = {
    "fr": {
        "title_extractor": "Extracteur 3DMark",
        "desc_main": "Transforme un fichier .3dmark-result en rapport PDF propre, lisible et partageable.",
        "btn_load": "Choisir un fichier",
        "btn_pdf": "Convertir en PDF",
        "drag_drop": "Dépose ton fichier ici",
        "or_click": ".3dmark-result • .zip",
        "drag_desc": "L’application extrait les XML, détecte les scores et prépare un rapport PDF propre.",
        "import_title": "Importer un résultat",
        "import_desc": "Charge ton fichier benchmark, prévisualise les données détectées puis exporte le PDF.",
        "summary_title": "Résumé détecté",
        "summary_desc": "Aperçu des données extraites.",
        "activity_title": "Activité",
        "activity_desc": "Journal d’analyse et de génération du PDF.",
        "sec_result": "Résultat",
        "sec_system": "Système",
        "sec_test": "Test",
        "log_ready": "Prêt. Utilisez le bouton ou Ctrl+O pour ouvrir.\n",
        "log_reading": "Lecture de {}...",
        "log_success": "Fichier détecté : {}",
        "log_err_read": "Erreur lors de la lecture: {}",
        "log_err_pdf": "Erreur de conversion PDF: {}",
        "log_pdf_ok": "Conversion PDF réussie ! {}",
        "pdf_title": "Rapport 3DMark",
        "pdf_sys_info": "Informations Système",
        "pdf_bench_info": "Informations Benchmark",
        "pdf_raw_data": "Données Brutes (XML)",
        "pdf_desc_raw": "Toutes les paires clé-valeur trouvées dans les fichiers XML de l'archive.",
        "pdf_perf_loops": "Performances par Boucle (Stress Test)",
        "pdf_desc_loops": "Résultats détaillés extraits du fichier Monitoring.csv (FPS moyen et Scores).",
        "pdf_loop": "Boucle",
        "pdf_score": "Score",
        "pdf_fps": "FPS Moyen",
        "lbl_status": "Status",
        "lbl_overall_score": "Score Global",
        "lbl_best_score": "Meilleur Score",
        "lbl_worst_score": "Pire Score",
        "lbl_stability": "Stabilité %",
        "lbl_average_fps": "FPS Moyen",
        "lbl_gpu": "GPU",
        "lbl_cpu": "CPU",
        "lbl_ram": "RAM",
        "lbl_vram": "VRAM",
        "lbl_os": "OS",
        "lbl_driver": "Pilote",
        "lbl_benchmark": "Benchmark",
        "lbl_api": "API",
        "lbl_resolution": "Résolution",
        "lbl_loop_count": "Boucles",
        "lbl_computer": "Nom de l'ordinateur",
        "lbl_user": "Utilisateur",
        "lbl_benchmark_id": "ID du Test",
        "no_file": "Aucun fichier sélectionné"
    },
    "en": {
        "title_extractor": "3DMark Extractor",
        "desc_main": "Transforms a .3dmark-result file into a clean, readable, and shareable PDF report.",
        "btn_load": "Choose a file",
        "btn_pdf": "Convert to PDF",
        "drag_drop": "Drop your file here",
        "or_click": ".3dmark-result • .zip",
        "drag_desc": "The app extracts XMLs, detects scores, and prepares a clean PDF report.",
        "import_title": "Import a result",
        "import_desc": "Load your benchmark file, preview the extracted data, then export to PDF.",
        "summary_title": "Detected Summary",
        "summary_desc": "Overview of extracted data.",
        "activity_title": "Activity",
        "activity_desc": "Analysis and PDF generation log.",
        "sec_result": "Result",
        "sec_system": "System",
        "sec_test": "Test",
        "log_ready": "Ready. Use the button or Ctrl+O to open.\n",
        "log_reading": "Reading {}...",
        "log_success": "File detected: {}",
        "log_err_read": "Error reading file: {}",
        "log_err_pdf": "PDF conversion error: {}",
        "log_pdf_ok": "PDF conversion successful! {}",
        "pdf_title": "3DMark Report",
        "pdf_sys_info": "System Information",
        "pdf_bench_info": "Benchmark Information",
        "pdf_raw_data": "Raw Data (XML)",
        "pdf_desc_raw": "All key-value pairs found in the archive's XML files.",
        "pdf_perf_loops": "Performance per Loop (Stress Test)",
        "pdf_desc_loops": "Detailed results extracted from Monitoring.csv (Average FPS and Scores).",
        "pdf_loop": "Loop",
        "pdf_score": "Score",
        "pdf_fps": "Average FPS",
        "lbl_status": "Status",
        "lbl_overall_score": "Overall Score",
        "lbl_best_score": "Best score",
        "lbl_worst_score": "Worst score",
        "lbl_stability": "Stability %",
        "lbl_average_fps": "Average FPS",
        "lbl_gpu": "GPU",
        "lbl_cpu": "CPU",
        "lbl_ram": "RAM",
        "lbl_vram": "VRAM",
        "lbl_os": "OS",
        "lbl_driver": "Driver",
        "lbl_benchmark": "Benchmark",
        "lbl_api": "API",
        "lbl_resolution": "Resolution",
        "lbl_loop_count": "Loop count",
        "lbl_computer": "Computer Name",
        "lbl_user": "User",
        "lbl_benchmark_id": "Run ID",
        "no_file": "No file selected"
    }
}

def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag

def parse_xml_file(path):
    root = ET.parse(path).getroot()
    data = []
    for elem in root.iter():
        tag = strip_ns(elem.tag)
        text = (elem.text or "").strip()
        if text:
            data.append((tag, text))
        for k, v in elem.attrib.items():
            val = str(v).strip()
            if val:
                data.append((f"{tag}_{strip_ns(k)}", val))
                data.append((strip_ns(k), val))
    return data

def safe_float(v):
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return None

def safe_int(v):
    try:
        return int(float(v))
    except Exception:
        return None

def find_first(pairs, patterns, exclude=None):
    exclude = exclude or []
    for p in patterns:
        p = p.lower()
        for k, v in pairs:
            if k.lower() == p:
                return v
    for p in patterns:
        p = p.lower()
        for k, v in pairs:
            lk = k.lower()
            if lk.startswith(f"{p}_") or lk.endswith(f"_{p}") or f"_{p}_" in lk:
                if not any(x in lk or x in str(v).lower() for x in exclude): return v
    for p in patterns:
        p = p.lower()
        if len(p) >= 4:
            for k, v in pairs:
                lk = k.lower()
                if p in lk:
                    if not any(x in lk or x in str(v).lower() for x in exclude): return v
    return None

def collect_archive_info(archive_path):
    result = {"archive": archive_path, "files": [], "pairs": [], "summary": {}, "scores": [], "fps_values": []}

    with zipfile.ZipFile(archive_path, "r") as zf:
        names = zf.namelist()
        result["files"] = names
        with tempfile.TemporaryDirectory() as td:
            zf.extractall(td)
            for name in names:
                full = os.path.join(td, name)
                if os.path.isfile(full) and name.lower().endswith(".xml"):
                    try: result["pairs"].extend(parse_xml_file(full))
                    except Exception: pass

    pairs = result["pairs"]
    benchmark_id = find_first(pairs, ["benchmark_run_id", "benchmarkrunid", "run_id"])
    benchmark_name = find_first(pairs, ["workload_name", "benchmarkname", "testname", "resultname"]) or "3DMark Benchmark"
    
    api = find_first(pairs, ["graphics_api", "graphicsapi", "api", "backend", "directx", "vulkan", "opengl"])
    start_time = find_first(pairs, ["benchmark_start_time", "starttime"])
    finish_time = find_first(pairs, ["benchmark_finish_time", "endtime"])
    loops = find_first(pairs, ["loop_count", "loopsdone", "testloopsdone", "loopcount"])
    
    resolution = None
    pw = find_first(pairs, ["physicalwidth", "physical_width"])
    ph = find_first(pairs, ["physicalheight", "physical_height"])
    if pw and ph:
        resolution = f"{pw}x{ph}"
    else:
        resolution = find_first(pairs, ["display_resolution", "screenresolution", "displayresolution", "render_resolution", "resolution"])
        if not resolution:
            for k, v in pairs:
                if k.lower() in ["commandline", "command_line"]:
                    m1 = re.search(r'--screenWidth=(\d+)', str(v))
                    m2 = re.search(r'--screenHeight=(\d+)', str(v))
                    if m1 and m2:
                        resolution = f"{m1.group(1)}x{m2.group(1)}"
                        break

    gpu = find_first(pairs, ["adapter_name", "graphicscard", "graphicsadapter", "videocard", "gpu_name", "gpu"]) or "Unknown GPU"
    cpu = find_first(pairs, ["cpu", "processor", "cpu_name", "processor_name"]) or "Unknown CPU"
    os_name = find_first(pairs, ["os", "operatingsystem", "os_name", "os_version", "osversion", "platform"], exclude=["bios"])
    ram = find_first(pairs, ["memory", "ram", "systemmemory", "memorytotal", "physical_memory"], exclude=["dedicated", "shared", "minimum", "maximum", "current", "clock"])
    vram = find_first(pairs, ["mem_size", "dedicatedvideomemory", "dedicatedmemory", "video_memory", "videomemory", "vram", "adapter_memory"])
    driver = find_first(pairs, ["driverversion", "driver_version", "graphicsdriver", "driver"])

    if ram and str(ram).isdigit(): ram = f"{int(ram) // 1048576} MB" if int(ram) > 1000000 else f"{ram} MB"
    if vram and str(vram).isdigit(): vram = f"{int(vram) // 1048576} MB" if int(vram) > 1000000 else f"{vram} MB"

    stability = find_first(pairs, ["stabilitydx", "dx12stability", "stability"])
    best_score = find_first(pairs, ["bestscoredx", "dx12bestscore"])
    worst_score = find_first(pairs, ["worstscoredx", "dx12worstscore"])
    passed = find_first(pairs, ["passdx", "dx12passed"])

    if not best_score: best_score = find_first(pairs, ["overallscoredxforpass"])

    primary_results = []
    for k, v in pairs:
        if k.lower() == "primary_result":
            fv = safe_float(v)
            if fv is not None: primary_results.append(fv)

    pass_scores = []
    for k, v in pairs:
        lk = k.lower()
        if "overallscoredxforpass" in lk or "graphicsscoredxforpass" in lk or "3dmarkscoreforpass" in lk:
            iv = safe_int(v)
            if iv is not None: pass_scores.append(iv)

    dedup_scores = []
    seen = set()
    for s in pass_scores:
        if s not in seen:
            dedup_scores.append(s)
            seen.add(s)

    avg_fps = round(mean(primary_results), 3) if primary_results else None
    avg_score = round(mean(dedup_scores), 1) if dedup_scores else None

    stability_num = safe_float(stability)
    if stability_num is not None: stability = round(stability_num, 2)

    passed_text = None
    if str(passed) in ("1", "1.0", "true", "True"): passed_text = "PASS"
    elif passed is not None: passed_text = "FAIL"

    result["summary"] = {
        "Benchmark name": benchmark_name,
        "Benchmark ID": benchmark_id,
        "GPU": gpu,
        "CPU": cpu,
        "RAM": ram,
        "VRAM": vram,
        "OS": os_name,
        "Driver": driver,
        "API": api,
        "Resolution": resolution,
        "Start time": start_time,
        "Finish time": finish_time,
        "Loop count": safe_int(loops) if loops is not None else loops,
        "Best score": safe_int(best_score) if best_score is not None else best_score,
        "Worst score": safe_int(worst_score) if worst_score is not None else worst_score,
        "Average score": avg_score,
        "Stability %": stability,
        "Average FPS": avg_fps,
        "Passed": passed_text,
        "Computer": find_first(pairs, ["computer_name", "computername"]),
        "User": find_first(pairs, ["username", "user_name"]),
    }
    result["scores"] = dedup_scores[:]
    result["fps_values"] = primary_results[:]
    return result

def nice_rows(summary):
    order = ["Benchmark name", "Benchmark ID", "GPU", "CPU", "RAM", "VRAM", "OS", "Driver", "API", "Resolution", "Computer", "User", "Loop count", "Best score", "Worst score", "Average score", "Stability %", "Average FPS", "Passed"]
    rows = []
    for key in order:
        value = summary.get(key)
        if value not in (None, "", []): rows.append([key, str(value)])
    return rows

def make_pdf(data, output_pdf, tr):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallMuted", parent=styles["BodyText"], fontSize=9, textColor=colors.HexColor("#667085")))
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading2"], fontSize=14, textColor=PDF_COLORS["accent"], spaceAfter=6))

    doc = SimpleDocTemplate(output_pdf, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=14*mm)
    story = []
    
    if os.path.exists("logo.png"):
        story.append(Image("logo.png", width=40*mm, height=40*mm, kind='proportional'))
        story.append(Spacer(1, 10))

    title = data["summary"].get("Benchmark name") or tr("pdf_title")
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Source file: {data['archive']}", styles["SmallMuted"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["SmallMuted"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(tr("pdf_sys_info"), styles["SectionTitle"]))
    summary_rows = [["Field", "Value"]] + nice_rows(data["summary"])
    summary_table = Table(summary_rows, colWidths=[48 * mm, 125 * mm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PDF_COLORS["bg_dark"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), PDF_COLORS["text_light"]),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, PDF_COLORS["border"]),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PDF_COLORS["alt_row"]]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    if data["scores"]:
        story.append(Paragraph(f"{tr('pdf_score')} ({tr('pdf_loop')})", styles["SectionTitle"]))
        score_rows = [[tr("pdf_loop"), tr("pdf_score")]]
        for i, score in enumerate(data["scores"], start=1): score_rows.append([str(i), str(score)])
        t = Table(score_rows, colWidths=[25 * mm, 35 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PDF_COLORS["bg_dark"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), PDF_COLORS["text_light"]),
            ("GRID", (0, 0), (-1, -1), 0.4, PDF_COLORS["border"]),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PDF_COLORS["alt_row"]]),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    if data["fps_values"]:
        story.append(Paragraph(tr("pdf_fps"), styles["SectionTitle"]))
        fps_rows = [[tr("pdf_loop"), tr("pdf_fps")]]
        for i, fps in enumerate(data["fps_values"], start=1): fps_rows.append([str(i), f"{fps:.3f}"])
        t = Table(fps_rows, colWidths=[25 * mm, 35 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PDF_COLORS["bg_dark"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), PDF_COLORS["text_light"]),
            ("GRID", (0, 0), (-1, -1), 0.4, PDF_COLORS["border"]),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PDF_COLORS["alt_row"]]),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    if os.path.exists("logo.png"):
        story.append(Spacer(1, 20))
        story.append(Image("logo.png", width=30*mm, height=30*mm, kind='proportional'))

    doc.build(story)

class StatCard(tk.Frame):
    def __init__(self, parent, title, icon, value="—", accent="#38bdf8"):
        super().__init__(parent, bg=COLORS["panel"], highlightthickness=1, highlightbackground=COLORS["border"])
        self.configure(padx=14, pady=12)

        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill="x")

        tk.Label(top, text=icon, font=("Segoe UI Emoji", 12), fg=accent, bg=COLORS["panel"]).pack(side="left")
        self.title_lbl = tk.Label(top, text=title, font=("Segoe UI", 9), fg=COLORS["muted"], bg=COLORS["panel"])
        self.title_lbl.pack(side="left", padx=(8, 0))

        self.value_label = tk.Label(self, text=value, font=("Segoe UI", 15, "bold"), fg=COLORS["text"], bg=COLORS["panel"], anchor="w", justify="left", wraplength=200)
        self.value_label.pack(anchor="w", pady=(10, 0))

    def set(self, value):
        self.value_label.config(text=value if value not in (None, "") else "—")

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        bg_color = kwargs.pop('bg', COLORS["bg"])
        super().__init__(container, *args, **kwargs)
        
        style = ttk.Style()
        style.configure("TFrame", background=bg_color)
        
        canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=bg_color)

        self.scrollable_frame.bind("<Configure>", self._configure_scrollregion)
        self.window_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(self.window_id, width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        # Scrollbar is created but intentionally NOT packed to keep it invisible
        self.canvas = canvas

    def _configure_scrollregion(self, event):
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

    def _on_mousewheel(self, event):
        # Only scroll if content is taller than canvas to prevent gap creation
        if self.scrollable_frame.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class ModernApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_lang = tk.StringVar(value="fr")
        self.current_lang.trace_add("write", self.update_language)
        self.tr = lambda key: TRANSLATIONS.get(self.current_lang.get(), TRANSLATIONS["en"]).get(key, key)
        
        self.title(APP_TITLE)
        self.geometry("1280x820")
        self.minsize(1080, 720)
        self.configure(bg=COLORS["bg"])
        
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

    def _on_mousewheel(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget and str(widget).startswith(str(self.summary_container)):
            self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_language(self, *args):
        self.title_lbl.config(text=self.tr("title_extractor"))
        self.desc_lbl.config(text=self.tr("desc_main"))
        self.choose_btn.config(text=self.tr("btn_load"))
        self.convert_btn.config(text=self.tr("btn_pdf"))
        self.lbl_drag.config(text=self.tr("drag_drop"))
        self.lbl_click.config(text=self.tr("or_click"))
        self.lbl_drag_desc.config(text=self.tr("drag_desc"))
        
        self.import_title.config(text=self.tr("import_title"))
        self.import_desc.config(text=self.tr("import_desc"))
        self.activity_title.config(text=self.tr("activity_title"))
        self.activity_desc.config(text=self.tr("activity_desc"))
        self.summary_title.config(text=self.tr("summary_title"))
        self.summary_desc.config(text=self.tr("summary_desc"))
        
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

    def section_card(self, parent):
        return tk.Frame(parent, bg=COLORS["panel2"], highlightthickness=1, highlightbackground=COLORS["border2"], bd=0)

    def add_title(self, parent, title, subtitle=None, icon_key=None, wrap=320):
        header = tk.Frame(parent, bg=COLORS["panel2"])
        header.pack(fill="x", padx=18, pady=(18, 10))
        if icon_key:
            tk.Label(header, text=self.icons.get(icon_key, ""), font=("Segoe UI Emoji", 16), fg=COLORS["accent"], bg=COLORS["panel2"]).pack(side="left", padx=(0, 10))
        text_frame = tk.Frame(header, bg=COLORS["panel2"])
        text_frame.pack(side="left", fill="x", expand=True)
        t_lbl = tk.Label(text_frame, text=title, font=("Segoe UI", 12, "bold"), fg=COLORS["text"], bg=COLORS["panel2"])
        t_lbl.pack(anchor="w")
        d_lbl = tk.Label(text_frame, text=subtitle, font=("Segoe UI", 9), fg=COLORS["muted"], bg=COLORS["panel2"], wraplength=wrap, justify="left")
        d_lbl.pack(anchor="w")
        return t_lbl, d_lbl

    def _build_ui(self):
        root = tk.Frame(self, bg=COLORS["bg"])
        root.pack(fill="both", expand=True, padx=20, pady=18)

        header = tk.Frame(root, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 14))

        left_head = tk.Frame(header, bg=COLORS["bg"])
        left_head.pack(side="left", fill="x", expand=True)

        title_frame = tk.Frame(left_head, bg=COLORS["bg"])
        title_frame.pack(side="left", fill="y")
        self.title_lbl = tk.Label(title_frame, text=self.tr("title_extractor"), font=("Segoe UI", 28, "bold"), fg=COLORS["text"], bg=COLORS["bg"])
        self.title_lbl.pack(anchor="w")
        self.desc_lbl = tk.Label(title_frame, text=self.tr("desc_main"), font=("Segoe UI", 10), fg=COLORS["muted"], bg=COLORS["bg"])
        self.desc_lbl.pack(anchor="w", pady=(4, 0))

        lang_frame = tk.Frame(header, bg=COLORS["bg"])
        lang_frame.pack(side="right", padx=(16, 0))
        tk.Radiobutton(lang_frame, text="FR", variable=self.current_lang, value="fr", bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["accent"], activebackground=COLORS["bg"], activeforeground=COLORS["accent"], indicatoron=False, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=10, pady=5).pack(side="left", padx=2)
        tk.Radiobutton(lang_frame, text="EN", variable=self.current_lang, value="en", bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["accent"], activebackground=COLORS["bg"], activeforeground=COLORS["accent"], indicatoron=False, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=10, pady=5).pack(side="left", padx=2)

        self.status_badge = tk.Label(lang_frame, text="NO FILE", font=("Segoe UI", 10, "bold"), fg="#0b1220", bg="#64748b", padx=18, pady=10)
        self.status_badge.pack(side="left", padx=(16, 0))

        stats_row = tk.Frame(root, bg=COLORS["bg"])
        stats_row.pack(fill="x", pady=(0, 14))

        self.top_score = StatCard(stats_row, self.tr("lbl_best_score"), self.icons["score"], "—", accent=COLORS["success"])
        self.top_score.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_fps = StatCard(stats_row, self.tr("lbl_average_fps"), self.icons["fps"], "—", accent=COLORS["info"])
        self.top_fps.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_stability = StatCard(stats_row, self.tr("lbl_stability"), self.icons["stability"], "—", accent=COLORS["accent"])
        self.top_stability.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_loops = StatCard(stats_row, self.tr("lbl_loop_count"), self.icons["loops"], "—", accent="#a78bfa")
        self.top_loops.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.top_gpu = StatCard(stats_row, self.tr("lbl_gpu"), self.icons["gpu"], "—", accent=COLORS["danger"])
        self.top_gpu.pack(side="left", fill="both", expand=True)

        content = tk.Frame(root, bg=COLORS["bg"])
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(content, bg=COLORS["bg"], width=350)
        right.pack(side="right", fill="y", padx=(16, 0))
        right.pack_propagate(False)

        summary_card = self.section_card(left)
        summary_card.pack(fill="both", expand=True)
        self.summary_title, self.summary_desc = self.add_title(summary_card, self.tr("summary_title"), self.tr("summary_desc"), icon_key="summary")

        scroll_wrapper = ScrollableFrame(summary_card, bg=COLORS["panel2"])
        scroll_wrapper.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.summary_container = scroll_wrapper.scrollable_frame
        self.scroll_canvas = scroll_wrapper.canvas
        
        self.sec_labels = {}
        self.item_labels = {}
        
        self.sections_layout = {
            "sec_result": [("Status", "Passed"), ("Overall Score", "Average score"), ("Best score", "Best score"), ("Worst score", "Worst score"), ("Stability", "Stability %"), ("Average FPS", "Average FPS")],
            "sec_system": [("GPU", "GPU"), ("CPU", "CPU"), ("RAM", "RAM"), ("VRAM", "VRAM"), ("OS", "OS"), ("Driver", "Driver"), ("Computer", "Computer"), ("User", "User")],
            "sec_test": [("Benchmark", "Benchmark name"), ("API", "API"), ("Resolution", "Resolution"), ("Loop count", "Loop count"), ("Benchmark ID", "Benchmark ID")]
        }

        import_card = self.section_card(right)
        import_card.pack(fill="x", pady=(0, 14))
        self.import_title, self.import_desc = self.add_title(import_card, self.tr("import_title"), self.tr("import_desc"), icon_key="import", wrap=280)

        drop = tk.Frame(import_card, bg=COLORS["panel3"], highlightthickness=1, highlightbackground=COLORS["border2"], height=165)
        drop.pack(fill="x", padx=18, pady=(0, 16))
        drop.pack_propagate(False)

        self.lbl_drag = tk.Label(drop, text=self.tr("drag_drop"), font=("Segoe UI", 14, "bold"), fg=COLORS["text"], bg=COLORS["panel3"])
        self.lbl_drag.pack(pady=(34, 6))
        self.lbl_click = tk.Label(drop, text=self.tr("or_click"), font=("Segoe UI", 10), fg=COLORS["muted"], bg=COLORS["panel3"])
        self.lbl_click.pack()
        self.lbl_drag_desc = tk.Label(drop, text=self.tr("drag_desc"), font=("Segoe UI", 9), fg=COLORS["muted"], bg=COLORS["panel3"], wraplength=280, justify="center")
        self.lbl_drag_desc.pack(pady=(8, 0))

        action_row = tk.Frame(import_card, bg=COLORS["panel2"])
        action_row.pack(fill="x", padx=18, pady=(0, 10))

        self.choose_btn = tk.Button(action_row, text=self.tr("btn_load"), command=self.pick_file, font=("Segoe UI", 10, "bold"), bg=COLORS["accent"], fg="#111827", activebackground=COLORS["accent_hover"], activeforeground="#111827", relief="flat", bd=0, padx=18, pady=12, cursor="hand2")
        self.choose_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.convert_btn = tk.Button(action_row, text=self.tr("btn_pdf"), command=self.convert_file, font=("Segoe UI", 10, "bold"), bg=COLORS["button_dark"], fg=COLORS["text"], activebackground=COLORS["button_dark_hover"], activeforeground=COLORS["text"], relief="flat", bd=0, padx=18, pady=12, cursor="hand2")
        self.convert_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.path_var = tk.StringVar(value=self.tr("no_file"))
        tk.Label(import_card, textvariable=self.path_var, font=("Segoe UI", 9), fg=COLORS["subtle"], bg=COLORS["panel2"], wraplength=300, justify="left").pack(anchor="w", padx=18, pady=(0, 16))

        activity_card = self.section_card(right)
        activity_card.pack(fill="both", expand=True)
        self.activity_title, self.activity_desc = self.add_title(activity_card, self.tr("activity_title"), self.tr("activity_desc"), icon_key="activity")

        self.log = tk.Text(activity_card, bg="#08101d", fg="#dbeafe", insertbackground="white", relief="flat", bd=0, wrap="word", font=("Consolas", 10), padx=14, pady=14)
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
        if status == "PASS": self.status_badge.config(text="PASS", bg=COLORS["success"], fg="#052e16")
        elif status == "FAIL": self.status_badge.config(text="FAIL", bg=COLORS["danger"], fg="#220a0a")
        elif status == "READY": self.status_badge.config(text="READY", bg=COLORS["accent"], fg="#111827")
        else: self.status_badge.config(text=status, bg="#64748b", fg="#0b1220")

    def update_summary_panel(self, data):
        summary = data.get("summary", {})
        for widget in self.summary_container.winfo_children(): widget.destroy()
        self.sec_labels = {}
        self.item_labels = {}

        for section, items in self.sections_layout.items():
            sec_frame = tk.Frame(self.summary_container, bg=COLORS["panel2"])
            sec_frame.pack(fill="x", pady=(0, 16))
            lbl_sec = tk.Label(sec_frame, text=self.tr(section).upper(), font=("Segoe UI", 10, "bold"), fg=COLORS["accent"], bg=COLORS["panel2"])
            lbl_sec.pack(anchor="w", pady=(0, 8))
            self.sec_labels[section] = lbl_sec
            
            grid_frame = tk.Frame(sec_frame, bg=COLORS["panel2"])
            grid_frame.pack(fill="x")
            grid_frame.columnconfigure(0, weight=1, uniform="col")
            grid_frame.columnconfigure(1, weight=1, uniform="col")
            grid_frame.columnconfigure(2, weight=1, uniform="col")
            
            row, col = 0, 0
            for label, key in items:
                val = summary.get(key)
                if val is None: val = "—"
                
                item_frame = tk.Frame(grid_frame, bg=COLORS["panel3"])
                item_frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
                
                lbl_title = tk.Label(item_frame, text=self.tr("lbl_" + label.lower().replace(" ", "_").replace("%", "").strip()), font=("Segoe UI", 9), fg=COLORS["muted"], bg=COLORS["panel3"])
                lbl_title.pack(anchor="w", padx=10, pady=(8, 0))
                self.item_labels[label] = lbl_title
                
                tk.Label(item_frame, text=str(val), font=("Segoe UI", 10, "bold"), fg=COLORS["text"], bg=COLORS["panel3"]).pack(anchor="w", padx=10, pady=(0, 8))
                
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

    def pick_file(self):
        path = filedialog.askopenfilename(title=self.tr("import_title"), filetypes=[("3DMark Result", "*.3dmark-result"), ("ZIP", "*.zip"), ("Tous les fichiers", "*.*")])
        if path:
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
        if not self.file_path: return
        try:
            data = collect_archive_info(self.file_path)
            self.current_data = data
            self.update_summary_panel(data)
            output = filedialog.asksaveasfilename(title=self.tr("btn_pdf"), defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=os.path.splitext(os.path.basename(self.file_path))[0] + "-clean.pdf")
            if not output: return
            make_pdf(data, output, self.tr)
            self.write_log(self.tr("log_pdf_ok").format(output))
            messagebox.showinfo(APP_TITLE, self.tr("log_pdf_ok").format(output))
        except Exception as e:
            self.write_log(self.tr("log_err_pdf").format(e))
            self.write_log(traceback.format_exc())
            messagebox.showerror(APP_TITLE, self.tr("log_err_pdf").format(e))
            self.update_badge("ERROR")

if __name__ == "__main__":
    ModernApp().mainloop()