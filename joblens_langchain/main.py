# ===================================
# MAIN — Entry Point
# ===================================

import logging
import os

from config import Config
from services.career_service import CareerService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def main():

    Config.validate()

    service = CareerService()

    # -------------------------------------------------
    # Debug existing payloads
    # -------------------------------------------------
    print("\n🔎 Existing payloads in Qdrant")
    service.vector.debug_payloads()

    # -------------------------------------------------
    # Sample Job Descriptions
    # -------------------------------------------------
    jds = [
        {
            "company": "Sarvam AI",
            "text": """
Backend Engineer to build low-latency APIs for ML models.
Strong Python, FastAPI, gRPC, PostgreSQL, Redis,
Docker, Kubernetes required.
AWS or GCP experience.
3-6 years experience.
"""
        },
        {
            "company": "Freshworks",
            "text": """
Data Analyst for product analytics team.
SQL, Python, Tableau or Power BI,
Excel, statistical analysis,
A/B testing.
2-4 years experience.
"""
        },
        {
            "company": "Haptik",
            "text": """
AI Engineer to build conversational AI products.
Python, NLP, LLMs,
LangChain,
Vector Databases,
RAG Systems,
FastAPI.
2-5 years experience.
"""
        }
    ]

    # -------------------------------------------------
    # Index Job Descriptions
    # -------------------------------------------------

    print("\n📥 Indexing Job Descriptions...\n")

    for jd in jds:

        result = service.index_jd(
            jd["text"],
            jd["company"]
        )

        print(
            f"{'✓' if result.success else '✗'} "
            f"{jd['company']} -> "
            f"{result.chunks_indexed} chunks"
        )

    # -------------------------------------------------
    # Index Resume
    # -------------------------------------------------

    resume_path = "data/sample.pdf"

    if os.path.exists(resume_path):

        print("\n📄 Indexing Resume...\n")

        result = service.index_resume(resume_path)

        print(
            f"{'✓' if result.success else '✗'} "
            f"Resume -> {result.chunks_indexed} chunks"
        )

    # -------------------------------------------------
    # Collection Statistics
    # -------------------------------------------------

    print("\n📊 Collection Statistics")
    print(service.collection_stats())

    # -------------------------------------------------
    # Show payloads AFTER indexing
    # -------------------------------------------------

    print("\n🔎 Payloads AFTER indexing")
    service.vector.debug_payloads()

    # -------------------------------------------------
    # Test Queries
    # -------------------------------------------------

    queries = [

        (
            "Sarvam AI",
            "What does this role require?"
        ),

        (
            "Freshworks",
            "What experience level does this need?"
        ),

        (
            "Haptik",
            "Does this role require RAG experience?"
        ),
    ]

    print("\n🔍 Running Queries...\n")

    for company, question in queries:

        print("=" * 70)
        print(f"Company : {company}")
        print(f"Question: {question}")
        print("-" * 70)

        try:

            result = service.ask_about_company(
                company,
                question
            )

            print("Answer:")
            print(result.answer)

            print("\nSources:")
            print(result.sources)

            print(f"\nChunks Used: {result.chunks_used}")

        except Exception as e:

            print(f"\n❌ Query Failed:\n{e}")

    print("\nFinished.")


if __name__ == "__main__":
    main()