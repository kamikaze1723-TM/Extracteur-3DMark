import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import matplotlib.pyplot as plt
from io import BytesIO

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

def nice_rows(summary):
    order = ["Benchmark name", "Benchmark ID", "GPU", "CPU", "RAM", "VRAM", "OS", "Driver", "API", "Resolution", "Computer", "User", "Loop count", "Best score", "Worst score", "Average score", "Stability %", "Average FPS", "Passed"]
    rows = []
    for key in order:
        value = summary.get(key)
        if value not in (None, "", []): rows.append([key, str(value)])
    return rows

def generate_chart(data, tr):
    if not data["fps_values"] and not data["scores"]:
        return None
        
    plt.figure(figsize=(7, 4))
    
    has_plotted = False
    if data["fps_values"]:
        plt.plot(range(1, len(data["fps_values"]) + 1), data["fps_values"], marker='o', color='#3B82F6', label=tr("pdf_fps"))
        max_fps = max(data["fps_values"])
        plt.ylim(0, max_fps * 1.15 if max_fps > 0 else 100)
        has_plotted = True
        
    if data["scores"] and not data["fps_values"]:
        # Only plot scores if FPS is missing, to avoid weird scaling, or use twinx
        plt.plot(range(1, len(data["scores"]) + 1), data["scores"], marker='s', color='#8B5CF6', label=tr("pdf_score"))
        max_score = max(data["scores"])
        plt.ylim(0, max_score * 1.15 if max_score > 0 else 100)
        has_plotted = True
        
    if not has_plotted:
        plt.close()
        return None
        
    plt.title(tr("pdf_perf_loops"))
    plt.xlabel(tr("pdf_loop"))
    plt.ylabel("Value")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf

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
    
    chart_buf = generate_chart(data, tr)
    if chart_buf:
        story.append(Image(chart_buf, width=160*mm, height=90*mm))
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
