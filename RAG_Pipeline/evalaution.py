import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langsmith import Client
from langchain_groq import ChatGroq

load_dotenv()

client = Client()

grader_llm = ChatGroq(
    model="openai/gpt-oss-120b",  
    temperature=0
)

# Helper function to extract document text safely
def _extract_doc_text(doc) -> str:
    if isinstance(doc, str):
        return doc
    if isinstance(doc, dict):
        return doc.get("text") or doc.get("content") or doc.get("page_content", "")
    if hasattr(doc, "page_content"):
        return doc.page_content
    return str(doc)

# =========================
# Correctness Evaluator
# =========================

class CorrectnessGrade(TypedDict):
    explanation: Annotated[str, "Explain your reasoning for the score"]
    correct: Annotated[bool, "True if the answer is correct"]

correctness_llm = grader_llm.with_structured_output(
    CorrectnessGrade,
    method="json_schema",
    strict=True
)

correctness_instructions = """
You are a teacher grading a quiz.
You will be given a QUESTION, a REFERENCE ANSWER, and a STUDENT ANSWER.
Grade the student answer based only on factual accuracy relative to the reference answer.

True means the student answer is factually correct.
False means it contains an incorrect or conflicting statement.
Explain your reasoning briefly.
"""

def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    # SAFE EXTRACTION
    ref_answer = (reference_outputs or {}).get("ground_truth") or (reference_outputs or {}).get("answer", "")
    student_answer = (outputs or {}).get("answer", "") if isinstance(outputs, dict) else str(outputs)

    prompt = f"""
QUESTION:
{inputs.get("question", "")}

REFERENCE ANSWER:
{ref_answer}

STUDENT ANSWER:
{student_answer}
"""

    grade = correctness_llm.invoke([
        {"role": "system", "content": correctness_instructions},
        {"role": "user", "content": prompt}
    ])

    return grade["correct"]


# =========================
# Relevance Evaluator
# =========================

class RelevanceGrade(TypedDict):
    explanation: Annotated[str, "Explain your reasoning for the score"]
    correct: Annotated[bool, "True if the answer addresses the question"]

relevance_llm = grader_llm.with_structured_output(
    RelevanceGrade,
    method="json_schema",
    strict=True
)

relevance_instructions = """
You are grading a CEMK college assistant.
Check whether the STUDENT ANSWER directly and concisely addresses the QUESTION.

True means the answer is relevant.
False means the answer does not properly address the question.
Explain briefly.
"""

def relevance(inputs: dict, outputs: dict) -> bool:
    student_answer = (outputs or {}).get("answer", "") if isinstance(outputs, dict) else str(outputs)

    prompt = f"""
QUESTION:
{inputs.get("question", "")}

STUDENT ANSWER:
{student_answer}
"""

    grade = relevance_llm.invoke([
        {"role": "system", "content": relevance_instructions},
        {"role": "user", "content": prompt}
    ])

    return grade["correct"]


# =========================
# Groundedness Evaluator
# =========================

class GroundedGrade(TypedDict):
    explanation: Annotated[str, "Explain your reasoning"]
    grounded: Annotated[bool, "True if the answer is supported by the documents"]

grounded_llm = grader_llm.with_structured_output(
    GroundedGrade,
    method="json_schema",
    strict=True
)

grounded_instructions = """
You are evaluating a RAG answer.
Check whether the STUDENT ANSWER is completely supported by the provided FACTS.

True means the answer is grounded in the facts.
False means the answer contains unsupported or hallucinated information.
Explain briefly.
"""

def groundedness(inputs: dict, outputs: dict) -> bool:
    docs = outputs.get("documents", []) if isinstance(outputs, dict) else []
    doc_string = "\n\n".join(_extract_doc_text(doc) for doc in docs)
    student_answer = (outputs or {}).get("answer", "") if isinstance(outputs, dict) else str(outputs)

    prompt = f"""
FACTS:
{doc_string}

STUDENT ANSWER:
{student_answer}
"""

    grade = grounded_llm.invoke([
        {"role": "system", "content": grounded_instructions},
        {"role": "user", "content": prompt}
    ])

    return grade["grounded"]


# =========================
# Retrieval Relevance
# =========================

class RetrievalRelevanceGrade(TypedDict):
    explanation: Annotated[str, "Explain your reasoning"]
    relevant: Annotated[bool, "True if retrieved documents are relevant"]

retrieval_relevance_llm = grader_llm.with_structured_output(
    RetrievalRelevanceGrade,
    method="json_schema",
    strict=True
)

retrieval_relevance_instructions = """
You are evaluating retrieved documents for a RAG system.
Check whether the retrieved FACTS contain information relevant to the QUESTION.

True means the retrieved documents are relevant.
False means the documents are completely unrelated.
Explain briefly.
"""

def retrieval_relevance(inputs: dict, outputs: dict) -> bool:
    docs = outputs.get("documents", []) if isinstance(outputs, dict) else []
    doc_string = "\n\n".join(_extract_doc_text(doc) for doc in docs)

    prompt = f"""
QUESTION:
{inputs.get("question", "")}

FACTS:
{doc_string}
"""

    grade = retrieval_relevance_llm.invoke([
        {"role": "system", "content": retrieval_relevance_instructions},
        {"role": "user", "content": prompt}
    ])

    return grade["relevant"]


# =========================
# Target Function & Evaluation Run
# =========================

from generator import generate_answer

def target(inputs: dict) -> dict:
    return generate_answer(inputs["question"])

if __name__ == "__main__":
    dataset_name = "cemk-notices-evaluation"

    experiment_results = client.evaluate(
        target,
        data=dataset_name,
        evaluators=[
            correctness,
            relevance,
            groundedness,
            retrieval_relevance
        ],
        experiment_prefix="cemk-rag-eval-run-"
    )

    print(experiment_results)