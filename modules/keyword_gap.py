from modules.resume_parser import clean_resume
from modules.predictor import tfidf


def extract_jd_keywords(jd_text, resume_text, top_n=15):
    """
    Extract matched and missing keywords from the Job Description
    using the trained TF-IDF vocabulary.
    """

    cleaned_jd_text = clean_resume(jd_text)
    cleaned_resume_text = clean_resume(resume_text)

    jd_vector = tfidf.transform([cleaned_jd_text])

    feature_names = tfidf.get_feature_names_out()

    scores = jd_vector.toarray()[0]

    top_indices = scores.argsort()[::-1]

    jd_keywords = []

    # Generic words to ignore
    generic_words = {
        "resume", "work", "experience", "year", "years",
        "team", "role", "job", "candidate", "ability",
        "responsibility", "responsibilities", "required",
        "requirement", "requirements", "skills", "skill",
        "knowledge", "good", "strong", "excellent",
        "must", "should", "preferred", "looking",
        "include", "including", "based", "using",
        "company", "organization", "client", "project"
    }

    for index in top_indices:

        if scores[index] <= 0:
            continue

        keyword = feature_names[index]

        if keyword not in generic_words and len(keyword) > 2:
            jd_keywords.append(keyword)

        if len(jd_keywords) == top_n:
            break

    matched_keywords = []
    missing_keywords = []

    resume_words = f" {cleaned_resume_text} "

    for keyword in jd_keywords:

        if f" {keyword} " in resume_words:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    return matched_keywords, missing_keywords