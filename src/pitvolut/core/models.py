from typing import List, Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class DividendTransaction(BaseModel):
    """Represents a dividend transaction from Revolut statement."""
    date: date
    security_name: str
    symbol: str
    isin: str
    country: str
    gross_amount_usd: Decimal
    gross_amount_pln: Decimal
    exchange_rate: Decimal
    withholding_tax_usd: Decimal
    withholding_tax_pln: Decimal
    net_amount_usd: Decimal
    net_amount_pln: Decimal
    raw_text: str

class RevolutStatement(BaseModel):
    """Represents the parsed Revolut statement."""
    period: str
    generation_date: str
    account_holder: str
    summary_text: str
    transactions: List[DividendTransaction]
