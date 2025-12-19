from typing import List, Dict, Any, Optional


def _parse_value(text: str) -> Optional[float]:
    if text is None:
        return None
    t = text.strip()
    if t == "" or t == "-" or "暫停" in t:
        return None
    # remove commas and other non-numeric chars except dot
    cleaned = "".join(c for c in t if (c.isdigit() or c == "."))
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_rates(raw_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize extracted rows into consistent dicts.

    Each row will contain:
      - currency: str
      - buy: Optional[float]
      - sell: Optional[float]
      - trade: bool (True if both buy and sell present)
      - raw: original row dict
    """
    out = []
    if not raw_rows:
        return out
    for r in raw_rows:
        currency = r.get("幣別") or r.get("currency") or ""
        buy_text = r.get("本行即期買入") or r.get("本行現金買入") or r.get("buy") or ""
        sell_text = r.get("本行即期賣出") or r.get("本行現金賣出") or r.get("sell") or ""
        buy = _parse_value(buy_text)
        sell = _parse_value(sell_text)
        trade = (buy is not None) and (sell is not None)
        out.append({"currency": currency.strip(), "buy": buy, "sell": sell, "trade": trade, "raw": r})
    return out


__all__ = ["normalize_rates"]
