
# 4.3 Generate a Scan-Level Summary

def summarize_scan_symptoms(lesion_mask_path, scan_date):
    regions = lesion_region_overlap(lesion_mask_path, atlas_img, atlas_labels)
    regions = add_symptom_domains(regions)

    # focus on top N contributors
    top = regions.head(5)

    # Build a short narrative string
    bullets = []
    for _, row in top.iterrows():
        if not row["symptom_domains"]:
            continue
        bullets.append(
            f"- {row['region_name']} (~{row['percent_lesion_volume']:.1f}% of lesion volume): "
            f"associated with {row['symptom_domains']}."
        )

    narrative = f"Scan {scan_date}: AI-detected lesions involve:\n" + "\n".join(bullets)
    return top, narrative

# Example usage:
# top_regions_df, narrative_text = summarize_scan_symptoms("/data/lesion_masks/patientX_2017.nii.gz", "2017-03-15")
# print(narrative_text)
