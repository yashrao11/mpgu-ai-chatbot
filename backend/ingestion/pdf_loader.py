from pathlib import Path
import re
import fitz  # PyMuPDF


PDF_DIR = Path("ingestion/pdfs")

RAW_DIR = Path("data/raw")

RAW_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_text_from_pdf(pdf_path: Path) -> str:

    document = fitz.open(pdf_path)

    all_text = []

    for page in document:

        text = page.get_text("text")

        if text.strip():
            all_text.append(text)

    document.close()

    return clean_text("\n".join(all_text))


def save_text_file(text: str, output_path: Path):

    output_path.write_text(
        text,
        encoding="utf-8"
    )


def process_pdfs():

    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:

        print("\nNo PDF files found")

        print(f"Expected location: {PDF_DIR.resolve()}")

        return

    print(f"\nFound {len(pdf_files)} PDF file(s)\n")

    for pdf_file in pdf_files:

        print("=" * 70)

        print(f"\nProcessing: {pdf_file.name}")

        try:

            extracted_text = extract_text_from_pdf(
                pdf_file
            )

            if not extracted_text:

                print("\nNo text extracted")

                continue

            output_file = (
                RAW_DIR /
                f"{pdf_file.stem}.txt"
            )

            save_text_file(
                extracted_text,
                output_file
            )

            print(
                f"\nSaved extracted text to:\n"
                f"{output_file}"
            )

            print(
                f"\nCharacters extracted: "
                f"{len(extracted_text)}"
            )

        except Exception as e:

            print(
                f"\nFailed processing "
                f"{pdf_file.name}"
            )

            print(f"Error: {e}")

    print("\nPDF ingestion completed")


if __name__ == "__main__":

    process_pdfs()