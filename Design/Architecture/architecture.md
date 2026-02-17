# Automated Quality Inspection System – Architecture Document

---

## I. Architecture Style: Layered Architecture

### A. Justification of Architecture Category  
**(Granularity of Software Components)**

The Automated Quality Inspection System follows a **Layered Architecture** because the system is divided into multiple logical layers, where each layer performs a specific function and interacts only with its adjacent layers. This structure ensures clear separation of concerns and controlled dependency flow.

### Overall Layered Structure of the System

```text
----------------------------------------
|        Presentation Layer             |
| (Operator / Engineer / Admin UI)      |
----------------------------------------
|        Application Layer              |
| (Inspection & Workflow Services)      |
----------------------------------------
|        Business Logic Layer           |
| (Defect Detection, Validation)        |
----------------------------------------
|            Data Layer                 |
| (Images, Results, Defects, Logs)      |
----------------------------------------
````

### Granularity of Components

* **Presentation Layer**

  * Provides user interfaces for Quality Operator, Manufacturing Engineer, and System Administrator.
  * Handles user input and displays inspection results and reports.

* **Application Layer**

  * Manages inspection workflows and service coordination.
  * Acts as a bridge between the presentation layer and business logic layer.

* **Business Logic Layer**

  * Performs defect detection using the vision-based model.
  * Applies inspection rules, validation logic, and decision-making.

* **Data Layer**

  * Stores captured images, inspection results, defect details, logs, and historical data.
  * Manages persistent data access.

The clear division of responsibilities and coarse-grained nature of each layer justifies that the system belongs to the **Layered Architecture** category.

---

### B. Justification for Choosing Layered Architecture

**(Scalability, Maintainability, Performance)**

The Layered Architecture is suitable for the Automated Quality Inspection System for the following reasons:

* **Scalability**

  * Individual layers such as defect detection or data storage can be scaled independently.
  * New functionalities like analytics or reporting can be added without affecting existing layers.

* **Maintainability**

  * Clear separation of concerns makes the system easier to understand, modify, and extend.
  * Changes in one layer do not directly impact other layers.

* **Performance**

  * Inspection processing follows a structured and predictable flow from image input to result generation.
  * Performance-critical logic is isolated within the business logic layer.

* **Ease of Development and Testing**

  * Each layer can be developed and tested independently.
  * Modular design simplifies debugging and reduces development complexity.

### Why Other Architecture Styles Were Not Chosen

* **Monolithic Architecture**

  * Not chosen because tight coupling makes the system difficult to maintain, scale, and update when defect detection logic or models change.

* **Microservices Architecture**

  * Not chosen because it introduces unnecessary complexity, network latency, and deployment overhead for a tightly integrated, real-time inspection system.

* **Service-Oriented Architecture (SOA)**

  * Not chosen because heavy service orchestration and communication overhead are unsuitable for performance-critical image processing workflows.

Hence, **Layered Architecture** provides the best balance of simplicity, performance, scalability, and maintainability for the Automated Quality Inspection System.

---

## II. Application Components of the Project

### Inspection Workflow Diagram

```text
[Camera / Image Source]
        |
        v
[Image Acquisition & Preprocessing]
        |
        v
[Defect Detection (Vision Model)]
        |
        v
[Inspection Result & Defect Details]
```

### List of Application Components

1. **User Management Component**
   Manages user authentication and role-based access control.

2. **Image Acquisition Component**
   Captures images from industrial cameras or image sources.

3. **Image Preprocessing Component**
   Enhances image quality through noise reduction and normalization.

4. **Inspection Management Component**
   Creates, tracks, and manages inspection workflows.

5. **Defect Detection Component**
   Uses the vision model to identify and classify defects.

6. **Inspection Result Component**
   Stores inspection outcomes and confidence scores.

7. **Defect Management Component**
   Maintains defect type, severity, and location information.

8. **Feedback and Validation Component**
   Allows quality operators to validate or correct inspection results.

9. **Model Update Component**
   Updates the vision model based on validated feedback.

10. **Data Storage Component**
    Stores images, inspection records, defect data, and system logs.

---

### Component Interaction Diagram

```text
[User Interface]
       ^ |
       | v
[Inspection Services]
       ^ |
       | v
[Defect Detection Logic]
       ^ |
       | v
[Database / Storage]
```
