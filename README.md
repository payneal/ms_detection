# ms_detection

MS Detection & Symptom Mapping (ms_detection)
Patient-Owned MRI Intelligence for Multiple Sclerosis

This project is an open, modular pipeline designed to analyze a patient’s brain MRI and return two high-value outputs:

Whether MS-like lesions are present, and

Which cognitive, emotional, or physical symptom domains those lesions are most likely to affect.

The goal is not diagnosis.
The goal is patient-owned insight — giving individuals a way to understand their MRI scans over time while keeping a clinician in the loop.

This repo contains the full technical pipeline: ingestion, harmonization, preprocessing, lesion detection, atlas overlap, symptom mapping, and human-friendly reporting.

🚀 Core Idea

MS patients often undergo years of MRI scans without clear explanations of what changed, why it matters, or what symptoms to expect.
This tool aims to fill that gap by providing:

Longitudinal lesion tracking

Template-aligned, harmonized brain images

Region-based lesion interpretation

Symptoms inferred from neuroscientific mapping

Simple, patient-readable summaries

This is the foundation for a future clinical-grade, one-click MRI intelligence engine.

🧠 Pipeline Overview

The codebase implements a 6-stage neuroimaging and AI workflow:

1. Ingest & Harmonize

Converts DICOM → NIfTI

Standardizes voxel spacing, orientation, and file structure

Ensures MRIs from different scanners are comparable

01_ingest_and_harmonize.py

2. Preprocess & Register to MNI

Bias-field correction

Skull stripping / brain extraction

Registers to a common template (MNI152)

Produces clean, normalized images for AI inference

02_preprocess_and_register.py
Includes MNI152_T1_1mm.nii.gz template.

3. AI Lesion Detection (Model Inference)

UNet/nnU-Net-style deep learning model

Outputs voxel-level lesion masks

Detects lesion presence, volume, and shape

03_train_lesion_model.py
04_inference_and_longitudinal_report.py

4. Longitudinal Lesion Tracking

Aggregates results across multiple MRI dates

Computes lesion count, volume change, and new lesion emergence

Produces patient-level progression summaries

Included within 04_inference_and_longitudinal_report.py.

5. Symptom–Lesion Mapping

Maps lesions to brain regions → symptom domains:

Lesion–Atlas Overlap
4_1_loadAtlasAndComputeRegionOverlaps.py
Intersects lesion masks with anatomical atlases.

Region → Symptom Mapping
4_2_mapRegionsToSymptomDomains.py
Maps affected regions to cognitive/emotional/motor functions.

Example domains:

Executive function

Emotional regulation

Sensory processing

Motor coordination

Memory systems

6. Human-Readable Summary

4_3_scanSummary.py
Generates simple clinical-style text:

Lesions Detected: Yes  
Most likely affected domains:
- Executive function
- Emotional regulation
- Sensory processing

🔥 One-Function API (High-Level Entry Point)

A single call handles the entire pipeline:

from analyze_brain_for_symptoms_image import analyze_brain_for_symptoms

has_lesions, symptoms = analyze_brain_for_symptoms("example.nii.gz")

print("Lesions present:", has_lesions)
print("Likely symptoms:", symptoms)


Example output:

Lesions present: True
Likely symptoms: ['executive dysfunction', 'emotional regulation challenges']

```
📁 Repo Structure
ms_detection/
│── 01_ingest_and_harmonize.py
│── 02_preprocess_and_register.py
│── 03_train_lesion_model.py
│── 04_inference_and_longitudinal_report.py
│── 4_1_loadAtlasAndComputeRegionOverlaps.py
│── 4_2_mapRegionsToSymptomDomains.py
│── 4_3_scanSummary.py
│── analyze_brain_for_symptoms_image.py
│── MNI152_T1_1mm.nii.gz
│── data/
└── README.md   (this file)
```

🧪 Demo Instructions

If you want a simple test-drive:

python analyze_brain_for_symptoms_image.py /path/to/your_mri.nii.gz


No GPU required for the pipeline structure to run.
Lesion model can be replaced with:

A real trained checkpoint, or

A stub for demonstration/ip review.

🏥 Clinical Vision

This project supports a future product with:

Upload MRI (.nii.gz or DICOM)

Auto-run lesion detection

Auto-map to symptoms

Auto-generate a PDF summary

Longitudinal tracking for home use

Clinician review layer for safety

A “clinical version” would offer:

One-click PDF export

Time-series lesion progression

Symptom domain probability scores

Secure patient data handling (HIPAA compliant)

🧩 Why This Matters

MS imaging is complex.
Patients deserve clarity.

This tool gives individuals:

A sense of control

An explanation of why they feel what they feel

A way to track changes over time

A tool to better communicate with their clinicians

It is not diagnostic.
It is empowerment through understanding.

📚 Future Work

Train/finetune models on public MS datasets

Expand symptom ontology

Add diffusion & FLAIR support

Build a web app wrapper

Integrate one-click PDF export

Deploy as lightweight edge/fog module for patient-owned compute

👤 Author

Built by Ali Payne
Entrepreneur, engineer, and researcher exploring patient-centered neurotechnology.



# diagram 
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





# single function 
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




