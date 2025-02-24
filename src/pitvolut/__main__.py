from pitvolut.core.pdf_processor import PitvolutPDFProcessor

def main():
    """Main entry point for the application."""
    try:
        processor = PitvolutPDFProcessor("test_data/revolut_statement.pdf")
        statement = processor.process()
        
        # Work with the structured data
        print(f"Found {len(statement.transactions)} transactions")
        
        # Example: Print all exchange transactions
        exchanges = [t for t in statement.transactions if t.type == "exchange"]
        for transaction in exchanges:
            print(f"Exchange on {transaction.completed_date}: {transaction.amount}")
            
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    main()
