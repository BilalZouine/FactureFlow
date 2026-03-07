import json
from pathlib import Path
from main.utils.errors import DataFileNotFoundError, InvalidAmountError

_JSON = Path(__file__).resolve().parent.parent.parent / "data" / "numbers_fr.json"


def _load():
    if not _JSON.exists():
        raise DataFileNotFoundError(str(_JSON))
    with open(_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


_V = _load()


def _below_1000(n):
    if n == 0:
        return ""
    u = _V["units"]
    ts = _V["tens_special"]
    t = _V["tens"]
    if n < 20:
        return u[n]
    if n < 100:
        k = str(n)
        if k in ts:
            return ts[k]
        ti = n // 10
        un = n % 10
        tw = t[ti]
        if un == 0:
            return tw
        return tw + ("-et-" if un == 1 and ti not in (8, 9) else "-") + u[un]
    h = n // 100
    r = n % 100
    hw = ("" if h == 1 else u[h] + " ") + "cent"
    if r == 0:
        return hw + ("s" if h > 1 else "")
    return hw + " " + _below_1000(r)


def number_to_french(amount):
    try:
        amount = float(amount)
    except:
        raise InvalidAmountError(amount)
    if amount < 0:
        return _V["special_words"]["negative"] + " " + number_to_french(-amount)
    # Use 2-decimal value only – never "complete" 1.99 to 2 (0.01 matters)
    amount_2d = round(amount, 2)
    main = int(amount_2d)
    cents = min(99, max(0, round((amount_2d - main) * 100)))
    if main == 0 and cents == 0:
        return _V["special_words"]["zero"].capitalize() + " " + _V["currency"]["main"]
    parts = []
    if main >= 1_000_000_000:
        b = main // 1_000_000_000
        main %= 1_000_000_000
        parts.append(_below_1000(b) + " milliard" + ("s" if b > 1 else ""))
    if main >= 1_000_000:
        m = main // 1_000_000
        main %= 1_000_000
        parts.append(_below_1000(m) + " million" + ("s" if m > 1 else ""))
    if main >= 1000:
        t = main // 1000
        main %= 1000
        parts.append(("" if t == 1 else _below_1000(t) + " ") + "mille")
    if main > 0:
        parts.append(_below_1000(main))
    orig = main
    cur = _V["currency"]["main_plural"] if orig > 1 else _V["currency"]["main"]
    res = " ".join(parts) + " " + cur
    if cents > 0:
        cl = _V["currency"]["cents_plural"] if cents > 1 else _V["currency"]["cents"]
        res += " et " + _below_1000(cents) + " " + cl
    return res[0].upper() + res[1:]


amount_to_words = number_to_french
