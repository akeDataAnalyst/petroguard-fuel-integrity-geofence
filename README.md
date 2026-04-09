# Fuel Integrity & Geofence Intelligence
[![Live Demo](https://img.shields.io/badge/Streamlit-Live%20Demo-brightgreen)](https://petroguard-fuel-integrity-geofence-c8t3x4tq8pv6hvar7f84bd.streamlit.app/)

## Description
PetroGuard Elite is a high-fidelity telematics dashboard designed to detect and analyze fuel theft in real-time. By synchronizing GPS geofencing with volumetric sensor data, the system identifies "Transit Shrinkage" that traditional manual auditing misses. It applies ASTM D1250 standards to differentiate between natural thermal expansion and unauthorized valve actuations.

---

## The Problem: "The Invisible Leak"
In fuel logistics, carriers face millions in annual losses due to siphoning during transit. 
* **Thermal Masking:** Fuel expands in heat and contracts in cold, making it easy for small thefts (200L - 500L) to be hidden within natural volume fluctuations.
* **Geofence Blind Spots:** Standard GPS tracking shows where a truck is, but not the integrity of the cargo at that specific coordinate.
* **Delayed Auditing:** Discrepancies are usually found days later during manual dip-stick measurements at the destination, making forensic recovery impossible.

---

## The Solution: Digital Forensic Synchronization
This project solves the "Invisible Leak" by creating a unified **Command Center** that integrates three layers of intelligence:

1.  Corridor Intelligence (Geofencing): Uses high-resolution satellite mapping to track assets along the Houston I-10 corridor. It triggers red-zone alerts the moment a valve is opened outside an authorized depot.
2.  Volumetric Thermal Correlation: A dual-axis forensic engine that plots Net Volume vs. Temperature. By visualizing these together, the system proves that the -248.53 L loss was a physical extraction (sudden drop) rather than thermal contraction (gradual curve).
3.  Automated Forensic Reporting: Generates instant executive summaries and incident reports with clickable GPS links to the exact coordinates of the breach for immediate security dispatch.

---

## Tech Stack
* Frontend: `Streamlit` (High-density enterprise dashboard)
* Geospatial: `Folium` & `Esri World Imagery` (Satellite-natural mapping)
* Data Science: `Pandas` (Standardized ASTM D1250 volumetric logic)
* Visualization: `Plotly Graph Objects` (Dual-axis forensic charting)
* Environment: `Python 3.9+`

---

## Recommendations for Deployment
Based on the forensic findings of the **SHL-TX-9921** mission, I recommend the following:
* **Hardened Geofencing: Implement "Corridor Locking." Any stationary stop longer than 5 minutes outside an authorized Shell Depot should trigger an automated "Alert Status" to the driver’s cabin.
* Smart Valve Integration: Upgrade manual valves to IoT-enabled electronic seals that require a digital handshake from the terminal to unlock.
* Predictive Risk Modeling: Use the historical data from this dashboard to identify "High-Risk Shoulders" on the I-10 highway where siphoning events are statistically most likely to occur.

---
