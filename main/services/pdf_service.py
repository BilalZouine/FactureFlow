from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from main.config import (
    COMPANY_NAME,
    COMPANY_ADDRESS,
    COMPANY_ICE,
    COMPANY_IF,
    COMPANY_RC,
    COMPANY_CNSS,
    COMPANY_DESIGNATION,
    COMPANY_CLIENT_NAME,
    COMPANY_CLIENT_ICE,
)
from main.models.invoice import Invoice
from main.services.number_service import number_to_french
from main.utils.errors import PDFGenerationError

TABLE_TOP_MARGIN = 0.5 * cm  # space above each table

_PAD = [
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]


def _st(n, **kw):
    d = dict(fontName="Helvetica", fontSize=9, leading=12)
    d.update(kw)
    return ParagraphStyle(n, **d)


S = {
    "title": _st(
        "t", fontName="Helvetica-Bold", fontSize=28, alignment=TA_CENTER, spaceAfter=14
    ),
    "bc": _st("bc", fontName="Helvetica-Bold", alignment=TA_CENTER),
    "nc": _st("nc", alignment=TA_CENTER),
    "nl": _st("nl", alignment=TA_LEFT),
    "bl": _st("bl", fontName="Helvetica-Bold", alignment=TA_LEFT),
    "sc": _st("sc", fontSize=7, alignment=TA_CENTER),
    "designation": _st("designation", fontName="Helvetica-Oblique", alignment=TA_CENTER),
}


def _fmt_num(x):
    """French format: 2 decimals only, no rounding to whole number (1.99 stays 1,99)."""
    s = f"{float(x):,.2f}"
    return s.replace(",", " ").replace(".", ",")


VIDE_PLACEHOLDER = "/// /// ///"


def _vide(text):
    """Return text if non-empty, else VIDE_PLACEHOLDER so reader sees the field is intentionally empty."""
    return (text or "").strip() or VIDE_PLACEHOLDER


def _p(text, s):    
    return Paragraph(str(text), S[s])


def _client_block(inv, pw):
    client_name = (inv.client_name or COMPANY_CLIENT_NAME) or ""
    client_ice = (inv.client_ice or COMPANY_CLIENT_ICE) or ""
    d = [
        [_p("ENTREPRISE", "bc"), _p(client_name, "bc")],
        [_p("ICE", "bc"), _p(client_ice, "nc")],
    ]
    inner = Table(d, colWidths=[4 * cm, 8 * cm])
    inner.setStyle(
        TableStyle(
            [
                *_PAD,
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    outer = Table([[None, inner]], colWidths=[pw - 4 * cm - 12 * cm, 12 * cm])
    outer.setStyle(
        TableStyle(
            [("ALIGN", (1, 0), (1, 0), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
        )
    )
    return outer


def _header(inv):
    d = [
        [_p("FACTURE N°", "bc"), _p("DATE", "bc"), _p("Référence", "bc")],
        [
            _p(str(inv.invoice_number).zfill(5), "nc"),
            _p(inv.date, "nc"),
            _p(inv.reference, "nc"),
        ],
    ]
    t = Table(d, colWidths=[5 * cm, 4 * cm, 4 * cm])
    t.setStyle(
        TableStyle(
            [
                *_PAD,
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )
    return t


def _items(inv):
    cw = [7 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]
    n = len(inv.rows)
    rows = [
        [
            _p("Désignations", "bc"),
            _p("Quantités", "bc"),
            _p("P.U (H.T)", "bc"),
            _p("Total (H.T)", "bc"),
        ]
    ]
    # One designation spanning all data rows (from env: e.g. TRANSPORT DE BETON)
    designation = _p(COMPANY_DESIGNATION, "designation")
    for i, r in enumerate(inv.rows):
        # Only first data row gets the designation text; cell will be spanned
        lbl = designation if i == 0 else ""
        rows.append(
            [
                lbl,
                _p(f"{r.qty:g}".replace(".", ","), "nc"),
                _p(_fmt_num(r.unit_price), "nc"),
                _p(_fmt_num(r.total), "nc"),
            ]
        )
    n_data = len(inv.rows)  # last data row index = n_data (1-based from row 1)
    rows += [
        ['', _p("", "nc"), _p("TOTAL H.T", "bc"), _p(_fmt_num(inv.total_ht), "nc")],
        [
            "",
            _p("", "nc"),
            _p(f"T.V.A {int(inv.tva_rate)} %", "bc"),
            _p(_fmt_num(inv.tva_amount), "nc"),
        ],
        ['', _p("", "nc"), _p("TOTAL T.T.C", "bc"), _p(_fmt_num(inv.total_ttc), "nc")],
    ]
    nd = len(rows)
    t = Table(rows, colWidths=cw)
    t.setStyle(
        TableStyle(
            [
                *_PAD,
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                # Right-align numeric columns (Quantités, P.U, Total)
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                # Designation cell spans all data rows
                ("SPAN", (0, 1), (0, n_data)),
                
 
                ("SPAN", (0, nd - 3), (1, nd - 1)),


                # Remove bottom border (overrides BOX's bottom edge on last row)
                ("LINEBELOW", (0, nd - 3), (1, nd - 1), 2, colors.white),

                # Also remove the inner vertical line between col 0 and col 1 in spanned rows
                ("LINEBEFORE", (0, nd - 3), (0, nd - 1), 2, colors.white),

                ("GRID", (2, nd - 3), (-1, nd - 1), 1.5, colors.black),



            ]
        )
    )
    return t


def generate_pdf(inv: Invoice) -> BytesIO:
    try:
        buf = BytesIO()
        pw, _ = A4
        num_str = str(inv.invoice_number).zfill(5)
        doc_title = f"{COMPANY_NAME} - Facture N° {num_str}"
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=1.5 * cm,
            bottomMargin=2 * cm,
            title=doc_title,
        )
        doc.build(
            [
                _p(COMPANY_NAME, "title"),
                Spacer(1, 0.4 * cm),
                Spacer(1, TABLE_TOP_MARGIN),
                _client_block(inv, pw),
                Spacer(1, TABLE_TOP_MARGIN),
                _header(inv),
                Spacer(1, TABLE_TOP_MARGIN),
                _items(inv),
                Spacer(1, 0.3 * cm),
                _p("Arrêter la présente facture à la somme de :", "nl"),
                _p(number_to_french(inv.total_ttc), "bl"),
                Spacer(1, 1.5 * cm),
                HRFlowable(width="100%", thickness=0.5, color=colors.black),
                Spacer(1, 0.15 * cm),
                _p(f"Siège social : {COMPANY_ADDRESS}", "sc"),
                _p(
                    f"ICE {COMPANY_ICE} – IF {COMPANY_IF} – RC {COMPANY_RC} – CNSS {COMPANY_CNSS}",
                    "sc",
                ),
            ]
        )
        buf.seek(0)
        return buf
    except Exception as e:
        raise PDFGenerationError(str(e))


def safe_filename(inv: Invoice, prefix=""):
    """Filename: CompanyName_Facture_00001_ClientName.pdf"""
    company = COMPANY_NAME.replace(" ", "_").replace("/", "-")
    clean = inv.client_name.replace(" ", "_").replace("/", "-")
    num_str = str(inv.invoice_number).zfill(5)
    return f"{prefix}{company}_Facture_{num_str}_{clean}.pdf"
