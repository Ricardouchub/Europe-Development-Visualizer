# Europe Development Visualizer

A web-based dashboard for exploring and comparing key development indicators across European nations, powered by live data from the World Bank API.

This project provides an interactive tool to analyze the economic and social landscape of Europe. The data is fetched in real-time, ensuring that the insights are always based on the most current information available.

### [**Dashboard**](https://your-europe-dashboard-url.onrender.com/)

![Placeholder Screenshot](https://placehold.co/764x385/060606/45b1e8?text=Europe+Dashboard+Screenshot)

---

The application features a modern, dark-themed user interface, designed for intuitive data exploration. Users can track trends over time, benchmark performance between countries, and analyze specific metrics through a variety of dynamic charts.

## Features

* **Live Data Integration:** Direct connection to the World Bank API ensures up-to-date information.
* **Interactive Controls:** Dynamically filter by indicator, select multiple countries, and adjust the time range for analysis.
* **Comprehensive Visualizations:**
    * **Line Chart:** Track the historical evolution of any indicator.
    * **Bar Chart:** Compare the latest available data point across different countries.
    * **Choropleth Map:** Visualize the geographical distribution of an indicator across the continent.
* **Detailed KPIs:** Get instant insights for a selected country, including its latest value, year-over-year change, compound annual growth rate (CAGR), and regional ranking.
* **Modern & Responsive Design:** A professional, dark interface built with Dash Bootstrap Components that adapts to any screen size.
* **Data Export:** Download the raw data for the selected indicator as a CSV file with a single click.

## Deployment

This application is deployed and publicly available via **Render**, a cloud platform for building and running web applications. The deployment is automated from the GitHub source code, using a Gunicorn server to ensure robust and scalable performance.

## 🛠️ Tech Stack

* **Backend & Visualization:**
    * [Dash](https://dash.plotly.com/): The core framework for building the web application.
    * [Plotly Express](https://plotly.com/python/plotly-express/): For creating interactive, high-quality charts.
    * [Pandas](https://pandas.pydata.org/): For data manipulation and processing.
    * [Requests](https://requests.readthedocs.io/en/latest/): For making HTTP requests to the World Bank API.
* **Frontend & Design:**
    * [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/): For responsive layouts and modern UI components.
    * [Bootstrap Icons](https://icons.getbootstrap.com/): For icons used throughout the interface.

## Author

Developed by **Ricardo Urdaneta**.

[**LinkedIn**](https://www.linkedin.com/in/ricardourdanetacastro)
