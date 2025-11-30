# 4.2 Map Regions → Symptom Domains
region_to_symptom = {
    "Frontal Pole": ["executive function", "planning", "mood"],
    "Superior Frontal Gyrus": ["attention", "working memory"],
    "Anterior Cingulate Gyrus": ["emotional regulation", "motivation"],
    "Insular Cortex": ["interoception", "anxiety", "emotional salience"],
    # ...extend as needed
}

def add_symptom_domains(region_df):
    symptom_cols = []

    for _, row in region_df.iterrows():
        name = str(row["region_name"])
        # naive mapping: find any keys contained in the region name
        matched_symptoms = []
        for region_key, symptoms in region_to_symptom.items():
            if region_key.lower() in name.lower():
                matched_symptoms.extend(symptoms)

        symptom_cols.append(", ".join(sorted(set(matched_symptoms))) if matched_symptoms else "")

    region_df["symptom_domains"] = symptom_cols
    return region_df
