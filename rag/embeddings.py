import math
import re
from typing import List, Dict, Any

KNOWLEDGE_DOCUMENTS = [
    {
        "id": "doc1",
        "title": "Operating Systems Syllabus & Exam Strategy",
        "category": "Syllabus",
        "content": "Operating Systems (CS501) covers Process Synchronization, Deadlocks, CPU Scheduling, Virtual Memory, and File Systems. Deadlocks and Bankers Algorithm historically account for 20% of exam marks. Students struggling with OS should prioritize Deadlock avoidance problems and Shortest Job First / SRTF Gantt chart scheduling."
    },
    {
        "id": "doc2",
        "title": "DBMS Normalization & Relational Algebra",
        "category": "Syllabus",
        "content": "Database Management Systems (CS503) focuses heavily on Normalization (1NF, 2NF, 3NF, BCNF) and SQL query optimization. Functional dependencies and 3NF/BCNF decomposition carry high historical examination weight (Importance Score: 92/100). Remedial focus should be placed on candidate key identification and lossless join properties."
    },
    {
        "id": "doc3",
        "title": "Machine Learning Core Concepts & Algorithmic Foundations",
        "category": "Syllabus",
        "content": "Machine Learning (CS502) requires mathematical understanding of Decision Trees, Impurity measures (Gini vs Entropy), Linear Regression gradient descent, and Backpropagation in Neural Networks. Practicing derivation of Gini index and decision boundary visualization significantly boosts assessment scores."
    },
    {
        "id": "doc4",
        "title": "Academic Risk Reduction & Intervention Guidelines",
        "category": "Advising",
        "content": "To reduce dropout risk level from HIGH to MEDIUM/LOW: 1. Maintain attendance above 75%. 2. Clear pending backlogs by focusing on weak unit topics identified in study planner. 3. Complete all lab assignments on time. 4. Devote at least 12-15 study hours weekly using the EduGuard Adaptive Study Planner."
    },
    {
        "id": "doc5",
        "title": "Exam Preparation & Time Management Strategies",
        "category": "Strategy",
        "content": "High-priority study tasks are determined by combining student topic weakness with historical exam question importance scores. High-risk students are advised to allocate 90-minute daily blocks to top-weighted weak topics before reviewing general coursework."
    }
]

def tokenize(text: str) -> List[str]:
    """Simple regex tokenizer for TF-IDF / keyword matching."""
    return re.findall(r'\w+', text.lower())

def search_documents(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    Search knowledge documents using lightweight TF-IDF / keyword similarity matching.
    Provides fast, reliable offline vector-style document retrieval without API dependencies.
    """
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return KNOWLEDGE_DOCUMENTS[:top_k]

    scored_docs = []
    for doc in KNOWLEDGE_DOCUMENTS:
        doc_tokens = tokenize(doc["content"] + " " + doc["title"])
        # Match count
        matches = sum(1 for t in q_tokens if t in doc_tokens)
        score = matches / (len(q_tokens) + 1e-5)
        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [d[1] for d in scored_docs[:top_k]]
