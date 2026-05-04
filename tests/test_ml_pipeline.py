import numpy as np
import pandas as pd

from ml import pipeline


class DummyEmbedder:
    def encode(self, texts):
        return np.random.rand(len(texts), 8)


def test_train_stream_classifier(monkeypatch, tmp_path):
    df = pd.DataFrame(
        {
            "description": ["data analysis", "build APIs", "devops work", "data science"],
            "stream": ["Data", "Engineering", "DevOps", "Data"],
        }
    )

    monkeypatch.setattr(pipeline, "ARTIFACT_DIR", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pipeline, "SentenceTransformer", lambda *_: DummyEmbedder())

    result = pipeline.train_stream_classifier(df)
    assert result["accuracy"] >= 0


def test_build_skill_graph(tmp_path, monkeypatch):
    df = pd.DataFrame({"skills": ["python, sql", "python, aws", "sql, aws"]})
    monkeypatch.setattr(pipeline, "ARTIFACT_DIR", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    result = pipeline.build_skill_graph(df)
    assert result["nodes"] >= 2
