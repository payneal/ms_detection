import os
import pathlib
import pandas as pd
import numpy as np
from PIL import Image
import nibabel as nib
from libary.util.medicalFormatChanger import MedicalFormatChanger

class MSDection:
    def __init__(self, dicom_path, nifti_output_path, image_output_path):
        self.dicom_path = dicom_path
        self.nifti_output_path = nifti_output_path
        self.image_output_path = image_output_path
        self.medicalChanger = MedicalFormatChanger()

    def detect(self, data):
        # Placeholder for multi-scale detection logic

        print("Performing multi-scale detection...")
        return {"detections": []}
    
    def ingest_and_harmonize(self):
       
        RAW_DICOM_ROOT = pathlib.Path(self.dicom_path)
        NIFTI_ROOT = pathlib.Path(self.nifti_output_path)

        NIFTI_ROOT.mkdir(parents=True, exist_ok=True)

        records = []

        for patient_dir in RAW_DICOM_ROOT.iterdir():
            if not patient_dir.is_dir():
                continue
            patient_id = patient_dir.name

            for date_dir in patient_dir.iterdir():
                # print("Processing date directory:", date_dir)
                if not date_dir.is_dir():
                    continue    
                date_str = date_dir.name 
            
            
                for series_dir in date_dir.iterdir():
                    if not series_dir.is_dir():
                        continue
                    series_str = series_dir.name    

                    for subseries_dir in series_dir.iterdir():
                        if not subseries_dir.is_dir():
                            continue
                 
                        out_file = NIFTI_ROOT / f"{patient_id}_{date_str}_{series_str}_{subseries_dir.name}.nii.gz"
                        try:
                            nifti_path = self.medicalChanger.dicom_to_nifti(subseries_dir, out_file)
                            img = nib.load(str(nifti_path))
                            voxel_sizes = img.header.get_zooms()
                            shape = img.shape

                            records.append({
                            "patient_id": patient_id,
                            "date": date_str,
                            "series_name": series_str,
                            "subseries_name": subseries_dir.name,
                            "nifti_path": str(nifti_path),
                            "voxel_x": voxel_sizes[0],
                            "voxel_y": voxel_sizes[1],
                            "voxel_z": voxel_sizes[2],
                            "shape": shape,
                            })
                        except Exception as e:
                            print(f"Failed on {series_dir}: {e}")

        df = pd.DataFrame(records)
        df.to_csv("scan_manifest.csv", index=False)
        return df
    

    def preprocess_and_register(self):  
        return False