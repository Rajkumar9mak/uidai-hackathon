# 🇮🇳 Aadhaar Service Stress Dashboard (ASSI)

A decision-support analytics and visualization platform built using aggregated Aadhaar datasets to identify enrolment bottlenecks, service stress, and regions requiring policy intervention.

This project introduces the **Aadhaar Service Stress Index (ASSI)** — a composite indicator designed to help authorities prioritize Aadhaar service improvements using data-driven insights.

---

## 🔍 Problem Statement

Aadhaar enrolment and update services experience uneven operational load across regions due to population mobility, demographic corrections, biometric refresh needs, and infrastructure limitations.

However, decision-makers currently lack:
- A unified metric to quantify service stress
- Geographic visibility of bottlenecks
- Actionable prioritization tools for interventions

---

## 💡 Solution Overview

This project analyzes aggregated and anonymised Aadhaar datasets to:

- Identify regions with high service stress
- Predict enrolment bottlenecks and dropout risk
- Visualize stress patterns spatially across India
- Simulate policy interventions using a dashboard

The solution is delivered through an **interactive Streamlit dashboard**.

---

## 📊 Aadhaar Service Stress Index (ASSI)

**ASSI** is a normalized score (0–100) that captures Aadhaar service pressure using multiple signals:

### Components Used
- **Friction Pressure**: Repeated updates per enrolment  
- **Update Load Intensity**: Total demographic + biometric updates  
- **Biometric Pressure**: Share of biometric updates  
- **Enrolment Weakness**: Low enrolment with high update demand  

### Interpretation
| ASSI Range | Meaning |
|-----------|--------|
| 0–30 | Low stress (stable services) |
| 30–60 | Moderate stress |
| 60–100 | High stress / bottleneck risk |

ASSI is designed as a **transparent, explainable, and policy-safe** indicator.

---

## 🖥️ Dashboard Features

- 📈 **National KPIs** (ASSI, bottleneck risk)
- 🗺️ **India map visualization** (ASSI-based choropleth)
- 🚨 **Intervention planner** (Top high-risk regions)
- 🔍 **State-wise drill-down analytics**
- 🎛️ **What-if policy simulator**
- 📊 **Interactive charts & tables**

---

## 🧰 Tech Stack

- **Python**
- **Pandas** – data processing
- **Streamlit** – interactive dashboard
- **Matplotlib** – visualizations
- **GeoPandas** – India map rendering

---


## 📁 Project Structure

<pre>
PROGRAM/
├── dashboard.py
│   └── Streamlit dashboard (visualization only)
│
├── adhar.py
│   └── Data processing & ASSI computation
│
├── aadhaar_bottleneck_prediction.csv
│   └── Final processed dataset with ASSI & risk labels
│
├── INDIA_STATES.geojson
│   └── India state boundaries for map visualization
│
├── api_data_aadhar_enrolment/
│   └── Aggregated Aadhaar enrolment datasets
│
├── api_data_aadhar_demographic/
│   └── Aggregated demographic update datasets
│
├── api_data_aadhar_biometric/
│   └── Aggregated biometric update datasets
│
└── README.md
    └── Project documentation
</pre>


---

## ▶️ How to Run the Project

Follow the steps below to run the Aadhaar Service Stress Dashboard locally.

### 1️⃣ Prerequisites
Ensure the following are installed on your system:
- Python 3.9 or above
- Git (optional, for cloning the repository)

---

### 2️⃣ Install Required Python Packages

Open a terminal or PowerShell in the project directory and run:

```bash 
pip install pandas streamlit matplotlib geopandas
```

---
###3️⃣ Data Processing (ASSI Computation)

This step processes the aggregated Aadhaar datasets and computes the
Aadhaar Service Stress Index (ASSI).

Requirements:

Python 3.9 or higher

Required libraries:

pandas

numpy

matplotlib

Input folders (must exist):

api_data_aadhar_enrolment/

api_data_aadhar_demographic/

api_data_aadhar_biometric/

Output generated:
- `aadhaar_bottleneck_prediction.csv`

Run command:
```bash
python adhar.py


