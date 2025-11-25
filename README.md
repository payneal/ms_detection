# ms_detection

          ┌───────────────────────────┐
          │  Patient-owned MRI data  │
          │   (DICOM from Kettering  │
          │    & outside facilities) │
          └───────────┬──────────────┘
                      │
                      ▼
     ┌───────────────────────────────────────┐
     │  1. Ingest & Harmonize               │
     │  - DICOM → NIfTI (SimpleITK/NiBabel) │
     │  - Standardize orientation/voxel size│
     └───────────────────┬──────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  2. Preprocess & Normalize                │
     │  - Bias correction (ANTs N4)              │
     │  - Brain extraction (FSL/ANTs)            │
     │  - Register to MNI (ANTs)                 │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  3. AI Lesion Detection                    │
     │  - MONAI / UNet / nnU-Net                  │
     │  - Output: voxelwise lesion masks          │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  4. Lesion Quantification & Longitudinal  │
     │  - Lesion count, volume, location         │
     │  - Time series vs diagnosis               │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  5. Symptom–Lesion Mapping (NEW)         │
     │  - Intersect lesions with brain atlases   │
     │  - Map regions → cognitive/emotional fxn  │
     │  - Generate “likely symptom domains”      │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  6. Clinical Review & Reporting           │
     │  - Overlays + regional labels             │
     │  - Narrative: “lesions here ↔ these sx”   │
     │  - Exec/grant-ready summary               │
     └───────────────────────────────────────────┘






```
image_path = "/mnt/data/your_mri_image.nii.gz"

has_lesions, symptoms = analyze_brain_for_symptoms(image_path)

print("Lesions present:", has_lesions)
print("Likely symptoms:", symptoms)
```

```
Example Output
Lesions present: True
Likely symptoms: [
    'executive dysfunction',
    'emotional regulation issues',
    'anxiety-like symptoms',
    'interoceptive disturbance',
    'memory issues'
]
```




