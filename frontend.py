import pandas as pd
from datetime import datetime as dt, date, time
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash.dcc import Download

import sys
import os
sys.path.append(os.path.dirname(__file__))
import dataCollector as dc
import plotly_chart_formatting as pcf

#-------------------------- DATA AND PLOTTING
nlc = dc.NetLiquidityCalculation(date(2022,5,1))
df = nlc.updater(tracker="spx")

namings = {
    "SPX": "S&P 500",
    "WSC": "Wilshire Small Cap Total Index",
    "WMC": "Wilshire Mid Cap Total Index",
    "WLC": "Wilshire Large Cap Total Index",
    "FV": "Fair Value",
    "HI": "Upper Bound",
    "LO": "Lower Bound",
}




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
            ], width=5, align="center", style={"text-align": "right"}),
            dbc.Col([
                ThemeSwitchAIO(
                    aio_id="theme", themes=[dbc.themes.CYBORG, dbc.themes.COSMO]
                )
            ], width=1, align="center")

        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dbc.RadioItems(
                    id="main_chart_radios",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "S&P 500", "value": "spx"},
                        {"label": "Small Caps", "value": "wsc"},
                        {"label": "Mid Caps", "value": "wmc"},
                        {"label": "Large Caps", "value": "wlc"},
                    ],
                    value="spx"
                )
            ], width={"size": 8, "offset": 4}, className="radio-group")
        ], justify="center", style={"marginTop": 20, "marginBottom": 10}),
        dbc.Row([
            dbc.Col([
                dbc.Button("Download Data", id="download_data_button"),
                dcc.Download(id="download_df")
            ], width={"size":4, "offset": 2}),
        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="main_figure")
            ], width=10),
        ], justify="center", style={"marginTop": 20}), # MAIN CHART ROW
        dbc.Row([
            dbc.Row([
                dbc.Col([
                    dbc.RadioItems(
                        id="side_chart_radios",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                        options=[
                            {"label": "WALCL", "value": "walcl"},
                            {"label": "TGA", "value": "tga"},
                            {"label": "RRP", "value": "rrp"},
                            {"label": "REM", "value": "rem"},
                        ],
                        value="walcl"
                    )
                ], width={"size": 4, "offset": 2}, className="radio-group")
            ], justify="center", style={"marginTop": 20, "marginBottom": 10}),
            dbc.Col([
                dcc.Graph(id="side_figure")
            ], width=10),
        ], justify="center"), # SUB CHART ROW
    ], justify="center"),
    dcc.Store(data=df.to_dict("records"), id="df_store")
])

@app.callback(
    Output("main_figure", "figure"),
    Output("side_figure", "figure"),
    Output("df_store", "data"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("side_chart_radios", "value"),
    Input("main_chart_radios", "value"),
    State("side_figure", "figure"),
    State("main_figure", "figure"),
    State("df_store", "data"), ## To pass through the same values if no change
)
def update_graph_theme(toggle, side_chart_radios, main_chart_radios, existing_side_fig, existing_main_fig, df_store):
    template = "cyborg" if toggle else "cosmo"
    def side_fig_creator():
        data_dict = {
            "walcl": nlc.walcl,
            "tga": nlc.tga,
            "rrp": nlc.rrp,
            "rem": nlc.rem,
        }
        df = data_dict[side_chart_radios].dropna(how="any")
        side_fig = go.Figure()
        side_fig = side_fig.add_trace(go.Scatter(x=df.index, y=df[df.columns[0]]))
        side_fig = side_fig.update_layout(pcf.layout_dict,template=template, title=dict(text=side_chart_radios.upper(), x=0.5))
        return side_fig

    def main_fig_creator():
        new_df = nlc.updater(main_chart_radios)
        df_store = new_df.to_dict("records")
        top_fig = go.Figure()
        top_fig.add_traces(data=[
            go.Scatter(x=new_df.index, y=new_df[trace], name=namings[trace]) for trace in
            [main_chart_radios.upper(), "LO", "FV", "HI"]
        ]).update_layout(pcf.layout_dict, template=template)
        return top_fig, df_store

    if ctx.triggered_id == "side_chart_radios" or not ctx.triggered_id:
        side_fig = side_fig_creator()
        if not ctx.triggered_id:
            top_fig, df_store = main_fig_creator()
        else:
            top_fig = existing_main_fig
    elif ctx.triggered_id == "main_chart_radios":
        top_fig, df_store = main_fig_creator()
        side_fig = existing_side_fig
    else:
        top_fig = existing_main_fig.update_layout(template=template)
        side_fig = go.Figure(existing_side_fig).update_layout(template=template)
    return top_fig, side_fig, df_store

if __name__ == '__main__':
    app.run(debug=True)
