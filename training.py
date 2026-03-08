import os
from anomalib.data import MVTec
from anomalib.models import Patchcore
from anomalib.engine import Engine

def train_local_item_model(mvtec_dataset_path: str, item_name: str = "bottle"):
    print(f"Initializing Quality Inspection Training Pipeline for Item: '{item_name}'...")
    print(f"Using local MVTec dataset located at: {os.path.abspath(mvtec_dataset_path)}")

    
    datamodule = MVTec(
        root=mvtec_dataset_path,
        category=item_name,
        train_batch_size=32,
        eval_batch_size=32,
        num_workers=11 
    )

    
    model = Patchcore(
        backbone="wide_resnet50_2",
        pre_trained=True
    )

    
    output_dir = f"C:/Users/shikh/OneDrive/Desktop/Computer Vision/CaughtIn4K/inspection_model_outputs/{item_name}"
    os.makedirs(output_dir, exist_ok=True)

    
    engine = Engine(
        default_root_dir=output_dir,
        max_epochs=1,
        accelerator="auto", 
        devices=1,
    )

    print(f"Starting Model Training on 'Good' products only for '{item_name}'...")
    engine.fit(datamodule=datamodule, model=model)

    
    print(f"Testing model against defective products for '{item_name}'...")
    engine.test(datamodule=datamodule, model=model)

    print(f"Preliminary Training Complete! Check: {output_dir}")

if __name__ == "__main__":
    
    LOCAL_MVTEC_ROOT = r"C:/Users/shikh/Downloads/mvtec_anomaly_detection"
    
    
    ITEM_TO_TRAIN = "bottle" 

    train_local_item_model(mvtec_dataset_path=LOCAL_MVTEC_ROOT, item_name=ITEM_TO_TRAIN)