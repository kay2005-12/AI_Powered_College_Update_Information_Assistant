import os
import requests
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

HF_TOKEN = os.getenv("HF_TOKEN")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")

HF_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5/pipeline/feature-extraction"
TYPESENSE_URL = "https://1vqzru2ahpengj6sp-1.a1.typesense.net"
COLLECTION_NAME = "cemk_documents"


def get_query_embedding(query):
    response = requests.post(
        HF_URL,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"inputs": query},
    )

    response.raise_for_status()
    raw_embedding = response.json()

    while isinstance(raw_embedding[0], list):
        raw_embedding = raw_embedding[0]

    return raw_embedding


def vector_search(embedding, top_k=5):
    vector = ",".join(map(str, embedding))

    response = requests.post(
        f"{TYPESENSE_URL}/multi_search",
        headers={
            "X-TYPESENSE-API-KEY": TYPESENSE_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "searches": [{
                "collection": COLLECTION_NAME,
                "q": "*",  
                "vector_query": f"embedding:([{vector}], k:{top_k})",
            }]
        },
    )

    response.raise_for_status()
    return response.json()


def retrieve(query, top_k=5):
    embedding = get_query_embedding(query)
    results = vector_search(embedding, top_k=top_k)

    hits = results.get("results", [{}])[0].get("hits", [])

    return [hit["document"] for hit in hits]


if __name__ == "__main__":
    question = input("Ask CEMK: ")
    documents = retrieve(question, top_k=5)

    print(f"\nTotal Retrieved: {len(documents)}\n")
    for doc in documents:
        print(f"Title: {doc.get('title')}")
        print(f"Text: {doc.get('text')}")
        print("---")

