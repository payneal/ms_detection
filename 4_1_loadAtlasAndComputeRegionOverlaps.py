# 4.1 Load an Atlas and Compute Region Overlaps
from nilearn import image, datasets, masking
import numpy as np
import pandas as pd
import nibabel as nib

# Example: Harvard–Oxford cortical atlas
ho_atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
atlas_img = ho_atlas.maps          # 3D label image in MNI space
atlas_labels = ho_atlas.labels     # list of region names (index = label)

def lesion_region_overlap(lesion_mask_path, atlas_img, atlas_labels):
    lesion_img = nib.load(lesion_mask_path)

    # Ensure same space/shape – you may need resampling in a real pipeline
    # (skipped here for brevity, but nilearn.image.resample_to_img is your friend)
    lesion_data = lesion_img.get_fdata()
    atlas_data = atlas_img.get_fdata()

    lesion_voxels = lesion_data > 0.5
    total_lesion_voxels = lesion_voxels.sum()

    region_stats = []

    for label_idx, label_name in enumerate(atlas_labels):
        if label_idx == 0:
            continue  # 0 is usually background

        region_mask = atlas_data == label_idx
        overlap_voxels = np.logical_and(lesion_voxels, region_mask).sum()

        if overlap_voxels > 0:
            pct_lesion = overlap_voxels / total_lesion_voxels * 100.0
            region_stats.append({
                "region_label": int(label_idx),
                "region_name": label_name,
                "overlap_voxels": int(overlap_voxels),
                "percent_lesion_volume": pct_lesion,
            })

    # sort descending by contribution
    region_stats = sorted(region_stats, key=lambda r: r["percent_lesion_volume"], reverse=True)
    return pd.DataFrame(region_stats)
