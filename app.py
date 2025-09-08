# app.py
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
from functools import lru_cache

# ============================
# APP CONFIGURATION & DATA
# ============================

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
                title='Europe Development Visualizer')
server = app.server

# European countries
COUNTRIES = {
    'Albania': 'ALB', 'Austria': 'AUT', 'Belarus': 'BLR', 'Belgium': 'BEL',
    'Bosnia and Herzegovina': 'BIH', 'Bulgaria': 'BGR', 'Croatia': 'HRV', 'Cyprus': 'CYP',
    'Czech Republic': 'CZE', 'Denmark': 'DNK', 'Estonia': 'EST', 'Finland': 'FIN',
    'France': 'FRA', 'Germany': 'DEU', 'Greece': 'GRC', 'Hungary': 'HUN',
    'Iceland': 'ISL', 'Ireland': 'IRL', 'Italy': 'ITA', 'Latvia': 'LVA',
    'Lithuania': 'LTU', 'Luxembourg': 'LUX', 'Malta': 'MLT', 'Moldova': 'MDA',
    'Montenegro': 'MNE', 'Netherlands': 'NLD', 'North Macedonia': 'MKD', 'Norway': 'NOR',
    'Poland': 'POL', 'Portugal': 'PRT', 'Romania': 'ROU', 'Russia': 'RUS',
    'Serbia': 'SRB', 'Slovakia': 'SVK', 'Slovenia': 'SVN', 'Spain': 'ESP',
    'Sweden': 'SWE', 'Switzerland': 'CHE', 'Turkey': 'TUR', 'Ukraine': 'UKR',
    'United Kingdom': 'GBR'
}

# Indicators
INDICATORS = {
    'GDP per capita (US$)': 'NY.GDP.PCAP.CD',
    'Annual Inflation Rate (%)': 'FP.CPI.TOTL.ZG',
    'Unemployment Rate (%)': 'SL.UEM.TOTL.ZS',
    'Life Expectancy (years)': 'SP.DYN.LE00.IN',
    'Health Expenditure per capita (US$)': 'SH.XPD.CHEX.PC.CD',
    'Access to Electricity (% of population)': 'EG.ELC.ACCS.ZS',
    'CO2 Emissions (metric tons per capita)': 'EN.ATM.CO2E.PC',
    'Internet Users (% of population)': 'IT.NET.USER.ZS'
}

DEFAULT_INDICATOR = 'GDP per capita (US$)'
DEFAULT_COUNTRIES = ['Germany', 'France', 'United Kingdom', 'Spain', 'Italy']
START_YEAR, END_YEAR = 2000, 2024

@lru_cache(maxsize=64)
def fetch_worldbank_page(countries_iso: str, indicator: str, date_range: str, page: int = 1, per_page: int = 2000):
    """Cached function to make a request to the World Bank API."""
    url = f"https://api.worldbank.org/v2/country/{countries_iso}/indicator/{indicator}?date={date_range}&format=json&per_page={per_page}&page={page}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def get_worldbank_data(countries_dict, indicators_dict, start_year=START_YEAR, end_year=END_YEAR):
    """Fetches and processes data for all indicators, handling pagination."""
    dfs = []
    countries_iso = ";".join(countries_dict.values())
    date_range = f"{start_year}:{end_year}"

    for indicator_name, indicator_code in indicators_dict.items():
        try:
            first_page = fetch_worldbank_page(countries_iso, indicator_code, date_range, page=1)
            if not isinstance(first_page, list) or len(first_page) < 2 or not first_page[1]:
                continue
            
            total_pages = int(first_page[0].get('pages', 1))
            all_rows = first_page[1]
            
            for p in range(2, total_pages + 1):
                json_data = fetch_worldbank_page(countries_iso, indicator_code, date_range, page=p)
                if len(json_data) > 1 and json_data[1]:
                    all_rows.extend(json_data[1])

            df = pd.DataFrame(all_rows)
            if df.empty:
                continue
                
            df_clean = df[['countryiso3code', 'country', 'date', 'value']].copy()
            df_clean.rename(columns={'countryiso3code': 'ISO3Code', 'country': 'Country', 'date': 'Year', 'value': 'Value'}, inplace=True)
            df_clean['Indicator'] = indicator_name
            
            # Map ISO3 code back to the standardized country name from our dictionary
            reverse_country_map = {v: k for k, v in countries_dict.items()}
            df_clean['Country'] = df_clean['ISO3Code'].map(reverse_country_map).fillna(df_clean['Country'])
            
            # Convert to correct data types
            df_clean['Year'] = pd.to_numeric(df_clean['Year'], errors='coerce')
            df_clean['Value'] = pd.to_numeric(df_clean['Value'], errors='coerce')
            df_clean.dropna(subset=['Value', 'Year'], inplace=True)
            dfs.append(df_clean)
        except Exception as e:
            print(f"Error with {indicator_name}: {e}")
            continue

    if dfs:
        return pd.concat(dfs, ignore_index=True).sort_values(['Indicator', 'Country', 'Year'])
    return pd.DataFrame(columns=['ISO3Code','Country','Year','Value','Indicator'])

