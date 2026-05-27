from pathlib import Path


RAW_DATA_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


class TextChunker:
    def __init__(self, chunk_size=300, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def clean_text(self, text: str):
        text = text.replace("\n", " ")

        text = " ".join(text.split())

        return text

    def split_text(self, text: str):
        text = self.clean_text(text)

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):
            end = start + self.chunk_size

            chunk_words = words[start:end]

            chunk = " ".join(chunk_words)

            if len(chunk.strip()) > 50:
                chunks.append(chunk)

            start += self.chunk_size - self.overlap

        return chunks

    def process_files(self):
        all_chunks = []

        txt_files = list(RAW_DATA_DIR.glob("*.txt"))

        chunk_id = 0

        seen_chunks = set()

        for file_path in txt_files:
            print(f"\nProcessing: {file_path.name}")

            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            chunks = self.split_text(text)

            print(f"Created {len(chunks)} chunks")

            for i, chunk in enumerate(chunks):
                normalized_chunk = chunk.strip().lower()

                if normalized_chunk in seen_chunks:
                    continue

                seen_chunks.add(normalized_chunk)

                all_chunks.append({
                    "id": f"{file_path.stem}_chunk_{i}",
                    "text": chunk,
                    "source": file_path.name
                })

                chunk_id += 1

        return all_chunks


if __name__ == "__main__":
    chunker = TextChunker()

    chunks = chunker.process_files()

    print(f"\nTotal chunks: {len(chunks)}")

    print("\nFirst chunk preview:\n")

    print(chunks[0]["text"][:1000])