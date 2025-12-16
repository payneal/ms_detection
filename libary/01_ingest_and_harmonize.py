

import os
import pathlib
import SimpleITK as sitk
import nibabel as nib
import pandas as pd

RAW_DICOM_ROOT = pathlib.Path("/data/dicom")
NIFTI_ROOT = pathlib.Path("/data/nifti")

NIFTI_ROOT.mkdir(parents=True, exist_ok=True)

def dicom_to_nifti(series_dir: pathlib.Path, out_path: pathlib.Path):
    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(str(series_dir))
    if not series_ids:
        raise RuntimeError(f"No DICOM series in {series_dir}")

    file_names = reader.GetGDCMSeriesFileNames(str(series_dir), series_ids[0])
    reader.SetFileNames(file_names)
    image = reader.Execute()
    sitk.WriteImage(image, str(out_path))
    return out_path

records = []

for patient_dir in RAW_DICOM_ROOT.iterdir():
    if not patient_dir.is_dir():
        continue
    patient_id = patient_dir.name

    for series_dir in patient_dir.iterdir():
        if not series_dir.is_dir():
            continue

        out_file = NIFTI_ROOT / f"{patient_id}__{series_dir.name}.nii.gz"
        try:
            nifti_path = dicom_to_nifti(series_dir, out_file)
            img = nib.load(str(nifti_path))
            voxel_sizes = img.header.get_zooms()
            shape = img.shape

            records.append({
                "patient_id": patient_id,
                "series_name": series_dir.name,
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
df.head()
