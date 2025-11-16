"""
Text Classification Example

This example demonstrates various approaches to text classification:
- Traditional ML with scikit-learn
- Using pre-trained transformers
- LLM-based classification
"""

import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()


def sklearn_classification():
    """Traditional text classification using scikit-learn"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    print("Scikit-learn Text Classification")
    print("="*50)

    # Sample dataset
    texts = [
        "I love this product, it's amazing!",
        "Terrible experience, waste of money",
        "Best purchase ever, highly recommend",
        "Very disappointed, poor quality",
        "Absolutely fantastic, exceeded expectations",
        "Worst service I've ever had",
        "Great value for money",
        "Complete disaster, avoid at all costs",
        "Wonderful experience, will buy again",
        "Not satisfied, requested refund",
    ]

    labels = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # 1 = positive, 0 = negative

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.3, random_state=42
    )

    # Create TF-IDF features
    vectorizer = TfidfVectorizer(max_features=100)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train classifier
    classifier = MultinomialNB()
    classifier.fit(X_train_vec, y_train)

    # Predict
    y_pred = classifier.predict(X_test_vec)

    # Evaluate
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.2f}")

    # Test with new examples
    new_texts = [
        "This is awesome!",
        "I hate this product"
    ]

    new_vec = vectorizer.transform(new_texts)
    predictions = classifier.predict(new_vec)

    print("\nPredictions on new texts:")
    for text, pred in zip(new_texts, predictions):
        sentiment = "Positive" if pred == 1 else "Negative"
        print(f"  '{text}' -> {sentiment}")

    print("\n" + "="*50 + "\n")


def transformer_classification():
    """Text classification using pre-trained transformers"""
    from transformers import pipeline

    print("Transformer-based Classification")
    print("="*50)

    # Load sentiment analysis pipeline
    classifier = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    texts = [
        "I absolutely love this!",
        "This is terrible.",
        "It's okay, nothing special.",
        "Best thing ever!",
        "Worst experience of my life."
    ]

    print("\nClassifying texts with DistilBERT:\n")

    results = classifier(texts)

    for text, result in zip(texts, results):
        print(f"Text: '{text}'")
        print(f"  Label: {result['label']}")
        print(f"  Confidence: {result['score']:.4f}\n")

    print("="*50 + "\n")


def llm_classification():
    """Text classification using LLMs (zero-shot)"""
    from anthropic import Anthropic

    print("LLM-based Zero-Shot Classification")
    print("="*50)

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    texts = [
        "The movie was fantastic with great acting",
        "I'm feeling really happy today",
        "Breaking news: Major earthquake hits city",
        "Check out our 50% off sale this weekend!",
        "Python is a versatile programming language"
    ]

    categories = ["Entertainment", "Personal", "News", "Marketing", "Technology"]

    print(f"\nClassifying texts into: {', '.join(categories)}\n")

    for text in texts:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Classify this text into ONE of these categories: {', '.join(categories)}

Text: "{text}"

Return only the category name, nothing else."""
            }]
        )

        category = message.content[0].text.strip()
        print(f"'{text}'")
        print(f"  -> {category}\n")

    print("="*50 + "\n")


def multi_label_classification():
    """Multi-label classification using transformers"""
    from transformers import pipeline

    print("Multi-Label Classification")
    print("="*50)

    # Zero-shot classification pipeline
    classifier = pipeline("zero-shot-classification")

    texts = [
        "This smartphone has an amazing camera and long battery life",
        "The restaurant serves delicious Italian and Mediterranean cuisine",
        "Climate change and renewable energy are critical topics"
    ]

    candidate_labels = [
        ["technology", "photography", "mobile"],
        ["food", "italian", "mediterranean", "dining"],
        ["environment", "energy", "politics", "science"]
    ]

    print("\nMulti-label classification:\n")

    for text, labels in zip(texts, candidate_labels):
        result = classifier(text, labels, multi_label=True)

        print(f"Text: '{text}'")
        print("Labels and scores:")
        for label, score in zip(result['labels'], result['scores']):
            if score > 0.3:  # Only show confident predictions
                print(f"  - {label}: {score:.3f}")
        print()

    print("="*50 + "\n")


def main():
    """Run all classification examples"""
    try:
        sklearn_classification()
        transformer_classification()

        # LLM examples require API key
        try:
            llm_classification()
        except Exception as e:
            print(f"LLM classification skipped: {e}")
            print("Set ANTHROPIC_API_KEY in .env to run this example\n")

        multi_label_classification()

    except Exception as e:
        print(f"Error: {e}")
        print("\nSome dependencies may be missing. Install with:")
        print("pip install scikit-learn transformers torch")


if __name__ == "__main__":
    main()
