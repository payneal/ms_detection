import os
import pathlib  
import SimpleITK as sitk
import nibabel as nib
import numpy as np
from PIL import Image


class MedicalFormatChanger:
    def __init__(self):
        pass 

    def convert_nii_to_image( 
            self, 
            nii_path: str | pathlib.Path,
            out_dir: str | pathlib.Path,
            plane: str = "axial",
            slice_index: int | None = None,
            output_format: str = "png",
            normalize: bool = True,
            percentile_clip: tuple[float, float] = (1, 99),
        ) -> list[pathlib.Path]:    
       
        # =================================================================
        # Convert a NIfTI (.nii/.nii.gz) volume into PNG/JPEG images.
        # 
        # Parameters
        # ----------
        # nii_path : str | Path
        #     Path to NIfTI file.
        # out_dir : str | Path
        #     Directory where images will be saved.
        # plane : {"axial", "coronal", "sagittal"}
        #     Anatomical plane to slice.
        # slice_index : int | None
        #     If provided, saves only this slice index. Otherwise saves all slices.
        # output_format : {"png", "jpg", "jpeg"}
        #     Image format.
        # normalize : bool
        #     Whether to normalize intensities to 0–255.
        # percentile_clip : (low, high)
        #     Percentile clipping for MRI contrast normalization.

        # Returns
        # -------
        # list[Path]
        #   Paths to saved images.
        # """
        nii_path = pathlib.Path(nii_path)
        out_dir = pathlib.Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        img = nib.load(str(nii_path))
        data = img.get_fdata()

        # Ensure 3D
        if data.ndim > 3:
            data = data[..., 0]

        ## Select slicing axis
        if plane == "axial":
            axis = 2
        elif plane == "coronal":
            axis = 1
        elif plane == "sagittal":
            axis = 0
        else:
            raise ValueError("plane must be axial, coronal, or sagittal")

        # Intensity normalization
        if normalize:
            lo, hi = np.percentile(data, percentile_clip)
            data = np.clip(data, lo, hi)
            data = (data - lo) / (hi - lo + 1e-8)
            data = (data * 255).astype(np.uint8)
        else:
            data = data.astype(np.uint8)

        saved_files = []

        def save_slice(slice_data: np.ndarray, idx: int):
            # Rotate for human-readable orientation
            slice_data = np.rot90(slice_data)

            img_pil = Image.fromarray(slice_data)
            fname = f"{nii_path.stem}_{plane}_slice_{idx:03d}.{output_format}"
            out_path = out_dir / fname
            img_pil.save(out_path)
            saved_files.append(out_path)

        if slice_index is not None:
            slice_data = np.take(data, slice_index, axis=axis)
            save_slice(slice_data, slice_index)
        else:
            for idx in range(data.shape[axis]):
                slice_data = np.take(data, idx, axis=axis)
                save_slice(slice_data, idx)

        return saved_files
    
    def dicom_to_nifti(self,series_dir: pathlib.Path, out_path: pathlib.Path):
        reader = sitk.ImageSeriesReader()
        series_ids = reader.GetGDCMSeriesIDs(str(series_dir))
        if not series_ids:
            raise RuntimeError(f"No DICOM series in {series_dir}")

        file_names = reader.GetGDCMSeriesFileNames(str(series_dir), series_ids[0])
        reader.SetFileNames(file_names)
        image = reader.Execute()
        sitk.WriteImage(image, str(out_path))
        return out_path
