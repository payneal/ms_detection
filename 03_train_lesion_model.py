# 03_train_lesion_model.ipynb

import os
import torch
from monai.transforms import (
    Compose, LoadImageD, AddChannelD, SpacingD,
    OrientationD, NormalizeIntensityD,
    RandCropByPosNegLabelD, ToTensorD
)
from monai.data import CacheDataset, DataLoader
from monai.networks.nets import UNet
from monai.losses import DiceLoss
from monai.metrics import DiceMetric

import pandas as pd

device = "cuda" if torch.cuda.is_available() else "cpu"

df = pd.read_csv("scan_manifest_preproc_with_labels.csv")

train_files = [
    {"image": row["preproc_nifti_path"], "label": row["lesion_mask_path"]}
    for _, row in df.iterrows()
    if row["split"] == "train"
]

val_files = [
    {"image": row["preproc_nifti_path"], "label": row["lesion_mask_path"]}
    for _, row in df.iterrows()
    if row["split"] == "val"
]

train_transforms = Compose([
    LoadImageD(keys=["image", "label"]),
    AddChannelD(keys=["image", "label"]),
    SpacingD(keys=["image", "label"], pixdim=(1.0, 1.0, 1.0),
             mode=("bilinear", "nearest")),
    OrientationD(keys=["image", "label"], axcodes="RAS"),
    NormalizeIntensityD(keys="image"),
    RandCropByPosNegLabelD(
        keys=["image", "label"], label_key="label",
        spatial_size=(128, 128, 128),
        pos=1, neg=1, num_samples=4,
    ),
    ToTensorD(keys=["image", "label"]),
])

val_transforms = Compose([
    LoadImageD(keys=["image", "label"]),
    AddChannelD(keys=["image", "label"]),
    SpacingD(keys=["image", "label"], pixdim=(1.0, 1.0, 1.0),
             mode=("bilinear", "nearest")),
    OrientationD(keys=["image", "label"], axcodes="RAS"),
    NormalizeIntensityD(keys="image"),
    ToTensorD(keys=["image", "label"]),
])

train_ds = CacheDataset(train_files, train_transforms)
val_ds = CacheDataset(val_files, val_transforms)

train_loader = DataLoader(train_ds, batch_size=2, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=1)

model = UNet(
    spatial_dims=3,
    in_channels=1,
    out_channels=2,
    channels=(16, 32, 64, 128, 256),
    strides=(2, 2, 2, 2),
    num_res_units=2,
).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
loss_fn = DiceLoss(to_onehot_y=True, softmax=True)
dice_metric = DiceMetric(include_background=False, reduction="mean")

best_val_dice = 0.0

for epoch in range(1, 51):
    model.train()
    epoch_loss = 0.0
    for batch in train_loader:
        images = batch["image"].to(device)
        labels = batch["label"].to(device)

        logits = model(images)
        loss = loss_fn(logits, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()

    # simple validation
    model.eval()
    with torch.no_grad():
        dice_scores = []
        for batch in val_loader:
            images = batch["image"].to(device)
            labels = batch["label"].to(device)
            logits = model(images)
            dice_metric(y_pred=logits, y=labels)
        mean_dice = dice_metric.aggregate().item()
        dice_metric.reset()

    print(f"Epoch {epoch}: loss={epoch_loss:.4f}, val_dice={mean_dice:.4f}")

    if mean_dice > best_val_dice:
        best_val_dice = mean_dice
        torch.save(model.state_dict(), "ms_lesion_unet.pt")
        print("Saved new best model.")
