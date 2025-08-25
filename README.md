# Europe Development Visualizer

<p align="left">
  <img src="https://img.shields.io/badge/Project_Completed-%E2%9C%94-2ECC71?style=flat-square&logo=checkmarx&logoColor=white" alt="Project Completed"/>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/GeoPandas-Geolocation-2A7F62?style=flat-square&logo=geopandas&logoColor=white" alt="GeoPandas"/>
  <img src="https://img.shields.io/badge/Plotly-Interactive_Visualization-3F4F75?style=flat-square&logo=plotly&logoColor=white" alt="Plotly"/>
  <img src="https://img.shields.io/badge/Dash-Dashboard-119DFF?style=flat-square&logo=dash&logoColor=white" alt="Dash"/>
</p>

A web-based dashboard for exploring and comparing key development indicators across European nations, powered by live data from the World Bank API.

This project provides an interactive tool to analyze the economic and social landscape of Europe. The data is fetched in real-time, ensuring that the insights are always based on the most current information available.


<p align="center">
  <a href="https://europe-development-visualizer.onrender.com" target="_blank" rel="noopener noreferrer">
    <img width="455" height="502" alt="image" src="https://github.com/user-attachments/assets/3f1f0a65-4ffd-4f69-8ddc-105466efb5c7" />
  </a>
</p>



---

The application features a modern, dark-themed user interface, designed for intuitive data exploration. Users can track trends over time, benchmark performance between countries, and analyze specific metrics through a variety of dynamic charts.

## Features

* **Live Data:** Direct connection to the World Bank API ensures up-to-date information.
* **Interactive Controls:** Dynamically filter by indicator, select multiple countries, and adjust the time range for analysis with comprehensive visualizations:
    * **Line Chart:** Track the historical evolution of any indicator.
    * **Bar Chart:** Compare the latest available data point across different countries.
    * **Choropleth Map:** Visualize the geographical distribution of an indicator across the continent.
* **KPIs:** Get instant insights for a selected country, including its latest value, year-over-year change, compound annual growth rate (CAGR), and regional ranking.
* **Data Export:** Download the raw data for the selected indicator as a CSV file with a single click.

## Deployment

This application is deployed and publicly available via **Render**, a cloud platform for building and running web applications. The deployment is automated from the GitHub source code, using a Gunicorn server to ensure robust and scalable performance.

## Tools

* **Backend & Visualization:**
    * Dash: The core framework for building the web application.
    * Plotly Express: For creating interactive, high-quality charts.
    * Pandas: For data manipulation and processing.
    * Requests: For making HTTP requests to the World Bank API.
* **Frontend & Design:**
    * Dash Bootstrap Components: For responsive layouts and modern UI components.
    * Bootstrap Icons: For icons used throughout the interface.

## Dashboard Visualization

<img width="2530" height="1286" alt="image" src="https://github.com/user-attachments/assets/c5bf721a-5c62-4c85-b601-b18f32664c3d" />


## Author

**Ricardo Urdaneta**.

[**LinkedIn**](https://www.linkedin.com/in/ricardourdanetacastro)
