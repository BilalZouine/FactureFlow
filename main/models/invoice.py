from dataclasses import dataclass
from typing import List

@dataclass
class InvoiceRow:
    qty: float
    unit_price: float
    total: float
    def to_dict(self):
        return {"qty": self.qty, "unit_price": self.unit_price, "total": self.total}

@dataclass
class Invoice:
    invoice_number: int
    date: str
    client_name: str
    client_ice: str
    rows: List[InvoiceRow]
    total_ht: float
    tva_rate: float
    tva_amount: float
    total_ttc: float
    reference: str = ""
    def to_dict(self):
        return {
            "invoice_number": self.invoice_number, "date": self.date,
            "reference": self.reference, "client_name": self.client_name,
            "client_ice": self.client_ice, "rows": [r.to_dict() for r in self.rows],
            "total_ht": self.total_ht, "tva_rate": self.tva_rate,
            "tva_amount": self.tva_amount, "total_ttc": self.total_ttc,
        }