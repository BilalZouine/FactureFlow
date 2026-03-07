import pandas as pd
from main.utils.errors import (
    UnsupportedFileTypeError,
    EmptyFileError,
    MissingColumnError,
)


# Canonical keys expected by invoice_service
REQUIRED_KEYS = ["prix", "qty"]
OPTIONAL_KEYS = ["client", "date_livr"]

# Possible header variants (case-insensitive match after strip)
PRIX_ALIASES = ("prix", "unit price", "prix unitaire", "pu")
QTY_ALIASES = ("qté livr.", "qté", "quantité", "qty", "quantité livrée", "quantity")
CLIENT_ALIASES = ("client", "client name", "nom client")
DATE_LIVR_ALIASES = ("date livr.", "date livr/", "date livr", "date livraison", "date de livraison", "delivery date")


def _normalize(s):
    return (s or "").strip().lower()


def detect_columns(column_names):
    """
    Map a list of actual column names to the logical keys expected by invoice_service.
    Returns a dict with at least 'prix' and 'qty'; optionally 'client'.
    Raises MissingColumnError if required columns are not found.
    """
    col_map = {}
    names_lower = {_normalize(c): c for c in column_names}

    # prix
    for alias in PRIX_ALIASES:
        if alias in names_lower:
            col_map["prix"] = names_lower[alias]
            break
    if "prix" not in col_map:
        for name, orig in names_lower.items():
            if "prix" in name and "total" not in name and "coût" not in name:
                col_map["prix"] = orig
                break
    if "prix" not in col_map:
        raise MissingColumnError(
            ["prix (e.g. PRIX)"],
            list(column_names),
        )

    # qty
    for alias in QTY_ALIASES:
        if alias in names_lower:
            col_map["qty"] = names_lower[alias]
            break
    if "qty" not in col_map:
        for name, orig in names_lower.items():
            if "qté" in name or "quantité" in name or name == "qty":
                col_map["qty"] = orig
                break
    if "qty" not in col_map:
        raise MissingColumnError(
            ["qty (e.g. Qté livr.)"],
            list(column_names),
        )

    # client (optional)
    for alias in CLIENT_ALIASES:
        if alias in names_lower:
            col_map["client"] = names_lower[alias]
            break
    if "client" not in col_map:
        for name, orig in names_lower.items():
            if name == "client":
                col_map["client"] = orig
                break

    # date livr (optional) – for facture date = last day of month
    for alias in DATE_LIVR_ALIASES:
        if alias in names_lower:
            col_map["date_livr"] = names_lower[alias]
            break
    if "date_livr" not in col_map:
        for name, orig in names_lower.items():
            if "date" in name and "livr" in name:
                col_map["date_livr"] = orig
                break

    return col_map


def parse_file(file_storage):
    """
    Read an uploaded file (Excel or CSV), validate it, and return (DataFrame, col_map).
    Raises UnsupportedFileTypeError, EmptyFileError, or MissingColumnError as appropriate.
    """
    filename = (file_storage.filename or "").strip().lower()
    if not filename:
        from main.utils.errors import EmptyFilenameError
        raise EmptyFilenameError()

    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file_storage, engine="openpyxl" if filename.endswith(".xlsx") else None)
    elif filename.endswith(".csv"):
        df = pd.read_csv(file_storage, encoding="utf-8-sig")
    else:
        raise UnsupportedFileTypeError(file_storage.filename)

    if df is None or df.empty or len(df) == 0:
        raise EmptyFileError()

    col_map = detect_columns(list(df.columns))
    return df, col_map
