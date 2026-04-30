import pandas as pd
from difflib import SequenceMatcher

# Load disease database
try:
    df = pd.read_csv("data/diseases.csv", encoding='utf-8', on_bad_lines='skip')
    print(f"Loaded {len(df)} disease entries")
except Exception as e:
    print(f"Error loading CSV: {e}")
    # Fallback data if CSV fails
    df = pd.DataFrame({
        "Disease": [
            "Cassava Mosaic Disease",
            "Yam Anthracnose",
            "Bacterial Wilt"
        ],
        "Symptoms": [
            "yellow leaves mosaic pattern stunted growth",
            "black spots leaf blight stem dieback",
            "wilting yellowing soft rot"
        ],
        "Treatment": [
            "Use resistant varieties and remove infected plants",
            "Apply fungicide and improve field sanitation",
            "Remove infected plants and avoid waterlogging"
        ]
    })

def similarity(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def diagnose(symptoms):
    """
    Diagnose disease based on symptoms.
    Matches symptom keywords against the disease database.
    """
    if not symptoms or not isinstance(symptoms, str):
        return {
            "disease": "No symptoms provided",
            "treatment": "Please describe the symptoms you observe on the crop."
        }

    symptoms_lower = symptoms.lower().strip()
    keyword_list = [word.strip() for word in symptoms_lower.split() if len(word.strip()) > 2]

    if not keyword_list:
        return {
            "disease": "Invalid symptoms",
            "treatment": "Please provide more detailed symptoms description."
        }

    best_match = None
    best_score = 0

    for index, row in df.iterrows():
        try:
            disease_symptoms = str(row["Symptoms"]).lower().split()

            # Count keyword matches
            matches = sum(1 for keyword in keyword_list if any(keyword in symptom or symptom in keyword for symptom in disease_symptoms))

            # Calculate match score
            if len(keyword_list) > 0:
                score = matches / len(keyword_list)
            else:
                score = 0

            # Check for direct substring matches (higher priority)
            for symptom in disease_symptoms:
                for keyword in keyword_list:
                    if symptom in keyword or keyword in symptom:
                        score = max(score, 0.8)

            if score > best_score:
                best_score = score
                best_match = index
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue

    # If a reasonably good match found (>0.3), return it
    if best_match is not None and best_score >= 0.3:
        try:
            disease = df.iloc[best_match]["Disease"]
            treatment = df.iloc[best_match]["Treatment"]
            return {
                "disease": disease,
                "treatment": treatment
            }
        except Exception as e:
            print(f"Error accessing best match: {e}")

    # Fallback response
    return {
        "disease": "Disease Not Identified",
        "treatment": "Please consult with an agricultural extension officer or provide more detailed symptoms. Common symptoms include: yellowing, spots, wilting, leaf damage, root problems, or overall stunted growth."
    }
