import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from retriver import retrieve


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)


prompt = ChatPromptTemplate.from_template("""
You are a helpful CEMK college assistant.

Answer the question using ONLY the provided context.
Give a concise answer in 2–4 sentences, including one relevant supporting detail from the context.

If the answer is not present in the context, say:
"I could not find this information in the CEMK data."

Context:
{context}

Question:
{question}

Answer:
""")

chain = prompt | llm | StrOutputParser()


def generate_answer(question: str) -> dict:
    documents = retrieve(
        question,
        top_k=5
    )

    context = "\n\n---\n\n".join(
        doc.get("text", "") if isinstance(doc, dict) else str(doc)
        for doc in documents
    )

    answer = chain.invoke({
        "question": question,
        "context": context
    })

    # FIXED: Output format now matches LangSmith evaluators criteria
    return {
        "answer": answer,
        "documents": documents
    }


if __name__ == "__main__":
    question = input("Ask CEMK: ")
    result = generate_answer(question)
    print("\nAnswer:")
    print(result["answer"])