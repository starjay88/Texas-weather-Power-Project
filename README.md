# Texas ERCOT Grid & Weather Open Data Portal

## Dashboard Link:
https://starjay88.github.io/Texas-weather-Power-Project/

## Project Overview
A real-time ETL pipeline and open data monitoring dashboard designed to analyze the correlation between Texas surface temperatures and ERCOT (Electric Reliability Council of Texas) power grid demand. This system proactively identifies potential grid stress and extreme weather events to forecast power outage risks.

## Key Features
* **Predictive Grid Stress Alerts:** Analyzes forecast data to trigger automated warnings for extreme temperatures (Above 105°F / Below 25°F) and critical grid loads (Approaching 85,000 MWh).
* **Automated ETL Pipeline:** Utilizes GitHub Actions (Cron) to extract, transform, and load time-series data continuously without manual server maintenance.
* **RESTful API Service:** Provides a fully documented backend API for developers to access the processed dataset.
* **Open Data Portal:** Features an interactive data visualization dashboard, a comprehensive data dictionary, and a raw CSV export function for offline analysis.

## System Architecture
1. **Extract:** Fetches real-time weather and power data from the U.S. National Weather Service (NWS) and the Energy Information Administration (EIA) APIs.
2. **Transform:** Cleanses raw data, normalizes timezones (UTC to Texas CT), and merges datasets seamlessly using Python (Pandas).
3. **Load:** Stores the processed time-series data securely in a Supabase (PostgreSQL) database.
4. **Serve:** Exposes the data through a FastAPI application deployed on Render cloud infrastructure.
5. **Present:** Renders responsive and interactive visualizations via GitHub Pages using Chart.js.

## Tech Stack
* **Backend & Data Processing:** Python, FastAPI, Pandas
* **Database:** Supabase (PostgreSQL)
* **Frontend:** HTML5, CSS3, JavaScript (Chart.js)
* **Infrastructure & CI/CD:** GitHub Actions, Render, GitHub Pages
* **External APIs:** NWS API, U.S. EIA API

## API Documentation
The backend exposes RESTful endpoints for the synchronized grid and weather dataset. Detailed API specifications and interactive testing are available via Swagger UI.

* **Base URL:** `https://texas-weather-power-project.onrender.com`
* **Swagger UI / Docs:** `https://texas-weather-power-project.onrender.com/docs`
* **Main Endpoint:** `GET /api/forecast`

## How to Run Locally

1. **Clone the repository**
   ```bash
   git clone [https://github.com/starjay88/Texas-weather-Power-Project.git](https://github.com/starjay88/Texas-weather-Power-Project.git)
   cd Texas-weather-Power-Project
