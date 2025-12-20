import os
import pathlib
import pandas as pd
import numpy as np
from PIL import Image
import nibabel as nib
import ants
import SimpleITK as sitk
from libary.util.medicalFormatChanger import MedicalFormatChanger

class MSDection:
    def __init__(self, dicom_path, nifti_output_path, image_output_path):
        self.dicom_path = dicom_path
        self.nifti_output_path = nifti_output_path
        self.image_output_path = image_output_path
        self.medicalChanger = MedicalFormatChanger()
    
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
        
        MANIFEST_PATH = pathlib.Path("scan_manifest.csv")
        PREPROC_ROOT = pathlib.Path("./data/preproc")
        PREPROC_ROOT.mkdir(parents=True, exist_ok=True)
        
        df = pd.read_csv(MANIFEST_PATH)
        preproc_records = []

        for _, row in df.iterrows():
            src = pathlib.Path(row["nifti_path"])
            out_file = PREPROC_ROOT / (src.stem + "_mni.nii.gz")
            try:
                out_path, voxel_mm3 = self._preprocess_to_mni(str(src), out_file)
                preproc_records.append({
                    **row.to_dict(),
                    "preproc_nifti_path": str(out_path),
                    "voxel_volume_mm3": voxel_mm3,
                })
            except Exception as e:
                print(f"Failed preprocessing {src}: {e}")
       
        df_preproc = pd.DataFrame(preproc_records)
        # df_preproc.to_csv("scan_manifest_preproc.csv", index=False)
        df_preproc.head()
        return df_preproc

            
    def _preprocess_to_mni(self, nifti_path: str, out_path: pathlib.Path):
        TEMPLATE_PATH = pathlib.Path("./data/templates/MNI152_T1_1mm.nii.gz")

        # img = sitk.ReadImage(nifti_path, sitk.sitkFloat32)  
        img = ants.image_read(nifti_path)
        # preferable to use ants image read but have to resolve sitk and ants compatibility issue first

        img_n4 = ants.n4_bias_field_correction(img)
        brain_mask = ants.get_mask(img_n4)
        img_brain = img_n4 * brain_mask

        template = ants.image_read(str(TEMPLATE_PATH))
        reg = ants.registration(fixed=template, moving=img_brain, type_of_transform="SyN")
        img_mni = reg["warpedmovout"]

        ants.image_write(img_mni, str(out_path))

        voxel_mm3 = abs(img_mni.spacing[0] * img_mni.spacing[1] * img_mni.spacing[2])
        return out_path, voxel_mm3