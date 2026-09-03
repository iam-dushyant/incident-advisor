from __future__ import annotations
import argparse, json
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

def read_jsonl(path: Path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    text = [
        f"severity={row['severity']} service={row['service']} status_code={row['status_code']} message={row['message']}"
        for row in rows
    ]
    labels = [row["label"] for row in rows]
    return text, labels

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True, help="Path to training data in JSONL format")
    p.add_argument("--out", required=True, default="artifacts/model", help="Path to save the trained model")
    a = p.parse_args()

    X, y = read_jsonl(Path(a.data))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
           ngram_range=(1, 2),
           min_df=2,
           max_features=25000,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )),
    ])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    report = classification_report(y_test, pred, output_dict=True)
    print(classification_report(y_test, pred))

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out/"incident_classifier.joblib")
    (out/"metric.json").write_text(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()