# Load data on startup
DF_ALL = get_worldbank_data(COUNTRIES, INDICATORS)

def format_value(indicator_name, v):
    """Formats a numeric value based on the indicator type."""
    if pd.isna(v):
        return 'N/A'
    if '%' in indicator_name:
        return f"{v:,.2f}%"
    if 'US$' in indicator_name:
        return f"US$ {v:,.2f}"
    return f"{v:,.2f}"

# ============================
# LAYOUT
# ============================
brand = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.I(className='bi bi-bar-chart-line-fill fs-3 me-2')),
            dbc.Col(html.Div([
                html.H5('Europe Development Visualizer', className='mb-0 text-white'),
                html.Small('Data from the World Bank API', className='text-muted')
            ])),
        ], align='center', className='g-2'),
    ], fluid=True),
    color='dark', dark=True, className='shadow-sm sticky-top'
)

kpis_layout = dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('Latest Value', className='kpi-title'),
        html.H3(id='kpi-value', className='kpi-number'),
        html.Span(id='kpi-year', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('vs. Previous Year', className='kpi-title'),
        html.H3(id='kpi-var', className='kpi-number'),
        html.Span(id='kpi-var-abs', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('CAGR in Range', className='kpi-title'),
        html.H3(id='kpi-cagr', className='kpi-number'),
        html.Span(id='kpi-range', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('Europe Rank (Latest Year)', className='kpi-title'),
        html.H3(id='kpi-rank', className='kpi-number'),
        html.Span(id='kpi-top', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
], className='g-2')

footer_layout = html.Div([
    html.Hr(className="my-3"),
    html.P("Developed by: Ricardo Urdaneta", className="text-muted small"),
    dbc.Row([
        dbc.Col(
            html.A(dbc.Button([html.I(className="bi bi-github me-2"), "GitHub"],
                              color="secondary", outline=True, className="w-100"),
                   href="https://github.com/Ricardouchub", target="_blank")
        , width=6),
        dbc.Col(
            html.A(dbc.Button([html.I(className="bi bi-linkedin me-2"), "LinkedIn"],
                              color="secondary", outline=True, className="w-100"),
                   href="https://www.linkedin.com/in/ricardourdanetacastro", target="_blank")
        , width=6)
    ])
], className="mt-auto")

sidebar = dbc.Card(
    dbc.CardBody([
        html.Div([
            html.P("Use the filters to explore the data.", className="small"),
            html.P("Note: Some countries may lack data for all years or indicators.", className="small text-muted")
        ], className="mb-3"),
        html.Hr(className="my-2"),
        
        html.Div([
            html.Label('Indicator', className='form-label fw-semibold'),
            dcc.Dropdown(id='dd-indicator', options=[{'label': k, 'value': k} for k in INDICATORS.keys()], value=DEFAULT_INDICATOR, clearable=False)
        ], className='mb-3'),
        html.Div([
            html.Label('Countries (multi-select)', className='form-label fw-semibold'),
            dcc.Dropdown(id='dd-countries', options=[{'label': k, 'value': k} for k in COUNTRIES.keys()], value=DEFAULT_COUNTRIES, multi=True)
        ], className='mb-3'),
        html.Div([
            html.Label('Year Range', className='form-label fw-semibold'),
            dcc.RangeSlider(id='rs-years', min=int(DF_ALL['Year'].min() if not DF_ALL.empty else START_YEAR),
                            max=int(DF_ALL['Year'].max() if not DF_ALL.empty else END_YEAR),
                            value=[max(START_YEAR, int(DF_ALL['Year'].min() if not DF_ALL.empty else START_YEAR)),
                                   int(DF_ALL['Year'].max() if not DF_ALL.empty else END_YEAR)],
                            step=1, allowCross=False, marks=None, tooltip={'placement': 'bottom', 'always_visible': True})
        ], className='mb-3'),
        html.Div([
            html.Label('Country for KPIs', className='form-label fw-semibold'),
            dcc.Dropdown(id='dd-kpi-country', options=[{'label': k, 'value': k} for k in COUNTRIES.keys()], value='Germany', clearable=False)
        ]),
        
        html.Hr(className="my-4"),
        kpis_layout,
        footer_layout
    ], className="d-flex flex-column h-100")
, className='shadow-sm h-100')

line_chart = dbc.Card(dbc.CardBody([
    html.H5('Time Series Evolution', className='card-title mb-3'),
    dcc.Loading(dcc.Graph(id='fig-line', config={'displaylogo': False}), type='dot')
]), className='shadow-sm')

bar_chart = dbc.Card(dbc.CardBody([
    html.H5('Cross-Country Comparison (Latest Year)', className='card-title mb-3'),
    dcc.Loading(dcc.Graph(id='fig-bar', config={'displaylogo': False}), type='dot')
]), className='shadow-sm')

map_chart = dbc.Card(dbc.CardBody([
    html.H5('Choropleth Map (Latest Year in Range)', className='card-title mb-3'),
    dcc.Loading(dcc.Graph(id='fig-map', config={'displaylogo': False}), type='dot')
]), className='shadow-sm')

app.layout = dbc.Container([
    brand,
    dbc.Row([
        dbc.Col(sidebar, md=3, lg=2, className='mb-3'),
        dbc.Col([
            dbc.Row([dbc.Col(line_chart, lg=12, className='mb-3')]),
            dbc.Row([
                dbc.Col(bar_chart, lg=6, className='mb-3'),
                dbc.Col(map_chart, lg=6, className='mb-3'),
            ]),
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Button("Download CSV", id="btn-download", n_clicks=0, color="secondary"),
                        dcc.Download(id='download-data')
                    ], className="d-flex justify-content-end mt-3"
                )
            ])
        ], md=9, lg=10)
    ], className='mt-3')
], fluid=True)

