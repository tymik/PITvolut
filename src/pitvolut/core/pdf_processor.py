import json
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2

from .models import RevolutStatement, DividendTransaction

class PitvolutPDFProcessor:
    """Processes Revolut PDF statements focusing on dividend transactions."""
    
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
                text += page.extract_text() + "\n"
        return text

    def extract_metadata(self, text: str) -> Dict[str, str]:
        """
        Extract metadata from the statement.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Dictionary with metadata
        """
        metadata = {}
        
        # Extract period
        period_match = re.search(r'(\d+ [A-Za-z]+ \d{4} - \d+ [A-Za-z]+ \d{4})', text)
        if period_match:
            metadata['period'] = period_match.group(1)
        
        # Extract generation date
        gen_date_match = re.search(r'Generated on the (\d+ [A-Za-z]+ \d{4})', text)
        if gen_date_match:
            metadata['generation_date'] = gen_date_match.group(1)
        
        # Extract account holder
        holder_match = re.search(r'©\s+Revolut\s+Ltd([A-Z\s]+)', text)
        if holder_match:
            metadata['account_holder'] = holder_match.group(1).strip()
        
        # Extract summary section
        summary_match = re.search(r'Summary for Brokerage Account - USD(.*?)This statement is provided by', text, re.DOTALL)
        if summary_match:
            metadata['summary_text'] = summary_match.group(1).strip()
        
        return metadata
    
    def standardize_date(self, date_str):
        """
        Convert non-standard month abbreviations to standard ones.
        
        Args:
            date_str: Date string to standardize
            
        Returns:
            Standardized date string
        """
        # Map non-standard abbreviations to standard ones
        month_mapping = {
            "Sept": "Sep",
            "Sept.": "Sep",
            "March": "Mar",
            "April": "Apr",
            "June": "Jun",
            "July": "Jul",
            "August": "Aug",
            "October": "Oct",
            "November": "Nov",
            "December": "Dec"
        }
        
        parts = date_str.split()
        if len(parts) == 3 and parts[1] in month_mapping:
            parts[1] = month_mapping[parts[1]]
            return " ".join(parts)
        return date_str



    def parse_transactions(self, text: str) -> List[DividendTransaction]:
        """Parse dividend transactions from the statement text."""
        transactions = []
        
        # Pattern to match transaction blocks
        transaction_pattern = r'(\d+ [A-Za-z]+\.? \d{4})\s+([^\n]+?)\s+([A-Z]+)\s*\n\s*([A-Z0-9]+)\s*([A-Z]+)\s+US\$(\d+\.\d+)\s+(\d+\.\d+)\s+PLN\s+Rate:\s+(\d+\.\d+)\s*US\$(\d+(?:\.\d+)?)\s+(?:(\d+\.\d+)?\s*PLN)?US\$(\d+\.\d+)\s+(\d+\.\d+)\s+PLN'
        
        # Find all matches
        matches = re.finditer(transaction_pattern, text)
        
        for match in matches:
            try:
                date_str, security_name, symbol, isin, country, gross_usd, gross_pln, rate, tax_usd, tax_pln, net_usd, net_pln = match.groups()
                
                # Standardize date string before parsing
                standardized_date = self.standardize_date(date_str)
                
                # Handle optional tax_pln value
                if tax_pln is None or tax_pln == "":
                    tax_pln = "0.00"
                
                # Convert date string to datetime
                try:
                    date = datetime.strptime(standardized_date, "%d %b %Y")
                except ValueError:
                    # Try alternative format if standard format fails
                    date = datetime.strptime(date_str, "%d %B %Y")
                
                transaction = DividendTransaction(
                    date=date,
                    security_name=security_name.strip(),
                    symbol=symbol.strip(),
                    isin=isin.strip(),
                    country=country.strip(),
                    gross_amount_usd=Decimal(gross_usd),
                    gross_amount_pln=Decimal(gross_pln),
                    exchange_rate=Decimal(rate),
                    withholding_tax_usd=Decimal(tax_usd),
                    withholding_tax_pln=Decimal(tax_pln),
                    net_amount_usd=Decimal(net_usd),
                    net_amount_pln=Decimal(net_pln),
                    raw_text=match.group(0)
                )
                transactions.append(transaction)
            except Exception as e:
                print(f"Failed to parse transaction: {e}")
                print(f"Raw match: {match.group(0)}")
                    
        return transactions

    def process(self) -> RevolutStatement:
        """
        Process the PDF and return structured data.
        
        Returns:
            RevolutStatement object containing parsed data
        """
        raw_text = self.extract_raw_text()
        metadata = self.extract_metadata(raw_text)
        transactions = self.parse_transactions(raw_text)
        
        return RevolutStatement(
            period=metadata.get('period', ''),
            generation_date=metadata.get('generation_date', ''),
            account_holder=metadata.get('account_holder', ''),
            summary_text=metadata.get('summary_text', ''),
            transactions=transactions
        )
        
    def get_raw_json(self) -> Dict[str, Any]:
        """
        Get raw JSON representation of the PDF content.
        
        Returns:
            Dictionary with raw PDF content
        """
        raw_text = self.extract_raw_text()
        
        # Extract sections for debugging
        transactions_section = ""
        transactions_match = re.search(r'Transactions for Brokerage Account.*?end of this document', raw_text, re.DOTALL)
        if transactions_match:
            transactions_section = transactions_match.group(0)
        
        # Create a raw representation
        raw_data = {
            "file_name": self.pdf_path.name,
            "raw_text": raw_text,
            "transactions_section": transactions_section,
            # Extract a sample transaction for pattern debugging
            "sample_transaction": self._extract_sample_transaction(raw_text)
        }
        
        return raw_data
    
    def _extract_sample_transaction(self, text: str) -> Optional[str]:
        """Extract a sample transaction for debugging pattern matching."""
        pattern = r'(\d+ [A-Za-z]+ \d{4}.*?PLN)'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(0) if match else None
    
    def debug_print_json(self) -> None:
        """
        Print raw JSON representation of the PDF for debugging.
        """
        raw_data = self.get_raw_json()
        # Use json.dumps for pretty printing
        print(json.dumps(raw_data, indent=2, default=str))