import os
import subprocess
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A6
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def ar(text):
    if not text:
        return ""
    return get_display(reshape(str(text)))


def generate_invoice_pdf(invoice_data, output_filename="invoice.pdf"):
    """دالة إنشاء الفاتورة PDF وفتحها للطباعة"""
    doc = SimpleDocTemplate(
        output_filename, pagesize=A6, rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15
    )
    story = []

    # تسجيل خط يدعم العربية (إذا كان متوفر بالنظام أو المجلد)
    if os.path.exists("arial.ttf"):
        pdfmetrics.registerFont(TTFont("ArabicFont", "arial.ttf"))
        font_name = "ArabicFont"
    else:
        font_name = "Helvetica"

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleStyle", fontName=font_name, fontSize=13, alignment=1, textColor=colors.HexColor("#0F172A")
    )
    cell_style = ParagraphStyle(
        name="CellStyle", fontName=font_name, fontSize=9, alignment=2, textColor=colors.HexColor("#1E293B")
    )

    story.append(Paragraph(ar("⚡ نظام إلكترو للطاقة الكهربائية"), title_style))
    story.append(Paragraph(ar("فاتورة استهلاك كهرباء"), title_style))
    story.append(Spacer(1, 10))

    table_data = [
        [Paragraph(ar(invoice_data.get('user_name')), cell_style), Paragraph(ar("اسم المشترك:"), cell_style)],
        [Paragraph(ar(invoice_data.get('meter_id')), cell_style), Paragraph(ar("رقم العداد:"), cell_style)],
        [Paragraph(ar(str(invoice_data.get('consumption')) + " ك.و"), cell_style), Paragraph(ar("الاستهلاك:"), cell_style)],
        [Paragraph(ar(str(invoice_data.get('price')) + " ريال"), cell_style), Paragraph(ar("سعر الواط/الكيلو:"), cell_style)],
        [Paragraph(ar(str(invoice_data.get('total')) + " ريال"), cell_style), Paragraph(ar("الإجمالي:"), cell_style)],
        [Paragraph(ar(invoice_data.get('status')), cell_style), Paragraph(ar("حالة السداد:"), cell_style)]
    ]

    if invoice_data.get('write'):
        table_data.append([Paragraph(ar(invoice_data.get('write')), cell_style), Paragraph(ar("ملاحظات / الآجل:"), cell_style)])

    table_data.append([Paragraph(ar(invoice_data.get('date')), cell_style), Paragraph(ar("التاريخ:"), cell_style)])

    t = Table(table_data, colWidths=[150, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(t)
    doc.build(story)

    # فتح الملف تلقائياً للطباعة
    if os.name == 'nt':
        os.startfile(output_filename)
    else:
        subprocess.call(["open", output_filename])
