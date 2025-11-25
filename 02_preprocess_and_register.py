# 02_preprocess_and_register.ipynb

import pathlib
import ants
import nibabel as nib
import pandas as pd

MANIFEST_PATH = pathlib.Path("scan_manifest.csv")
TEMPLATE_PATH = pathlib.Path("/templates/MNI152_T1_1mm.nii.gz")
PREPROC_ROOT = pathlib.Path("/data/preproc")
PREPROC_ROOT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(MANIFEST_PATH)

def preprocess_to_mni(nifti_path: str, out_path: pathlib.Path):
    img = ants.image_read(nifti_path)

    img_n4 = ants.n4_bias_field_correction(img)
    brain_mask = ants.get_mask(img_n4)
    img_brain = img_n4 * brain_mask

    template = ants.image_read(str(TEMPLATE_PATH))
    reg = ants.registration(fixed=template, moving=img_brain, type_of_transform="SyN")
    img_mni = reg["warpedmovout"]

    ants.image_write(img_mni, str(out_path))

    voxel_mm3 = abs(img_mni.spacing[0] * img_mni.spacing[1] * img_mni.spacing[2])
    return out_path, voxel_mm3

preproc_records = []

for _, row in df.iterrows():
    src = pathlib.Path(row["nifti_path"])
    out_file = PREPROC_ROOT / (src.stem + "_mni.nii.gz")
    try:
        out_path, voxel_mm3 = preprocess_to_mni(str(src), out_file)
        preproc_records.append({
            **row.to_dict(),
            "preproc_nifti_path": str(out_path),
            "voxel_volume_mm3": voxel_mm3,
        })
    except Exception as e:
        print(f"Failed preprocessing {src}: {e}")

df_preproc = pd.DataFrame(preproc_records)
df_preproc.to_csv("scan_manifest_preproc.csv", index=False)
df_preproc.head()
