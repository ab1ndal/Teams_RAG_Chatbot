import uuid
import pytest
from app.embedding import embed_text
from app.pinecone_index import (
    upsert_vector,
    query_index,
    fetch_vector,
    delete_vector
)
from app.config import PINECONE_NAMESPACE

SEMANTIC_CASES = [
    ("foundations", "A spread footing distributes load from a column to the supporting soil.", "What type of foundation spreads column load to soil?"),
    ("reinforced_concrete", "Steel bars embedded in concrete provide tensile strength to structural members.", "Why is steel used inside concrete beams?"),
    ("base_isolation", "Base isolation helps structures absorb seismic forces by decoupling them from ground motion.", "How does base isolation protect buildings during an earthquake?"),
    ("load_path", "The structural load travels from the slab to beams, then to columns and finally to the foundation.", "How is gravity load transferred through a building?"),
    ("wind_load", "Lateral bracing systems resist wind-induced horizontal forces in tall buildings.", "What structural systems help resist wind loads in skyscrapers?")
]

DISTRACTOR_SENTENCES = [
    "Solar panels generate electricity from sunlight.",
    "Python is a versatile programming language.",
    "Baking bread requires yeast and flour.",
    "The Eiffel Tower is a popular landmark in Paris.",
    "Photosynthesis occurs in the leaves of plants."
]

@pytest.mark.parametrize("topic,doc_text,query_text", SEMANTIC_CASES)
class TestPineconeFunctionality:

    @pytest.fixture(autouse=True)
    def setup(self, topic, doc_text, query_text):
        self.vector_id = f"split-test-{topic}-{uuid.uuid4()}"
        self.doc_text = doc_text
        self.query_text = query_text
        self.doc_vector = embed_text(self.doc_text)
        self.query_vector = embed_text(self.query_text)
        self.metadata = {
            "file_path": f"/test_docs/{topic}.pdf",
            "chunk_id": 0,
            "snippet": self.doc_text
        }
        # Cleanup just in case
        delete_vector(self.vector_id, namespace=PINECONE_NAMESPACE)

    def test_upsert_vector(self, topic, doc_text, query_text):
        upsert_vector(self.vector_id, self.doc_vector, self.metadata, namespace=PINECONE_NAMESPACE)
        result = fetch_vector(self.vector_id, namespace=PINECONE_NAMESPACE)
        assert self.vector_id in result.vectors

    def test_fetch_vector(self, topic, doc_text, query_text):
        upsert_vector(self.vector_id, self.doc_vector, self.metadata, namespace=PINECONE_NAMESPACE)
        result = fetch_vector(self.vector_id, namespace=PINECONE_NAMESPACE)
        assert result.vectors[self.vector_id].metadata["file_path"] == self.metadata["file_path"]

    def test_query_vector(self, topic, doc_text, query_text):
        upsert_vector(self.vector_id, self.doc_vector, self.metadata, namespace=PINECONE_NAMESPACE)
        result = query_index(self.doc_vector, top_k=2, namespace=PINECONE_NAMESPACE)
        ids = [m["id"] for m in result["matches"]]
        assert self.vector_id in ids

    def test_semantic_match(self, topic, doc_text, query_text):
        # Upsert distractors
        for i, text in enumerate(DISTRACTOR_SENTENCES):
            dummy_id = f"dummy-{uuid.uuid4()}"
            dummy_vector = embed_text(text)
            dummy_metadata = {
                "file_path": f"/dummy/{i}.txt",
                "chunk_id": 0,
                "snippet": text
            }
            upsert_vector(dummy_id, dummy_vector, dummy_metadata, namespace=PINECONE_NAMESPACE)

        upsert_vector(self.vector_id, self.doc_vector, self.metadata, namespace=PINECONE_NAMESPACE)
        result = query_index(self.query_vector, top_k=5, namespace=PINECONE_NAMESPACE)
        ids = [m["id"] for m in result["matches"]]

        # Log scores for debug
        print(f"\n🔍 [{topic}] Top matches:")
        for m in result["matches"]:
            print(f"  ID: {m['id']}  Score: {m['score']:.4f}")

        assert self.vector_id in ids, f"Expected semantic match for {self.vector_id} not found"

        # Cleanup
        delete_vector(self.vector_id, namespace=PINECONE_NAMESPACE)

    def test_delete_vector(self, topic, doc_text, query_text):
        upsert_vector(self.vector_id, self.doc_vector, self.metadata, namespace=PINECONE_NAMESPACE)
        delete_vector(self.vector_id, namespace=PINECONE_NAMESPACE)
        result = fetch_vector(self.vector_id, namespace=PINECONE_NAMESPACE)
        assert self.vector_id not in result.vectors
