# analyze_brain_for_symptoms(image_path)

import nibabel as nib
import numpy as np
from nilearn import datasets, image

# ---------------------------
#  Load atlas once (global)  
# ---------------------------
ho_atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
atlas_img = ho_atlas.maps
atlas_labels = ho_atlas.labels

# ---------------------------
#  Symptom mapping dictionary
# ---------------------------
region_to_symptoms = {
    "frontal": ["executive dysfunction", "attention problems", "emotional regulation issues"],
    "cingulate": ["motivation issues", "emotional dysregulation", "conflict processing problems"],
    "insula": ["anxiety-like symptoms", "interoceptive disturbance", "stress intolerance"],
    "temporal": ["memory issues", "language difficulties"],
    "parietal": ["sensory issues", "spatial confusion"],
    "occipital": ["visual disturbances"],
    "cerebellum": ["balance issues", "coordination problems"],
}

# ---------------------------------------
#  Main One-Shot Function
# ---------------------------------------
def analyze_brain_for_symptoms(image_path, lesion_threshold=0.15):
    """
    Provide one MRI image → return (has_lesions, predicted_symptoms)

    image_path: path to a NIfTI file (.nii or .nii.gz)
    lesion_threshold: voxel intensity threshold for lesion detection (simple rule)
    """
    
    # ----------------------
    # Load MRI image
    # ----------------------
    img = nib.load(image_path)
    data = img.get_fdata()

    # ----------------------------------------------
    # STEP 1 — SIMPLE LESION DETECTION
    # (You can replace with real MS lesion model later)
    # ----------------------------------------------
    # Rule: lesions = bright voxels on FLAIR-like input
    voxels = data > (np.mean(data) + lesion_threshold * np.std(data))
    lesion_voxels = np.sum(voxels)

    if lesion_voxels < 50:  # very small → assume no lesion
        return False, []

    # -------------------------------
    # STEP 2 — Align atlas to image
    # -------------------------------
    if data.shape != atlas_img.shape:
        atlas_resampled = image.resample_to_img(atlas_img, img, interpolation="nearest")
        atlas_data = atlas_resampled.get_fdata()
    else:
        atlas_data = atlas_img.get_fdata()

    # ------------------------------------
    # STEP 3 — Compute region overlaps
    # ------------------------------------
    region_hits = []
    for idx, label in enumerate(atlas_labels):
        if idx == 0:  # background
            continue
        
        region_mask = (atlas_data == idx)
        overlap = np.logical_and(voxels, region_mask).sum()
        
        if overlap > 0:
            region_hits.append(label)

    # -----------------------------------
    # STEP 4 — Map regions → symptoms
    # -----------------------------------
    symptoms = []
    for region in region_hits:
        name_lower = region.lower()
        for key, sy in region_to_symptoms.items():
            if key in name_lower:
                symptoms.extend(sy)

    # Deduplicate symptoms
    symptoms = sorted(list(set(symptoms)))

    return True, symptoms
