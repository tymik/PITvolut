from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

class Transaction(BaseModel):
    """Represents a single transaction from Revolut statement."""
    completed_date: datetime
    description: str
    amount: Decimal
    fee: Decimal
    balance: Decimal
    type: str
    raw_text: str  # Keep original text for debugging

class RevolutStatement(BaseModel):
    """Represents the parsed Revolut statement."""
    header_text: str  # Text before the transactions table
    footer_text: str  # Text after the transactions table
    transactions: List[Transaction]
