# **ms_detection**
### **MS Detection & Symptom Mapping — Patient-Owned MRI Intelligence for Multiple Sclerosis**

This project is an open, modular pipeline designed to analyze a patient’s brain MRI and return two high-value outputs:

1. **Whether MS-like lesions are present**  
2. **Which cognitive, emotional, or physical symptom domains those lesions are most likely to affect**

The goal is **not diagnosis**.  
The goal is **patient-owned insight** — giving individuals clarity on their MRI scans over time while keeping a clinician in the loop.

The repository includes the full processing pipeline: *ingestion, harmonization, preprocessing, lesion detection, atlas overlap, symptom-domain mapping, and human-readable reporting.*

* Folder structure
```
README.TXT                    - This readme file
bussiness_modals              - PDF of 90 day implementation plan
data                          - Patient Data ( Dicom MRI ) 
images                        - images used in this readme file
libary                        - code for functionality
pitch_decks                   - varrious pitch decks (clincial, executive, general)
proposals                     - proposals ex Kettering Health
templates                     - General to compare to Patient Data  
```

![Image](https://github.com/user-attachments/assets/0cfa9579-a40f-4b83-b74f-3240223edc45)

---

## 🚀 **Core Idea**

MS patients often undergo years of MRI scans without clear explanations of:

- What changed  
- Why it matters  
- What symptoms to expect  

This tool fills that gap by providing:

- Longitudinal lesion tracking  
- Template-aligned, harmonized brain images  
- Region-based lesion interpretation  
- Symptom inference based on neuroscientific mapping  
- Simple, patient-readable summaries  

This is the foundation for a future **clinical-grade, one-click MRI intelligence engine**.

---

## 🧠 **Pipeline Overview**

A 6-stage neuroimaging + AI workflow:

---

### **1. Ingest & Harmonize**

- Converts DICOM → NIfTI  
- Standardizes voxel spacing and orientation  
- Ensures comparability across scanners  

**File:** `01_ingest_and_harmonize.py`

---

### **2. Preprocess & Register to MNI**

- N4 bias-field correction  
- Skull stripping / brain extraction  
- Registers to MNI152 template  
- Produces clean, normalized volumes for AI  

**Files:**  
`02_preprocess_and_register.py`  
Includes: **`MNI152_T1_1mm.nii.gz` templates**


---

### **3. AI Lesion Detection (Model Inference)**

- UNet / nnU-Net–style deep learning  
- Generates voxel-level lesion masks  
- Returns lesion presence, volume, and distribution  

**Files:**  
`03_train_lesion_model.py`  
`04_inference_and_longitudinal_report.py`

---

### **4. Longitudinal Lesion Tracking**

- Aggregates MRI results across dates  
- Computes lesion count, lesion load, and emergence of new lesions  
- Builds patient-level progression profiles  

Included in: `04_inference_and_longitudinal_report.py`

---

### **5. Symptom–Lesion Mapping**

Maps lesions → brain regions → symptom domains.

#### **Lesion–Atlas Overlap**
Intersects lesion masks with anatomical atlases.  
**File:** `4_1_loadAtlasAndComputeRegionOverlaps.py`

#### **Region → Symptom Mapping**
Maps affected regions to cognitive/emotional/motor functions.  
**File:** `4_2_mapRegionsToSymptomDomains.py`

**Example domains:**
- Executive function  
- Emotional regulation  
- Sensory processing  
- Motor coordination  
- Memory systems  

---

### **6. Human-Readable Summary**

Generates clinical-style interpretation:

Lesions Detected: Yes
Most likely affected domains:

Executive function

Emotional regulation

Sensory processing


**File:** `4_3_scanSummary.py`

---

## 🔥 **One-Function API (High-Level Entry Point)**

A single call runs the **entire pipeline**:

```python
from analyze_brain_for_symptoms_image import analyze_brain_for_symptoms

has_lesions, symptoms = analyze_brain_for_symptoms("example.nii.gz")

print("Lesions present:", has_lesions)
print("Likely symptoms:", symptoms)


Example Output:

Lesions present: True
Likely symptoms: ['executive dysfunction', 'emotional regulation challenges']
```

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
└── README.md
```

# 🧪 Demo Instructions

* To run a single-image analysis:

'''python analyze_brain_for_symptoms_image.py /path/to/your_mri.nii.gz'''


# Notes:
No GPU required for demonstrating the pipeline structure

## Lesion model can be:
* A real trained checkpoint
* A stub for demonstration / IP review

🏥 Clinical Vision
A future version of this tool supports:
Upload MRI (NIfTI or DICOM)
Auto-run lesion detection
Auto-map regions → symptoms
Auto-generate PDF summaries
Longitudinal tracking across years

Optional clinician review for safety

A clinical-grade version would include:

One-click PDF export
Time-series lesion progression
Symptom-domain probability mapping
Secure patient data handling (HIPAA-compliant)

🧩 Why This Matters

MS imaging is complex.
Patients deserve clarity.

This tool offers:

A sense of control

Explanations for symptoms

A way to track change over time

Better communication with clinicians

It is not diagnostic — it is empowerment through understanding.

📚 Future Work

Train/finetune models on public MS datasets

Expand symptom ontology

Add FLAIR + diffusion support

Build a web app wrapper

Integrate one-click PDF export

Deploy as fog/edge compute module for patient-owned devices

👤 Author

Ali Payne
Entrepreneur, engineer, and researcher exploring patient-centered neurotechnology.
```
Pipeline Diagram
          ┌───────────────────────────┐
          │  Patient-owned MRI data  │
          │   (DICOM from hospitals) │
          └───────────┬──────────────┘
                      │
                      ▼
     ┌───────────────────────────────────────┐
     │  1. Ingest & Harmonize               │
     │  - DICOM → NIfTI                     │
     │  - Standardize orientation/voxel size│
     └───────────────────┬──────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  2. Preprocess & Normalize                │
     │  - Bias correction (ANTs N4)              │
     │  - Brain extraction                       │
     │  - Register to MNI                        │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  3. AI Lesion Detection                    │
     │  - UNet / nnU-Net                          │
     │  - Output: voxelwise lesion masks          │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  4. Lesion Quantification & Longitudinal  │
     │  - Lesion count, volume, location         │
     │  - Time-series progression                │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  5. Symptom–Lesion Mapping                │
     │  - Atlas intersection                     │
     │  - Map regions → cognitive/emotional fxn  │
     │  - Generate likely symptom domains        │
     └───────────────────┬──────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────────┐
     │  6. Clinical Review & Reporting           │
     │  - Overlays + regional labels             │
     │  - Narrative summary                      │
     └───────────────────────────────────────────┘

# Single-Function Example
image_path = "/mnt/data/your_mri_image.nii.gz"

has_lesions, symptoms = analyze_brain_for_symptoms(image_path)

print("Lesions present:", has_lesions)
print("Likely symptoms:", symptoms)


# Example Output:

Lesions present: True
Likely symptoms: [
    "executive dysfunction",
    "emotional regulation issues",
    "anxiety-like symptoms",
    "interoceptive disturbance",
    "memory issues"
]

```
