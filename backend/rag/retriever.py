import chromadb

from sentence_transformers import SentenceTransformer


class Retriever:
    def __init__(self):
        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Connecting to ChromaDB...")

        self.client = chromadb.PersistentClient(
            path="data/vector_store"
        )

        self.collection = self.client.get_collection(
            name="mpgu_knowledge"
        )

        print("Retriever ready")

    def search(self, query: str, top_k=4):
        print(f"\nSearching for: {query}")

        query_embedding = self.embedding_model.encode(
            query
        ).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        distances = results["distances"][0]

        retrieved_chunks = []

        for doc, meta, distance in zip(
            documents,
            metadatas,
            distances
        ):
            retrieved_chunks.append({
                "text": doc,
                "source": meta["source"],
                "distance": distance
            })

        return retrieved_chunks


retriever = Retriever()


if __name__ == "__main__":
    query = input("\nEnter query: ")

    results = retriever.search(query)

    print("\nRetrieved Results:\n")

    for i, result in enumerate(results, start=1):
        print("=" * 80)

        print(f"\nResult {i}")

        print(f"\nSource: {result['source']}")

        print(f"\nDistance: {result['distance']}")

        print(f"\nText:\n")

        print(result["text"][:1000])