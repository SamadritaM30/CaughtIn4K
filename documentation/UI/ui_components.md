# UI Implementation and User Interaction

````md id="caughtin4k-part2-full"
# Part II — UI Implementation and User Interaction

To implement the user interface of our project **CaughtIn4K**, we developed a **web-based interface using HTML, CSS, and JavaScript**. The interface allows quality inspectors to upload product images, view inspection results, provide feedback, and review inspection history.

The UI follows a **direct manipulation design**, where users interact with the system using graphical elements such as buttons, file upload fields, and visual result displays.

---

# 1. UI Components Implemented

The following UI components were implemented in the CaughtIn4K system:

| UI Component | Purpose |
|---|---|
| Image Upload Component | Allows users to upload product images for inspection |
| Inspection Result Panel | Displays prediction results and heatmaps |
| Feedback Button | Allows inspectors to confirm or correct predictions |
| Inspection History View | Shows past inspection records |
| Interaction Flow Visualization | Demonstrates system interaction between components |

These components together provide an intuitive interface for interacting with the defect detection system.

---

# 2. UI Code Implementation

The following code implements the UI used to visualize the interaction flows and user interface components of the CaughtIn4K system.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CaughtIn4K – Interaction Flow Diagrams</title>

<style>

body{
font-family:Arial, sans-serif;
background:#07101f;
color:white;
padding:40px;
}

.container{
max-width:900px;
margin:auto;
}

.card{
background:#0c1829;
padding:20px;
border-radius:10px;
margin-bottom:20px;
}

button{
padding:10px 20px;
border:none;
border-radius:6px;
background:#00d4ff;
cursor:pointer;
font-weight:bold;
}

input[type=file]{
margin-top:10px;
}

table{
width:100%;
border-collapse:collapse;
margin-top:15px;
}

td,th{
border:1px solid #162840;
padding:8px;
text-align:left;
}

</style>
</head>

<body>

<div class="container">

<h1>CaughtIn4K Inspection Interface</h1>

<div class="card">

<h2>Upload Product Image</h2>

<form action="/upload" method="POST" enctype="multipart/form-data">

<label>Select Image</label>
<br>

<input type="file" name="image" required>

<br><br>

<button type="submit">Upload and Inspect</button>

</form>

</div>

<div class="card">

<h2>Inspection Result</h2>

<p>Prediction: <strong>Defective / Non-Defective</strong></p>

<p>Confidence Score: <strong>92%</strong></p>

<img src="heatmap_example.png" width="300">

<br><br>

<button>Submit Feedback</button>

</div>

<div class="card">

<h2>Inspection History</h2>

<table>

<tr>
<th>ID</th>
<th>Date</th>
<th>Prediction</th>
<th>Confidence</th>
</tr>

<tr>
<td>101</td>
<td>2026-03-10</td>
<td>Defective</td>
<td>0.92</td>
</tr>

<tr>
<td>102</td>
<td>2026-03-10</td>
<td>Non-Defective</td>
<td>0.87</td>
</tr>

</table>

</div>

</div>

</body>
</html>
````

---

# 3. User Interaction with the System

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

## Step 4 — Human Feedback

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