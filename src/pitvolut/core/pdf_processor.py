from pathlib import Path
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple
import PyPDF2

from .models import RevolutStatement, Transaction

class PitvolutPDFProcessor:
    """Processes Revolut PDF statements focusing on transaction data."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the PDF processor.
        
        Args:
            pdf_path: Path to the PDF file to process
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    def extract_raw_text(self) -> str:
        """
        Extract all text content from the PDF.
        
        Returns:
            String containing all text from the PDF
        """
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def split_content(self, text: str) -> Tuple[str, str, str]:
        """
        Split PDF content into header, transactions table, and footer.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Tuple of (header_text, table_text, footer_text)
        """
        # These patterns need to be adjusted based on actual Revolut PDF structure
        table_start_pattern = r"Completed Date.*Balance"
        table_end_pattern = r"End of statement"
        
        # Split content
        parts = re.split(table_start_pattern, text, maxsplit=1)
        header = parts[0].strip() if len(parts) > 1 else ""
        
        if len(parts) > 1:
            table_and_footer = parts[1]
            parts = re.split(table_end_pattern, table_and_footer, maxsplit=1)
            table = parts[0].strip()
            footer = parts[1].strip() if len(parts) > 1 else ""
        else:
            table = ""
            footer = ""
            
        return header, table, footer

    def parse_transactions(self, table_text: str) -> List[Transaction]:
        """
        Parse transaction table text into Transaction objects.
        
        Args:
            table_text: Text containing the transactions table
            
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        # Split into lines and process each transaction
        lines = table_text.split('\n')
        for line in lines:
            if not line.strip():
                continue
                
            try:
                # This regex pattern needs to be adjusted based on actual Revolut PDF format
                pattern = r"(\d{2}-\d{2}-\d{4})\s+(.*?)\s+([-+]?\d+\.\d{2})\s+([-+]?\d+\.\d{2})\s+([-+]?\d+\.\d{2})"
                match = re.match(pattern, line)
                
                if match:
                    date_str, desc, amount, fee, balance = match.groups()
                    
                    transaction = Transaction(
                        completed_date=datetime.strptime(date_str, "%d-%m-%Y"),
                        description=desc.strip(),
                        amount=Decimal(amount),
                        fee=Decimal(fee),
                        balance=Decimal(balance),
                        type=self._determine_transaction_type(desc),
                        raw_text=line.strip()
                    )
                    transactions.append(transaction)
            except Exception as e:
                print(f"Failed to parse transaction line: {line}")
                print(f"Error: {e}")
                
        return transactions

    def _determine_transaction_type(self, description: str) -> str:
        """
        Determine transaction type based on description.
        
        Args:
            description: Transaction description
            
        Returns:
            Transaction type string
        """
        # This needs to be expanded based on actual Revolut transaction types
        if "EXCHANGE" in description.upper():
            return "exchange"
        elif "CARD PAYMENT" in description.upper():
            return "payment"
        elif "TRANSFER" in description.upper():
            return "transfer"
        return "other"

    def process(self) -> RevolutStatement:
        """
        Process the PDF and return structured data.
        
        Returns:
            RevolutStatement object containing parsed data
        """
        raw_text = self.extract_raw_text()
        header, table, footer = self.split_content(raw_text)
        transactions = self.parse_transactions(table)
        
        return RevolutStatement(
            header_text=header,
            footer_text=footer,
            transactions=transactions
        )
