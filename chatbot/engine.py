"""
NAUB Chatbot Matching Engine
Uses TF-IDF Vectorization + Cosine Similarity for intent matching.
This is a retrieval-based (rule-based) approach — no ML training involved.
"""

import json
import os
import re
import math
from collections import Counter

# ──────────────────────────────────────────────
# STEP 1: Text Pre-processing
# ──────────────────────────────────────────────

STOP_WORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "not", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall",
    "can", "i", "my", "me", "we", "you", "your", "he", "she", "they",
    "their", "his", "her", "this", "that", "what", "how", "when",
    "where", "who", "which", "about", "with", "from", "into", "by"
}

# Simple stemming rules (suffix stripping)
STEM_SUFFIXES = ["ing", "tion", "ment", "ness", "ies", "ed", "ly", "er", "s"]


def stem(word):
    """Reduce word to approximate root form using suffix stripping."""
    for suffix in STEM_SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def preprocess(text):
    """
    Clean and normalize text:
    1. Lowercase
    2. Remove punctuation
    3. Tokenize (split into words)
    4. Remove stop words
    5. Stem each token
    Returns a list of processed tokens.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)   # remove punctuation
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]
    tokens = [stem(t) for t in tokens]
    return tokens


# ──────────────────────────────────────────────
# STEP 2: TF-IDF Vectorization
# ──────────────────────────────────────────────

def compute_tf(tokens):
    """
    Term Frequency: count of term t in document / total terms in document.
    Returns a dict {term: tf_score}.
    """
    if not tokens:
        return {}
    count = Counter(tokens)
    total = len(tokens)
    return {term: freq / total for term, freq in count.items()}


def compute_idf(all_documents):
    """
    Inverse Document Frequency: log(N / df(t))
    N = total documents, df(t) = documents containing term t.
    Returns a dict {term: idf_score}.
    """
    N = len(all_documents)
    df = Counter()
    for doc in all_documents:
        unique_terms = set(doc)
        for term in unique_terms:
            df[term] += 1
    idf = {}
    for term, count in df.items():
        idf[term] = math.log(N / count)
    return idf


def compute_tfidf_vector(tokens, idf):
    """
    Combine TF and IDF to produce a weighted vector for a document.
    Returns a dict {term: tfidf_weight}.
    """
    tf = compute_tf(tokens)
    vector = {}
    for term, tf_score in tf.items():
        if term in idf:
            vector[term] = tf_score * idf[term]
    return vector


# ──────────────────────────────────────────────
# STEP 3: Cosine Similarity
# ──────────────────────────────────────────────

def cosine_similarity(vec_a, vec_b):
    """
    Cosine Similarity = (A · B) / (||A|| × ||B||)
    Measures angular similarity between two TF-IDF vectors.
    Returns a float between 0 (no match) and 1 (perfect match).
    """
    # Dot product: sum of products of shared terms
    dot_product = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in vec_b)

    # Magnitudes (Euclidean norms)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (mag_a * mag_b)


# ──────────────────────────────────────────────
# STEP 4: ChatbotEngine — loads KB and matches queries
# ──────────────────────────────────────────────

class ChatbotEngine:
    """
    Core NAUB chatbot engine.
    Loads the knowledge base and matches user queries using TF-IDF + Cosine Similarity.
    """

    SIMILARITY_THRESHOLD = 0.15  # minimum score to accept a match

    def __init__(self, knowledge_base_path=None):
        if knowledge_base_path is None:
            # Default path: knowledge_base/faqs.json relative to this file's parent
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            knowledge_base_path = os.path.join(base_dir, "knowledge_base", "faqs.json")

        self.intents = self._load_knowledge_base(knowledge_base_path)
        self.fallback_response = self._get_fallback()
        self._build_index()

    def _load_knowledge_base(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_fallback(self):
        for intent in self.intents:
            if intent["intent"] == "fallback":
                return intent["response"]
        return "I'm sorry, I could not understand your question. Please try rephrasing."

    def _build_index(self):
        """
        Pre-compute TF-IDF vectors for all intent patterns.
        This runs once at startup, making query-time matching very fast.
        """
        # Collect all tokenized pattern documents (exclude fallback)
        self.intent_docs = []  # list of (intent_id, response, tokens)

        for intent in self.intents:
            if intent["intent"] == "fallback":
                continue
            for pattern in intent["patterns"]:
                tokens = preprocess(pattern)
                self.intent_docs.append({
                    "intent": intent["intent"],
                    "response": intent["response"],
                    "tokens": tokens
                })

        # Compute IDF across all pattern documents
        all_token_lists = [doc["tokens"] for doc in self.intent_docs]
        self.idf = compute_idf(all_token_lists)

        # Pre-compute TF-IDF vectors for each pattern document
        for doc in self.intent_docs:
            doc["vector"] = compute_tfidf_vector(doc["tokens"], self.idf)

    def get_response(self, user_query):
        """
        Main method: takes user query string, returns chatbot response string.

        Steps:
        1. Pre-process the query
        2. Compute TF-IDF vector for the query
        3. Compute Cosine Similarity against all intent pattern vectors
        4. Return the response of the best-matching intent if above threshold
        5. Otherwise return the fallback response
        """
        query_tokens = preprocess(user_query)

        if not query_tokens:
            return (self.fallback_response, "fallback", 0.0)

        query_vector = compute_tfidf_vector(query_tokens, self.idf)

        # Compute similarity with every intent pattern
        best_score = 0.0
        best_response = None
        best_intent = None

        for doc in self.intent_docs:
            score = cosine_similarity(query_vector, doc["vector"])
            if score > best_score:
                best_score = score
                best_response = doc["response"]
                best_intent = doc["intent"]

        if best_score >= self.SIMILARITY_THRESHOLD:
            return (best_response, best_intent, round(best_score, 4))

        return (self.fallback_response, "fallback", 0.0)


# ──────────────────────────────────────────────
# Quick test (run this file directly to verify)
# ──────────────────────────────────────────────

if __name__ == "__main__":
    engine = ChatbotEngine()
    test_queries = [
        "How do I apply for admission at NAUB?",
        "What is the JAMB cut off mark?",
        "How much are the school fees?",
        "Where is the library?",
        "I want to change my course",
        "What programmes does NAUB offer?",
        "Can I get a hostel room?",
        "Hello",
        "How do I verify my result?",
        "What is 2 + 2?",   # fallback test
    ]

    print("=" * 60)
    print("NAUB Chatbot Engine — Test Run")
    print("=" * 60)
    for query in test_queries:
        response, intent, score = engine.get_response(query)
        print(f"\nQuery  : {query}")
        print(f"Intent : {intent}  (score: {score})")
        print(f"Response: {response[:100]}...")
    print("\n" + "=" * 60)
