# Automated Quality Inspection System  
## Use Case Diagram Description

---

## 1. Introduction

This use case diagram represents the **behavioral aspects** of the Automated Quality Inspection (AQI) System.  
The system is designed to automatically detect product defects using **computer vision techniques**, while incorporating **human validation** and **continual learning**.

The diagram shows:
- Interactions between **external actors** and the system
- Relationships among different **use cases**

---

## 2. Actors

The following external actors interact with the system:

### 2.1 Quality Operator
- Captures or uploads product images  
- Initiates anomaly detection  
- Views classification results  
- Validates inspection results  
- Corrects false positives  
- Marks missed defects  
- Views inspection history  
- Monitors system performance  

### 2.2 Manufacturing Engineer
- Updates the model incrementally  
- Views inspection history  
- Monitors system performance  

### 2.3 System Administrator
- Manages system configuration  
- Monitors system performance  

### 2.4 Industrial Camera (External)
- Provides real-time product images to the system  
- Connected to the **Capture Image** use case  

### 2.5 System Database (External)
- Stores inspection results and human feedback  
- Provides stored data for history viewing and performance monitoring  

---

## 3. Main Functional Flow

The main workflow of the system is as follows:

1. The Quality Operator captures or uploads product images  
2. The image is preprocessed  
3. The system performs **Anomaly Detection**, which includes:
   - Localise defective regions  
   - Generate confidence score  
   - Generate visual explanations  
   - Classify products  
4. The classification result is stored in the system database  
5. The Quality Operator validates the inspection result  
6. If errors are found:
   - Correct false positives *(extend)*  
   - Mark missed defects *(extend)*  
7. Human feedback is stored  
8. Validated feedback is used to update the model incrementally  
9. Inspection history can be viewed  
10. System performance can be monitored  

---

## 4. Include Relationships

The dashed arrows represent **<<include>> relationships**, while other connections are **associative relationships**.

### 4.1 Anomaly Detection includes
- Preprocess Image  
- Localise Defective Regions  
- Generate Confidence Score  
- Generate Visual Explanations  
- Classify Products  

### 4.2 Classify Products includes
- Store Inspection Result  
- Validate Inspection Result  

### 4.3 Validate Inspection Result includes
- Correct False Positives  
- Mark Missed Defects  
- Update Model Incrementally  

### 4.4 Store Human Feedback includes
- Use Validated Feedback  

### 4.5 Use Validated Feedback includes
- Update Model Incrementally  

### 4.6 View Inspection History includes
- Monitor Performance  

---

## 5. Conclusion

The use case diagram clearly illustrates:
- Interaction between **human users**, **hardware devices**, and the AQI system  
- The **automated defect detection** workflow  
- The **human-in-the-loop validation** mechanism  
- The **continual learning process** through feedback integration  
