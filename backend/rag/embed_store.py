from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from rag.chunker import TextChunker


VECTOR_DB_DIR = Path("data/vector_store")


class ChromaVectorStore:
    def __init__(self):
        print("\nLoading embedding model...")

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded")

        print("\nConnecting to ChromaDB...")

        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name="mpgu_knowledge"
        )

        print("ChromaDB connected")

    def generate_embeddings(self, chunks):
        for chunk in chunks:
            print(f"\nEmbedding: {chunk['id']}")

            embedding = self.embedding_model.encode(
                chunk["text"]
            ).tolist()

            self.collection.add(
                ids=[chunk["id"]],
                documents=[chunk["text"]],
                embeddings=[embedding],
                metadatas=[
                    {
                        "source": chunk["source"]
                    }
                ]
            )

    def run(self):
        print("\nStarting chunking pipeline...")

        chunker = TextChunker()

        chunks = chunker.process_files()

        print(f"\nTotal chunks generated: {len(chunks)}")

        print("\nStarting embedding generation...")

        self.generate_embeddings(chunks)

        print("\nEmbeddings stored successfully!")

        print("\nVector database location:")
        print(VECTOR_DB_DIR.resolve())


if __name__ == "__main__":
    store = ChromaVectorStore()

    store.run()