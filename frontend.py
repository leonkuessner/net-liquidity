import pandas as pd
from datetime import datetime as dt, date, time
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO

import sys
import os
sys.path.append(os.path.dirname(__file__))
import dataCollector as dc
import plotly_chart_formatting as pcf

#-------------------------- DATA AND PLOTTING
df = dc.NetLiquidityCalculation((dt.now() - relativedelta(months=15)).date()).calculate_net_liquidity()

namings = {
    "SPX": "S&P 500",
    "SPX_FV": "Fair Value",
    "SPX_HI": "Upper Bound",
    "SPX_LO": "Lower Bound",
}

main_fig = go.Figure()
main_fig.add_traces(data=[
    go.Scatter(x = df.index, y = df[trace], name=namings[trace]) for trace in ["SPX", "SPX_LO", "SPX_FV", "SPX_HI"]
]).update_layout(pcf.layout_dict)


#-------------------------- DASH
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = html.Div([
    dbc.Row([
        dbc.Row([
            dbc.Col(width=1),
            dbc.Col([
                html.H3("Net Liquidity")
            ], width=5),
            dbc.Col([
                html.H5("Leon Kuessner")
            ], width=3, align="center", style={"text-align": "left"}),
            dbc.Col([
                html.P("Inspiration:"),
                dcc.Link("Dharmatrade", href="https://twitter.com/dharmatrade")
            ], width=2, align="center", style={"text-align": "center"}),
            dbc.Col([
                ThemeSwitchAIO(
                    aio_id="theme", themes=[dbc.themes.CYBORG, dbc.themes.COSMO]
                )
            ], width=1, align="center")

        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="main_figure")
            ], width=10),
        ], justify="center"), # MAIN CHART ROW
        dbc.Row([
            dbc.Col([
                dbc.Button("Download Data", id="download_data_button")
            ], width=3),
        ], justify="center"),
        dbc.Row([
            dbc.Col([

            ], width=2),
            dbc.Col([

            ], width=2),
            dbc.Col([

            ], width=2),
            dbc.Col([

            ], width=2),
        ], justify="center"), # SUB CHART ROW
    ], justify="center"),
])

@app.callback(
    Output("main_figure", "figure"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_graph_theme(toggle):
    template = "cyborg" if toggle else "cosmo"
    # return px.line(df, x="date", y="GOOG", template=template)
    return main_fig.update_layout(template=template)

if __name__ == '__main__':
    app.run(debug=True)
