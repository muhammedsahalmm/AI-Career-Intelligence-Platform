import joblib

# Load trained model and preprocessing objects
model = joblib.load("models/resume_classifier.pkl")
tfidf = joblib.load("models/tfidf_vectorizer.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")


def predict_roles(cleaned_resume_text):
    """
    Predict the top 2 job roles and their confidence scores.
    """

    resume_vector = tfidf.transform([cleaned_resume_text])

    prediction_proba = model.predict_proba(resume_vector)[0]

    # Get top 2 predictions
    top_2_indices = prediction_proba.argsort()[-2:][::-1]

    top_2_roles = label_encoder.inverse_transform(top_2_indices)

    top_2_confidences = prediction_proba[top_2_indices] * 100

    return (
        resume_vector,
        top_2_roles,
        top_2_confidences
    )