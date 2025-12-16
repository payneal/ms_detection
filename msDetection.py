import os
import pathlib
import SimpleITK as sitk
import nibabel as nib
import pandas as pd


class MSDection:
    def __init__(self):
        pass

    def detect(self, data):
        # Placeholder for multi-scale detection logic

        print("Performing multi-scale detection...")
        return {"detections": []}
    
    def ingest_and_harmonize(self, dicom_path, nifti_output_path):
       
        RAW_DICOM_ROOT = pathlib.Path(dicom_path)
        NIFTI_ROOT = pathlib.Path(nifti_output_path)

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
                            nifti_path = dicom_to_nifti(subseries_dir, out_file)
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