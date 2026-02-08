# 🚗 Smart Vehicle Rental System (ITS Integrated)

> **Vehicle Rental System Integrated with Intelligent Transportation Systems (ITS)**
>
> *Developed using Agile/Scrum methodology*

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Framework-Django-092E20.svg?style=flat&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)
![Leaflet](https://img.shields.io/badge/Map-LeafletJS-199900.svg?style=flat&logo=leaflet&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat&logo=postgresql&logoColor=white)

---

## 📖 Overview
**The Smart Vehicle Rental System** addresses passenger transportation challenges by integrating Intelligent Transportation System (ITS) modules.
The system not only manages vehicle rentals but also optimizes operations through geospatial data (GIS) and dynamic pricing algorithms.

---

## 🌟 Key Features

### 1. 🌏 ITS Module & Core Intelligence
- **Real-time GIS Mapping (Leaflet):** Visualizes vehicle locations and parking-lot heatmaps on digital maps using the Leaflet API.
- **Smart Routing:** Automatically calculates optimal routes (distance/time) between pick-up and drop-off points.
- **Dynamic Pricing Algorithm:** Real-time flexible pricing model:
    - Time-based: Automatic price increase during peak hours and weekends.
    - Demand-based: Price adjustment based on fleet occupancy rate.
- **Fleet Lifecycle:** Vehicle state workflow: `Available` 🟢 → `Booked` 🟡 → `In Operation` 🔵 → `Maintenance` 🔴

### 2. 👤 User Portal
- **KYC & Account:** Registration/Login with driver’s license image upload for identity verification.
- **Advanced Search:** Multi-criteria vehicle search (Vehicle type, Price range, Nearest location on map).
- **Booking Flow:** Intuitive booking process with simulated payment gateway integration.
- **Feedback System:** Post-trip vehicle and service rating system (star voting) to improve recommendation algorithms.

### 3. 👤 Admin Dashboard
- **Fleet Management (CRUD):** Create, update, delete vehicle data, images, and maintenance records.
- **Order Processing:** Approval or cancellation workflow for customer booking requests.
- **Data Analytics:** 
    - Rental frequency charts
    - Real-time revenue forecasting

---

## 🛠 Technology Stack

| Domain | Technology | Role & Application |
| :--- | :--- | :--- |
| **Core/Backend** | ![Python](https://img.shields.io/badge/-Python-black?logo=python) ![Django](https://img.shields.io/badge/-Django-black?logo=django) | Core processing, dynamic pricing algorithms, and fleet coordination logic. |
| **Frontend** | ![HTML5](https://img.shields.io/badge/-HTML5-black?logo=html5) ![Sass](https://img.shields.io/badge/-Sass-black?logo=sass) | User interface, interactive dashboards, and map visualization. |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-black?logo=postgresql) | Relational data storage: fleet, customers, and route history. |
| **Mapping & GIS** | ![Leaflet](https://img.shields.io/badge/-LeafletJS-black?logo=leaflet) | **Core Feature:** digital mapping, vehicle positioning (markers), and route drawing (polylines). |
| **DevOps** | ![Docker](https://img.shields.io/badge/-Docker-black?logo=docker) | Application containerization and environment consistency. |

---

## 🚀 Guide

### 1. Clone the repository
```bash
git clone https://github.com/Minhhieu3012/its-vehicle-rental-system.git
cd vehicle-rental-its
```
### 2. Build & Run (Local)

```bash
docker-compose up -d --build
```
- User Site: http://localhost:8000

- Admin Dashboard: http://localhost:8000/admin

---

## 📝 Note
- This project is a course assignment for Intelligent Transportation Systems (ITS).
- All vehicle data and transactions are simulated for academic and demonstration purposes only.
