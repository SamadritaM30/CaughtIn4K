import os
from anomalib.data import MVTec
from anomalib.models import Patchcore
from anomalib.engine import Engine

def train_local_item_model(mvtec_dataset_path: str, item_name: str = "bottle"):
    print(f"Initializing Quality Inspection Training Pipeline for Item: '{item_name}'...")
    print(f"Using local MVTec dataset located at: {os.path.abspath(mvtec_dataset_path)}")

    # 1. Setup the Dataset
    # num_workers=0 is required for Windows to prevent crashes
    datamodule = MVTec(
        root=mvtec_dataset_path,
        category=item_name,
        train_batch_size=32,
        eval_batch_size=32,
        num_workers=11 
    )

    # 2. Initialize the Model (PatchCore)
    model = Patchcore(
        backbone="wide_resnet50_2",
        pre_trained=True
    )

    # 3. Initialize the Training Engine
    output_dir = f"C:/Users/shikh/OneDrive/Desktop/Computer Vision/CaughtIn4K/inspection_model_outputs/{item_name}"
    os.makedirs(output_dir, exist_ok=True)

    # FIX: Removed 'task="segmentation"'
    # The Engine passes extra arguments to the PyTorch Lightning Trainer.
    # 'task' is not a valid Trainer argument, so we remove it.
    engine = Engine(
        default_root_dir=output_dir,
        max_epochs=1,
        accelerator="auto", 
        devices=1,
    )

    # 4. Start Training
    print(f"Starting Model Training on 'Good' products only for '{item_name}'...")
    engine.fit(datamodule=datamodule, model=model)

    # 5. Test the Model
    print(f"Testing model against defective products for '{item_name}'...")
    engine.test(datamodule=datamodule, model=model)

    print(f"Preliminary Training Complete! Check: {output_dir}")

if __name__ == "__main__":
    # --- Configuration ---
    # use r"" (raw string) to handle Windows backslashes correctly
    LOCAL_MVTEC_ROOT = r"C:/Users/shikh/Downloads/mvtec_anomaly_detection"
    
    # Make sure this matches the folder name exactly inside your dataset
    ITEM_TO_TRAIN = "bottle" 

    train_local_item_model(mvtec_dataset_path=LOCAL_MVTEC_ROOT, item_name=ITEM_TO_TRAIN)