import argparse
from decimal import Decimal
from pitvolut.core.pdf_processor import PitvolutPDFProcessor


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Process Revolut PDF statements for PIT-38 tax declaration"
    )
    parser.add_argument("pdf_path", help="Path to the Revolut PDF statement")
    parser.add_argument(
        "--debug", action="store_true", help="Print raw JSON for debugging"
    )
    args = parser.parse_args()

    try:
        processor = PitvolutPDFProcessor(args.pdf_path)

        if args.debug:
            # Print raw JSON for debugging
            processor.debug_print_json()
        else:
            # Normal processing
            statement = processor.process()

            total_gross_amount_pln = Decimal("0.00")
            total_withholding_tax_pln = Decimal("0.00")
            total_gross_tax = Decimal("0.00")
            total_tax_to_pay_pln = Decimal("0.00")

            print(f"Found {len(statement.transactions)} transactions")

            # Print summary
            for transaction in statement.transactions:
                tax_info = (
                    f"Tax to pay: {transaction.tax_to_pay_pln:.2f} PLN"
                    if transaction.transaction_type == "dividend"
                    else ""
                )
                print(
                    f"{transaction.date}: {transaction.gross_amount_pln} PLN ({transaction.security_name}) | Type: {transaction.transaction_type} | Withholding tax: {transaction.withholding_tax_pln} PLN | {tax_info}"
                )

                total_gross_amount_pln += transaction.gross_amount_pln
                total_withholding_tax_pln += transaction.withholding_tax_pln
                total_gross_tax += transaction.gross_tax
                total_tax_to_pay_pln += transaction.tax_to_pay_pln

            summary = {
                "total_gross_amount_pln": total_gross_amount_pln,
                "total_withholding_tax_pln": total_withholding_tax_pln,
                "total_gross_tax": total_gross_tax,
                "total_tax_to_pay_pln": total_tax_to_pay_pln,
            }

            print("\n\n\n")
            print("Summary of transactions:")
            print(f"Total gross amount: {summary['total_gross_amount_pln']:.2f} PLN")
            print(
                f"Total withholding tax: {summary['total_withholding_tax_pln']:.2f} PLN"
            )
            print(f"Total gross tax: {summary['total_gross_tax']:.2f} PLN")
            print(f"Total tax to pay: {summary['total_tax_to_pay_pln']:.2f} PLN")

    except Exception as e:
        print(f"Error processing PDF: {e}")


if __name__ == "__main__":
    main()
