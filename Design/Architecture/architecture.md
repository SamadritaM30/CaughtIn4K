# Automated Quality Inspection System - Architecture Document

---

## I. Architecture Style: Layered Architecture

### A. Justification of Architecture Category
**(Granularity of Software Components)**

The Automated Quality Inspection System follows a **Layered Architecture** because the system is divided into multiple logical layers, where each layer performs a specific function and interacts only with the adjacent layers.

**Overall layered structure of the system:**

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
```

**Granularity of components:**

*   **Presentation Layer**
    *   Provides user interfaces for Quality Operator, Manufacturing Engineer, and System Administrator.
    *   Handles user input and displays inspection results.
*   **Application Layer**
    *   Manages inspection workflow and service coordination.
    *   Acts as a bridge between UI and business logic.
*   **Business Logic Layer**
    *   Performs defect detection using the vision model.
    *   Applies inspection rules and validation logic.
*   **Data Layer**
    *   Stores captured images, inspection results, defect details, and historical data.

---

### B. Justification for Choosing Layered Architecture
**(Scalability, Maintainability, Performance)**

The Layered Architecture is suitable for the Automated Quality Inspection System for the following reasons:

*   **Scalability**
    *   Individual layers such as defect detection or data storage can be scaled independently.
    *   New features like analytics or reporting can be added without affecting existing layers.
*   **Maintainability**
    *   Clear separation of concerns makes the system easy to understand and modify.
    *   Changes in one layer do not impact other layers directly.
*   **Performance**
    *   Inspection processing follows a structured flow from image input to result generation.
    *   Performance-critical logic is isolated in the business logic layer.
*   **Ease of Development and Testing**
    *   Each layer can be developed and tested independently.
    *   Debugging is easier due to modular design.

---

## II. Application Components of the Project

### Inspection Workflow Diagram:

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

### List of Application Components:

1.  **User Management Component**: Manages user authentication and role-based access.
2.  **Image Acquisition Component**: Captures images from industrial cameras.
3.  **Image Preprocessing Component**: Improves image quality for accurate inspection.
4.  **Inspection Management Component**: Creates, tracks, and manages inspections.
5.  **Defect Detection Component**: Uses the vision model to detect defects in images.
6.  **Inspection Result Component**: Stores inspection outcomes and confidence scores.
7.  **Defect Management Component**: Stores defect type, location, and severity.
8.  **Feedback and Validation Component**: Allows quality operators to validate or correct results.
9.  **Model Update Component**: Updates the vision model based on validated feedback.
10. **Data Storage Component**: Stores images, inspection records, defect data, and logs.

---

### Component Interaction Diagram:

```text
[User Interface]
        |
        v
[Inspection Services]
        |
        v
[Defect Detection Logic]
        |
        v
[Database / Storage]
```