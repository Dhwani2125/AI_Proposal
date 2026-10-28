"""Small illustrative supervised classifier; never generates proposal facts."""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

TRAINING = {
    "objective": ["Improve sales forecasting", "Understand customer behaviour", "Reduce manual reporting effort", "Identify data quality problems", "Predict customer churn", "The goal is better planning"],
    "deliverable": ["We need a report", "Deliver a model prototype", "Provide an analysis notebook", "Create a summary of findings", "We require a dashboard", "Hand over evaluation results"],
    "dependency": ["Client will provide the data", "Access to the database is needed", "We need labelled training data", "The team must supply content", "Approval depends on the project owner", "Data access is pending"],
    "timeline": ["Finish by December", "Target delivery is next month", "The deadline is Friday", "Start after approval", "Complete the milestone in June", "Schedule a review next week"],
    "question": ["Which platform should we use?", "Who approves the report?", "Is the dataset ready?", "The requirements are unclear", "We have not decided the format", "Confirm the acceptance criteria"],
    "context": ["The company sells products", "The team uses spreadsheets", "Current process is manual", "We have historical records", "There are several departments", "Existing reports are prepared monthly"],
}

def train_model():
    texts, labels = zip(*[(text, label) for label, rows in TRAINING.items() for text in rows])
    pipeline = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000))
    return pipeline.fit(texts, labels)

MODEL = train_model()
COMMERCIAL = re.compile(r"[$€£₹]|\b(?:price|pricing|cost|budget|rate|discount|tax|payment|currency|usd|inr|eur|gbp|dollars?|rupees?|free|fees?|total)\b", re.I)

def classify(notes):
    sentences = [s.strip() for s in re.split(r"[\n]+|(?<=[.!?])\s+", notes) if s.strip()]
    result = []
    for sentence in sentences:
        if COMMERCIAL.search(sentence):
            result.append({"text": "Commercial statement withheld; use the approved package pricing record.", "category": "commercial_unverified", "source": "discovery_note"})
        else:
            result.append({"text": sentence, "category": str(MODEL.predict([sentence])[0]), "source": "discovery_note"})
    return result