# ============================
# CALLBACKS
# ============================

@app.callback(
    Output('download-data', 'data'),
    Input('btn-download', 'n_clicks'),
    State('dd-indicator', 'value'),
    prevent_initial_call=True
)
def download_csv(n_clicks, indicator):
    """Allows the user to download the selected indicator's data as a CSV file."""
    df = DF_ALL[DF_ALL['Indicator'] == indicator].copy()
    return dcc.send_data_frame(df.to_csv, f"europe_{indicator.replace(' ', '_')}.csv", index=False)

def filter_and_transform_data(indicator, selected_countries, start_year, end_year):
    """Helper function to filter the main DataFrame."""
    df = DF_ALL[(DF_ALL['Indicator'] == indicator) & (DF_ALL['Country'].isin(selected_countries)) & (DF_ALL['Year'].between(start_year, end_year))].copy()
    return df

@app.callback(
    [Output('kpi-value', 'children'), Output('kpi-year', 'children'),
     Output('kpi-var', 'children'), Output('kpi-var-abs', 'children'),
     Output('kpi-cagr', 'children'), Output('kpi-range', 'children'),
     Output('kpi-rank', 'children'), Output('kpi-top', 'children')],
    [Input('dd-indicator', 'value'), Input('dd-kpi-country', 'value'), Input('rs-years', 'value')]
)
def update_kpis(indicator, kpi_country, year_range):
    """Updates the four KPI cards."""
    y0, y1 = int(year_range[0]), int(year_range[1])
    df_indicator = DF_ALL[(DF_ALL['Indicator'] == indicator) & (DF_ALL['Country'] == kpi_country) & (DF_ALL['Year'].between(y0, y1))]
    if df_indicator.empty:
        return ['N/A'] * 8

    df_indicator = df_indicator.sort_values('Year')
    last_row = df_indicator.iloc[-1]
    last_val, last_year = last_row['Value'], int(last_row['Year'])
    
    if len(df_indicator) >= 2:
        prev_val = df_indicator.iloc[-2]['Value']
        var_pct = ((last_val - prev_val) / prev_val) * 100 if prev_val != 0 and pd.notna(prev_val) else np.nan
        var_abs = last_val - prev_val
    else:
        var_pct, var_abs = np.nan, np.nan

    first_row = df_indicator.iloc[0]
    first_val, first_year = first_row['Value'], int(first_row['Year'])
    num_years = max(1, last_year - first_year)
    cagr = ((last_val / first_val) ** (1 / num_years) - 1) * 100 if first_val != 0 and pd.notna(first_val) else np.nan

    df_last_year = DF_ALL[(DF_ALL['Indicator'] == indicator) & (DF_ALL['Year'] == last_year)].dropna(subset=['Value'])
    if df_last_year.empty:
        rank_text, top_text = 'N/A', ''
    else:
        df_last_year = df_last_year.sort_values('Value', ascending=False).reset_index()
        df_last_year['rank'] = df_last_year.index + 1
        row = df_last_year[df_last_year['Country'] == kpi_country]
        rank_text = f"#{int(row['rank'].iloc[0])} of {len(df_last_year)}" if not row.empty else 'N/A'
        top_text = f"Year {last_year}"

    return (
        format_value(indicator, last_val), f"Year {last_year}",
        (f"{var_pct:,.2f}%" if pd.notna(var_pct) else 'N/A'),
        (f"Δ {format_value(indicator, var_abs)}" if pd.notna(var_abs) else 'Δ N/A'),
        (f"{cagr:,.2f}%" if pd.notna(cagr) else 'N/A'),
        f"{y0}–{y1}", rank_text, top_text
    )

