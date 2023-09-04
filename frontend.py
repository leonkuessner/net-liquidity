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
nlc = dc.NetLiquidityCalculation((dt.now() - relativedelta(months=15)).date())
df = nlc.calculate_net_liquidity()

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
            ], width=5, align="center", style={"text-align": "right"}),
            # dbc.Col([
            #     html.P("Inspiration:"),
            #     dcc.Link("Dharmatrade", href="https://twitter.com/dharmatrade")
            # ], width=2, align="center", style={"text-align": "center"}),
            dbc.Col([
                ThemeSwitchAIO(
                    aio_id="theme", themes=[dbc.themes.CYBORG, dbc.themes.COSMO]
                )
            ], width=1, align="center")

        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dbc.Button("Download Data", id="download_data_button")
            ], width=3),
        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="main_figure")
            ], width=10),
        ], justify="center"), # MAIN CHART ROW
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
                ], width=5, className="radio-group")
            ], justify="center"),
            dbc.Col([
                dcc.Graph(id="side_figure")
            ], width=10),
        ], justify="center"), # SUB CHART ROW
    ], justify="center"),
    # dcc.Store(id="side_figure_store")
])

# @app.callback(
#     Output("side_figure", "figure"),
#     Input("side_chart_radios", "value"),
#     State(ThemeSwitchAIO.ids.switch("theme"), "value"),
# )
# def create_sub_chart(radio_val, toggle):
#     template = "cyborg" if toggle else "cosmo"
#     data_dict = {
#         "walcl": nlc.walcl,
#         "tga": nlc.tga,
#         "rrp": nlc.rrp,
#         "rem": nlc.rem,
#     }
#     df = data_dict[radio_val].dropna(how="any")
#     return side_fig.add_trace(go.Scatter(x=df.index, y=df[df.columns[0]])).update_layout(template=template)
#
# @app.callback(
#     Output("main_figure", "figure"),
#     Output("side_figure", "figure"),
#     Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
#     State("side_figure", "figure")
# )
# def update_graph_theme(toggle, side_fig):
#     template = "cyborg" if toggle else "cosmo"
#     # return px.line(df, x="date", y="GOOG", template=template)
#     top_fig = main_fig.update_layout(template=template)
#     sub_fig = side_fig.update_layout(template=template)
#     return top_fig, sub_fig
@app.callback(
    Output("main_figure", "figure"),
    Output("side_figure", "figure"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("side_chart_radios", "value"),
    State("side_figure", "figure")
)
def update_graph_theme(toggle, side_chart_radios, existing_side_fig):
    template = "cyborg" if toggle else "cosmo"
    if ctx.triggered_id == "side_chart_radios" or not ctx.triggered_id:
        data_dict = {
            "walcl": nlc.walcl,
            "tga": nlc.tga,
            "rrp": nlc.rrp,
            "rem": nlc.rem,
        }
        df = data_dict[side_chart_radios].dropna(how="any")
        side_fig = go.Figure()
        sub_fig = side_fig.add_trace(go.Scatter(x=df.index, y=df[df.columns[0]]))
        sub_fig = sub_fig.update_layout(pcf.layout_dict,template=template, title=dict(text=side_chart_radios.upper(), x=0.5))
        if not ctx.triggered_id:
            top_fig = main_fig.update_layout(template=template)
        else:
            top_fig = main_fig
    else:
        top_fig = main_fig.update_layout(template=template)
        sub_fig = go.Figure(existing_side_fig).update_layout(template=template)
    return top_fig, sub_fig

if __name__ == '__main__':
    app.run(debug=True)
