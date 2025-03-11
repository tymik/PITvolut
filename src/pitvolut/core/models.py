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
    gross_tax: Decimal = Decimal("0.00")
    exchange_rate: Decimal
    withholding_tax_usd: Decimal
    withholding_tax_pln: Decimal
    net_amount_usd: Decimal
    net_amount_pln: Decimal
    raw_text: str
    transaction_type: str = ""
    tax_to_pay_pln: Decimal = Decimal("0.00")

    def process_transaction(self):
        self.determine_transaction_type()
        if self.transaction_type == "dividend":
            self.calculate_tax()

    def determine_transaction_type(self):
        if "dividend" in self.security_name.lower():
            self.transaction_type = "dividend"
        else:
            self.transaction_type = "other"

    def calculate_tax(self):
        tax_rate = Decimal("0.19")
        self.gross_tax = self.gross_amount_pln * tax_rate
        self.tax_to_pay_pln = max(
            self.gross_tax - self.withholding_tax_pln, Decimal("0.00")
        )


class RevolutStatement(BaseModel):
    """Represents the parsed Revolut statement."""

    period: str
    generation_date: str
    account_holder: str
    summary_text: str
    transactions: List[DividendTransaction]