@app.callback(
    Output('fig-line', 'figure'),
    [Input('dd-indicator', 'value'), Input('dd-countries', 'value'), Input('rs-years', 'value')]
)
def update_line_chart(indicator, selected_countries, year_range):
    """Updates the line chart."""
    y0, y1 = int(year_range[0]), int(year_range[1])
    df = filter_and_transform_data(indicator, selected_countries, y0, y1)
    if df.empty:
        return go.Figure().update_layout(title_text='No data available for current selection', template='plotly_dark')

    title = f"Evolution of {indicator} ({y0}–{y1})"
    y_label = indicator

    fig = px.line(df, x='Year', y='Value', color='Country', markers=True, labels={'Year': 'Year', 'Value': y_label}, title=title, template='plotly_dark')
    fig.update_layout(legend_title_text='Country', hovermode='x unified', transition_duration=400)
    fig.update_traces(mode='lines+markers')
    return fig

@app.callback(
    Output('fig-bar', 'figure'),
    [Input('dd-indicator', 'value'), Input('rs-years', 'value')]
)
def update_bar_chart(indicator, year_range):
    """Updates the bar chart."""
    y0, y1 = int(year_range[0]), int(year_range[1])
    df = DF_ALL[(DF_ALL['Indicator'] == indicator) & (DF_ALL['Year'].between(y0, y1))].copy()
    if df.empty:
        return go.Figure().update_layout(title_text='No data available for current selection', template='plotly_dark')

    idx = df.sort_values('Year').groupby('Country')['Value'].idxmax()
    df_last = df.loc[idx].dropna(subset=['Value']).sort_values('Value', ascending=False)
    
    if df_last.empty:
        return go.Figure().update_layout(title_text='No data available for current selection', template='plotly_dark')

    fig = px.bar(df_last, x='Country', y='Value', text='Value', labels={'Value': indicator, 'Country': 'Country'}, template='plotly_dark')
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, uniformtext_minsize=8, uniformtext_mode='hide', margin=dict(t=40, r=10, l=10, b=40))
    return fig

@app.callback(
    Output('fig-map', 'figure'),
    [Input('dd-indicator', 'value'), Input('rs-years', 'value')]
)
def update_map_chart(indicator, year_range):
    """Updates the choropleth map."""
    y0, y1 = int(year_range[0]), int(year_range[1])
    df = DF_ALL[(DF_ALL['Indicator'] == indicator) & (DF_ALL['Year'].between(y0, y1))].copy()
    if df.empty:
        return go.Figure().update_layout(title_text='No data available for current selection', template='plotly_dark', geo=dict(visible=False))

    last_year_in_data = int(df['Year'].max())
    df_last = df[df['Year'] == last_year_in_data]

    fig = px.choropleth(
        df_last, locations='ISO3Code', color='Value', hover_name='Country',
        color_continuous_scale='Viridis', locationmode='ISO-3', labels={'Value': indicator},
        title=f"{indicator} — {last_year_in_data}", scope='europe' 
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(t=50, r=0, l=0, b=0), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', geo_bgcolor='rgba(0,0,0,0)')
    return fig

# ============================
# RUN APP
# ============================
if __name__ == '__main__':
    app.run(debug=True)

# ============================
# Developer: Ricardo Urdaneta
# ============================
