# ===================================
# EVALUATION DATASET
# Ground truth questions — built once, reused forever
# Every time you change the RAG pipeline, re-run this dataset
# ===================================

EVAL_DATASET = [

    # -------------------------------------------------------
    # Factual retrieval — clear, specific answer in the JD
    # These should ALWAYS be answerable if retrieval works
    # -------------------------------------------------------
    {
        "id": "eval_001",
        "question": "What Python frameworks does the Sarvam AI role require?",
        "relevant_source": "Sarvam AI JD",
        "relevant_chunk_keywords": ["FastAPI", "Python"],
        "expected_answer_contains": ["FastAPI"],
        "category": "factual_retrieval"
    },
    {
        "id": "eval_002",
        "question": "How many years of experience does the Sarvam AI role need?",
        "relevant_source": "Sarvam AI JD",
        "relevant_chunk_keywords": ["3", "years"],
        "expected_answer_contains": ["3"],
        "category": "factual_retrieval"
    },
    {
        "id": "eval_003",
        "question": "What database tools does the Razorpay Data Engineer role require?",
        "relevant_source": "Razorpay JD",
        "relevant_chunk_keywords": ["Snowflake", "SQL"],
        "expected_answer_contains": ["Snowflake", "SQL"],
        "category": "factual_retrieval"
    },
    {
        "id": "eval_004",
        "question": "Does the Haptik role require RAG experience?",
        "relevant_source": "Haptik JD",
        "relevant_chunk_keywords": ["RAG"],
        "expected_answer_contains": ["RAG"],
        "category": "factual_retrieval"
    },
    {
        "id": "eval_005",
        "question": "What workflow tool does the Razorpay role mention?",
        "relevant_source": "Razorpay JD",
        "relevant_chunk_keywords": ["Airflow", "dbt"],
        "expected_answer_contains": ["Airflow"],
        "category": "factual_retrieval"
    },

    # -------------------------------------------------------
    # Grounding check — these answers should NOT exist in docs
    # System must say "I don't have enough information"
    # If it answers confidently, it's hallucinating
    # -------------------------------------------------------
    {
        "id": "eval_006",
        "question": "What is the salary for the Sarvam AI role?",
        "relevant_source": "Sarvam AI JD",
        "relevant_chunk_keywords": [],
        "expected_answer_contains": [],
        "expected_to_be_unanswerable": True,
        "category": "grounding_check"
    },
    {
        "id": "eval_007",
        "question": "Does Freshworks offer health insurance?",
        "relevant_source": "Freshworks JD",
        "relevant_chunk_keywords": [],
        "expected_answer_contains": [],
        "expected_to_be_unanswerable": True,
        "category": "grounding_check"
    },

    # -------------------------------------------------------
    # Resume questions — answers in your resume, not JDs
    # Tests that resume chunks are indexed and retrievable
    # -------------------------------------------------------
    {
        "id": "eval_008",
        "question": "What BI tools has the candidate used?",
        "relevant_source": "My Resume",
        "relevant_chunk_keywords": ["Qlik", "Power BI", "Tableau"],
        "expected_answer_contains": ["Qlik"],
        "category": "resume_retrieval"
    },
    {
        "id": "eval_009",
        "question": "What cloud platforms has the candidate worked with?",
        "relevant_source": "My Resume",
        "relevant_chunk_keywords": ["AWS", "Snowflake"],
        "expected_answer_contains": ["AWS"],
        "category": "resume_retrieval"
    },
# -------------------------------------------------------
    # HARD NEGATIVES
    # Questions that sound like they should be answerable
    # but the specific answer is NOT in any document
    # These test whether grounding holds under pressure
    # -------------------------------------------------------
    {
        "id": "eval_010",
        "question": "Does the Sarvam AI role require Django experience?",
        "relevant_source": "Sarvam AI JD",
        "relevant_chunk_keywords": [],
        "expected_answer_contains": [],
        "expected_to_be_unanswerable": True,
        "category": "hard_negative",
        "note": "Django is not mentioned — only FastAPI is. Should not hallucinate Django."
    },
    {
        "id": "eval_011",
        "question": "What is the notice period for the Freshworks Data Analyst role?",
        "relevant_source": "Freshworks JD",
        "relevant_chunk_keywords": [],
        "expected_answer_contains": [],
        "expected_to_be_unanswerable": True,
        "category": "hard_negative",
        "note": "Notice period never mentioned in the JD."
    },
    {
        "id": "eval_012",
        "question": "Does the Razorpay role require Kubernetes?",
        "relevant_source": "Razorpay JD",
        "relevant_chunk_keywords": [],
        "expected_answer_contains": [],
        "expected_to_be_unanswerable": True,
        "category": "hard_negative",
        "note": "Kubernetes is in Sarvam AI JD, not Razorpay. Tests cross-contamination."
    },
    {
        "id": "eval_013",
        "question": "How many Qlik Sense applications has the candidate built?",
        "relevant_source": "My Resume",
        "relevant_chunk_keywords": ["Qlik"],
        "expected_answer_contains": ["2", "two"],
        "category": "resume_retrieval",
        "note": "Specific number — tests whether resume chunks contain enough detail."
    },
]