# Automated Quality Inspection System – Deployment and Implementation

## I. Hosting and Deployment Strategy[Marks = 5]

### A. Host Site
Given the need for real-time image processing (low latency) combined with heavy data storage and model training, a **Hybrid Cloud Architecture (Edge + AWS Cloud)** will be used:

*   **Edge Server (Local Factory Floor):**
    *   *Image Acquisition Component:* Direct connection to industrial cameras.
    *   *Image Preprocessing & Defect Detection Components:* Hosted locally on GPU-enabled edge devices (e.g., NVIDIA Jetson or local edge servers) to ensure zero-latency inference and real-time anomaly detection.
*   **Cloud Environment (Amazon Web Services - AWS):**
    *   *User Management, Inspection Management, Feedback Component:* Hosted on AWS Elastic Kubernetes Service (EKS) or AWS ECS.
    *   *Model Update Component:* Hosted on AWS SageMaker (for retraining vision models).
    *   *Data Storage Component:* Amazon S3 (for storing raw/processed images) and Amazon RDS (PostgreSQL for metadata, inspection results, and defect logs).

### B. Deployment Strategy
The deployment process follows a containerized micro-services approach:
1.  **Containerization:** Package all components (Python/Node.js) into Docker containers.
2.  **Server Configuration:**
    *   Provision AWS EC2 instances (Compute optimized) for backend microservices.
    *   Provision local Edge Server with CUDA/GPU drivers for the vision model.
3.  **CI/CD Pipeline:** Use GitHub Actions or Jenkins to automate the building of Docker images and pushing them to Amazon ECR (Elastic Container Registry).
4.  **API Configuration:**
    *   Deploy an **API Gateway** (e.g., Kong or AWS API Gateway) to route incoming frontend requests to the correct backend components.
    *   Use **REST APIs** for synchronous requests (e.g., User Login, Fetch History) and **gRPC/WebSockets** for real-time camera feed and anomaly detection communication between Edge and Cloud.
5.  **Orchestration:** Deploy Cloud containers using Kubernetes (EKS) to handle automatic scaling based on factory load.

### C. Security Measures (Optional)
*   **Network Security:** All cloud components will reside inside a Virtual Private Cloud (VPC) with strict Security Groups (Firewalls) blocking direct internet access to databases.
*   **Data Encryption:** 
    *   *At Rest:* AWS KMS (Key Management Service) with AES-256 for S3 buckets and RDS.
    *   *In Transit:* TLS/SSL (HTTPS) enforced for all API communication.
*   **Authentication:** JWT (JSON Web Tokens) and Role-Based Access Control (RBAC) configured via AWS Cognito.

---

## II. End-User Access and Interaction Diagram[Marks = 10]

### How Users Access Services
*   **Quality Operators:** Access a local **Desktop Application / Web Dashboard** connected to the Edge Server for real-time monitoring of the assembly line and immediate feedback validation.
*   **Manufacturing Engineers & System Admins:** Access a **Cloud-based Web Application** (React/Angular) via standard web browsers to view aggregated reports, update model configurations, and manage user access.

### Interaction Diagram
Below is the pictorial representation (System Sequence & Interaction Diagram) showing how users and components interact:

```mermaid
graph TD
    %% Actors
    Camera((Industrial Camera))
    Operator((Quality Operator))
    Engineer((Manufacture Engineer))

    %% Frontend UIs
    subgraph Presentation Layer [Front End]
        EdgeUI[Operator Dashboard]
        CloudUI[Admin/Engineer Portal]
    end

    %% Backend Services
    subgraph Edge Backend [Local Edge Server]
        Acq[Image Acquisition]
        Preproc[Image Preprocessing]
        Detect[Defect Detection Model]
    end

    subgraph Cloud Backend [AWS Cloud]
        APIGW[API Gateway]
        InspMgmt[Inspection Management]
        Feedback[Validation & Feedback]
        ModelUp[Model Update]
    end

    %% Database
    subgraph Data Layer [Databases]
        RDS[(SQL Database)]
        S3[(Image Storage S3)]
    end

    %% Interactions
    Camera -->|Live Feed| Acq
    Acq --> Preproc
    Preproc --> Detect
    Detect -->|Result & Confidence| EdgeUI
    
    Operator -->|Views & Validates| EdgeUI
    EdgeUI -->|Send Validation via REST| APIGW
    
    Engineer -->|Manage Models/Rules| CloudUI
    CloudUI -->|REST API| APIGW
    
    APIGW --> InspMgmt
    APIGW --> Feedback
    APIGW --> ModelUp
    
    InspMgmt --> RDS
    Detect -->|Uploads Defect Image| S3
    Feedback --> RDS
    ModelUp -->|Pulls Validated Data| S3