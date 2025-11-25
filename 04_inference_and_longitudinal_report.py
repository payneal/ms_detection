# 04_inference_and_longitudinal_report.ipynb

import pathlib
import torch
import numpy as np
import nibabel as nib
import pandas as pd
import matplotlib.pyplot as plt

from monai.transforms import (
    Compose, LoadImageD, AddChannelD, SpacingD,
    OrientationD, NormalizeIntensityD, ToTensorD
)
from monai.networks.nets import UNet

device = "cuda" if torch.cuda.is_available() else "cpu"

df = pd.read_csv("scan_manifest_preproc.csv")

model = UNet(
    spatial_dims=3,
    in_channels=1,
    out_channels=2,
    channels=(16, 32, 64, 128, 256),
    strides=(2, 2, 2, 2),
    num_res_units=2,
)
model.load_state_dict(torch.load("ms_lesion_unet.pt", map_location=device))
model = model.to(device)
model.eval()

inference_transforms = Compose([
    LoadImageD(keys=["image"]),
    AddChannelD(keys=["image"]),
    SpacingD(keys=["image"], pixdim=(1.0, 1.0, 1.0), mode=("bilinear",)),
    OrientationD(keys=["image"], axcodes="RAS"),
    NormalizeIntensityD(keys="image"),
    ToTensorD(keys=["image"]),
])

LESION_MASK_ROOT = pathlib.Path("/data/lesion_masks")
LESION_MASK_ROOT.mkdir(parents=True, exist_ok=True)

def run_inference(image_path: str, out_mask_path: pathlib.Path):
    data = {"image": image_path}
    data = inference_transforms(data)
    img_tensor = data["image"].unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(img_tensor)
        probs = torch.softmax(logits, dim=1)
        pred = probs.argmax(dim=1).squeeze(0).cpu().numpy()

    img_nib = nib.load(image_path)
    mask_img = nib.Nifti1Image(pred.astype("uint8"), img_nib.affine)
    nib.save(mask_img, str(out_mask_path))
    return out_mask_path

def compute_lesion_stats(mask_path: str, voxel_volume_mm3: float):
    mask = nib.load(mask_path).get_fdata()
    lesion_voxels = np.sum(mask > 0.5)
    lesion_volume_ml = lesion_voxels * voxel_volume_mm3 / 1000.0
    return lesion_voxels, lesion_volume_ml

lesion_records = []

for _, row in df.iterrows():
    preproc_path = row["preproc_nifti_path"]
    voxel_volume_mm3 = row["voxel_volume_mm3"]
    scan_date = row.get("scan_date", None)

    mask_path = LESION_MASK_ROOT / (pathlib.Path(preproc_path).stem + "_lesions.nii.gz")
    mask_path = run_inference(preproc_path, mask_path)

    voxels, volume_ml = compute_lesion_stats(str(mask_path), voxel_volume_mm3)

    lesion_records.append({
        "patient_id": row["patient_id"],
        "scan_date": scan_date,
        "preproc_nifti_path": preproc_path,
        "lesion_mask_path": str(mask_path),
        "lesion_voxels": voxels,
        "lesion_volume_ml": volume_ml,
    })

df_lesions = pd.DataFrame(lesion_records).sort_values("scan_date")
df_lesions.to_csv("lesion_summary.csv", index=False)
df_lesions

# Quick longitudinal plot (what you’ll show neurology + execs):

plt.figure()
plt.plot(df_lesions["scan_date"], df_lesions["lesion_volume_ml"], marker="o")
plt.xticks(rotation=45)
plt.xlabel("Scan date")
plt.ylabel("Lesion volume (ml)")
plt.title("Lesion burden over time")
plt.grid(True)
plt.tight_layout()
plt.show()
