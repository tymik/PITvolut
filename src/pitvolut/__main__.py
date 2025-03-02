import argparse
from pitvolut.core.pdf_processor import PitvolutPDFProcessor

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process Revolut PDF statements for PIT-38 tax declaration')
    parser.add_argument('pdf_path', help='Path to the Revolut PDF statement')
    parser.add_argument('--debug', action='store_true', help='Print raw JSON for debugging')
    args = parser.parse_args()
    
    try:
        processor = PitvolutPDFProcessor(args.pdf_path)
        
        if args.debug:
            # Print raw JSON for debugging
            processor.debug_print_json()
        else:
            # Normal processing
            statement = processor.process()
            print(f"Found {len(statement.transactions)} transactions")
            
            # Print summary
            for transaction in statement.transactions:
                print(f"{transaction.date}: {transaction.gross_amount_pln} ({transaction.security_name}), tax: {transaction.withholding_tax_pln}")
                
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    main()
