from __future__ import annotations

import json
import pickle
from functools import lru_cache
from pathlib import Path

import joblib
import networkx as nx
import numpy as np
import pandas as pd
from loguru import logger
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.svm import LinearSVC
from statsmodels.tsa.arima.model import ARIMA


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

SALARY_VARIANCE_LOWER = 0.9
SALARY_VARIANCE_UPPER = 1.1


@lru_cache
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def save_metadata(name: str, metadata: dict) -> None:
    path = ARTIFACT_DIR / f"{name}_metadata.json"
    path.write_text(json.dumps(metadata, indent=2))


def train_stream_classifier(df: pd.DataFrame) -> dict:
    df = df.dropna(subset=["description", "stream"]).copy()
    if df.empty:
        return {"accuracy": 0, "report": {}}

    embedder = get_embedder()
    embeddings = embedder.encode(df["description"].tolist())

    encoder = LabelEncoder()
    labels = encoder.fit_transform(df["stream"].tolist())
    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, labels, test_size=0.2, random_state=42
    )

    classifier = LinearSVC()
    classifier.fit(X_train, y_train)
    accuracy = float(classifier.score(X_test, y_test))
    report = classification_report(y_test, classifier.predict(X_test), output_dict=True)

    joblib.dump(embedder, ARTIFACT_DIR / "stream_embedder.joblib")
    joblib.dump(classifier, ARTIFACT_DIR / "stream_classifier.joblib")
    joblib.dump(encoder, ARTIFACT_DIR / "stream_encoder.joblib")
    save_metadata(
        "stream_classifier",
        {"accuracy": accuracy, "model": "all-MiniLM-L6-v2", "classes": encoder.classes_.tolist()},
    )
    return {"accuracy": accuracy, "report": report}


def train_demand_forecaster(df: pd.DataFrame) -> dict:
    df = df.dropna(subset=["posted_at"]).copy()
    if df.empty:
        return {"mse": None, "forecast": {}}
    df["month"] = pd.to_datetime(df["posted_at"]).dt.to_period("M").astype(str)
    counts = df.groupby("month").size()
    values = counts.values
    if len(values) < 3:
        return {"mse": None, "forecast": {}}
    model = ARIMA(values, order=(1, 1, 1))
    fitted = model.fit()
    forecast = fitted.forecast(steps=3).tolist()
    joblib.dump(fitted, ARTIFACT_DIR / "demand_forecaster.joblib")
    save_metadata("demand_forecaster", {"forecast": forecast})
    return {"mse": float(fitted.mse), "forecast": forecast}


def train_salary_estimator(df: pd.DataFrame) -> dict:
    df = df.dropna(subset=["salary_min", "salary_max", "stream"]).copy()
    if df.empty:
        return {"mae": None}

    df["salary_mid"] = (df["salary_min"] + df["salary_max"]) / 2
    features = df[["stream", "location"]].fillna("unknown")
    encoder = OneHotEncoder(handle_unknown="ignore")
    X = encoder.fit_transform(features)
    y = df["salary_mid"].values

    model = GradientBoostingRegressor(random_state=42)
    model.fit(X, y)

    joblib.dump(model, ARTIFACT_DIR / "salary_estimator.joblib")
    joblib.dump(encoder, ARTIFACT_DIR / "salary_encoder.joblib")
    save_metadata("salary_estimator", {"rows": len(df)})
    return {"rows": len(df)}


def build_skill_graph(df: pd.DataFrame) -> dict:
    graph = nx.Graph()
    for skills_text in df["skills"].dropna().tolist():
        skills = [s.strip().lower() for s in skills_text.split(",") if s.strip()]
        for i, skill in enumerate(skills):
            for other in skills[i + 1 :]:
                if graph.has_edge(skill, other):
                    graph[skill][other]["weight"] += 1
                else:
                    graph.add_edge(skill, other, weight=1)
    with open(ARTIFACT_DIR / "skill_graph.gpickle", "wb") as handle:
        pickle.dump(graph, handle)
    save_metadata("skill_graph", {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges()})
    return {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges()}


def load_stream_models():
    embedder = joblib.load(ARTIFACT_DIR / "stream_embedder.joblib")
    classifier = joblib.load(ARTIFACT_DIR / "stream_classifier.joblib")
    encoder = joblib.load(ARTIFACT_DIR / "stream_encoder.joblib")
    return embedder, classifier, encoder


def predict_stream(description: str) -> tuple[str | None, float]:
    try:
        embedder, classifier, encoder = load_stream_models()
    except Exception as exc:
        logger.error(f"Stream model unavailable: {exc}")
        return None, 0.0
    embedding = embedder.encode([description])
    prediction = classifier.predict(embedding)[0]
    stream = encoder.inverse_transform([prediction])[0]
    return stream, 1.0


def estimate_salary(stream: str, location: str | None) -> tuple[float | None, float | None]:
    try:
        model = joblib.load(ARTIFACT_DIR / "salary_estimator.joblib")
        encoder = joblib.load(ARTIFACT_DIR / "salary_encoder.joblib")
    except Exception as exc:
        logger.error(f"Salary model unavailable: {exc}")
        return None, None

    features = pd.DataFrame([{"stream": stream, "location": location or "unknown"}])
    X = encoder.transform(features)
    estimate = float(model.predict(X)[0])
    return estimate * SALARY_VARIANCE_LOWER, estimate * SALARY_VARIANCE_UPPER
