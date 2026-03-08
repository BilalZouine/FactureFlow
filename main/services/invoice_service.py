from calendar import monthrange
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

import pandas as pd
from main.config import COMPANY_CLIENT_ICE, COMPANY_CLIENT_NAME, TVA_RATE
from main.models.invoice import Invoice, InvoiceRow
from main.utils.errors import NoNumericDataError

ENTREPRISE = COMPANY_CLIENT_NAME
_ICE = COMPANY_CLIENT_ICE
_TVA = Decimal(TVA_RATE)
_TWO = Decimal("0.01")  # 2 decimal places – never round to whole number


def _to2(x):
    """Round to 2 decimals only (sensible: 1.99 stays 1.99, no completion to 2)."""
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _last_day_of_month(dt):
    """Return date as last day of the same month (e.g. 2/13/2026 -> 28/02/2026)."""
    _, last = monthrange(dt.year, dt.month)
    return dt.replace(day=last)


def _facture_date_from_df(df, col_map):
    """Facture date = last day of month of latest delivery date. Format dd/mm/yyyy."""
    if "date_livr" not in col_map:
        d = datetime.now()
        last = _last_day_of_month(d)
        return last.strftime("%d/%m/%Y")
    dc = col_map["date_livr"]
    try:
        parsed = pd.to_datetime(df[dc], errors="coerce", dayfirst=False)
        parsed = parsed.dropna()
        if parsed.empty:
            d = datetime.now()
        else:
            d = parsed.max()
            if getattr(d, "to_pydatetime", None):
                d = d.to_pydatetime()
        last = _last_day_of_month(d)
        return last.strftime("%d/%m/%Y")
    except Exception:
        d = datetime.now()
        return _last_day_of_month(d).strftime("%d/%m/%Y")


def build_invoice(df, col_map, invoice_number):
    pc = col_map["prix"]
    qc = col_map["qty"]
    df = df.copy()
    df[pc] = pd.to_numeric(df[pc], errors="coerce")
    df[qc] = pd.to_numeric(df[qc], errors="coerce")
    df = df.dropna(subset=[pc, qc])
    df = df[(df[pc] > 0) & (df[qc] > 0)]
    if df.empty:
        raise NoNumericDataError()

    client = ENTREPRISE or "CLIENT"
    if not ENTREPRISE and "client" in col_map:
        v = df[col_map["client"]].dropna()
        if not v.empty:
            client = str(v.iloc[0]).strip()

    g = df.groupby(pc)[qc].sum().reset_index()
    g.columns = ["unit_price", "qty"]
    g["total"] = g["unit_price"] * g["qty"]
    g = g.sort_values("unit_price").reset_index(drop=True)

    rows = []
    for _, r in g.iterrows():
        qty = Decimal(str(r["qty"]))
        unit_price = Decimal(str(r["unit_price"]))
        total = (qty * unit_price).quantize(_TWO, rounding=ROUND_HALF_UP)
        rows.append(
            InvoiceRow(
                qty=_to2(qty),
                unit_price=_to2(unit_price),
                total=_to2(total),
            )
        )
    ht = sum(Decimal(str(row.total)) for row in rows)
    tva = (ht * _TVA / 100).quantize(_TWO, rounding=ROUND_HALF_UP)
    ttc = (ht + tva).quantize(_TWO, rounding=ROUND_HALF_UP)
    facture_date = _facture_date_from_df(df, col_map)
    return Invoice(
        invoice_number=invoice_number,
        date=facture_date,
        reference="",
        client_name=client,
        client_ice=_ICE,
        rows=rows,
        total_ht=_to2(ht),
        tva_rate=float(_TVA),
        tva_amount=_to2(tva),
        total_ttc=_to2(ttc),
    )


def build_invoices_per_client(df, col_map):
    from main.utils.errors import NoNumericDataError

    if "client" not in col_map:
        return [build_invoice(df, col_map, 0)]
    cc = col_map["client"]
    invs = []
    for cl in df[cc].dropna().unique():
        try:
            invs.append(build_invoice(df[df[cc] == cl].copy(), col_map, 0))
        except NoNumericDataError:
            pass
    return invs
