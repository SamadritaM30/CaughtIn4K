# 1. User Interaction with the System

The following steps describe how a user interacts with the CaughtIn4K interface.

## Step 1 — Upload Product Image

The inspector uploads a product image using the upload interface.

The browser sends a request to the backend:

```
POST /upload
```

The Flask backend receives the image and sends it to the machine learning inference engine for defect detection.

---

## Step 2 — Image Processing

The ML model processes the image and performs:

* Image preprocessing
* Anomaly detection
* Grad-CAM heatmap generation
* Confidence score calculation

The image and heatmap are stored in **AWS S3**, and inspection results are stored in **AWS RDS**.

---

## Step 3 — Display Inspection Result

After processing, the system returns the prediction results to the browser.

The UI displays:

* Defect prediction
* Confidence score
* Grad-CAM heatmap highlighting the defect area

---

## Step 4 — Human Feedback (to be implemented)

The inspector can confirm or correct the prediction using the **Submit Feedback** button.

The browser sends the feedback request:

```
POST /feedback
```

The corrected label is stored in the database and later used for **continual model learning**.

---

## Step 5 — Viewing Inspection History

Users can view previous inspection records.

The browser sends a request:

```
GET /history
```

The backend retrieves the inspection data from the database and displays it in the history table.

---

# 4. Interaction Summary

Through this UI implementation, users can perform the following actions:

* Upload product images
* Run automated defect detection
* View model predictions and heatmaps
* Provide feedback to improve the model
* Review historical inspection results

The user interface provides a simple and intuitive way for inspectors to interact with the **CaughtIn4K defect detection system** while the backend services handle machine learning inference and data storage.

```

---
