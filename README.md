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
