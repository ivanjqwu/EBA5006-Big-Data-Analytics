import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import plotly.express as px

data = pd.read_csv("data.csv", encoding="UTF-8")
data["Time"] = pd.to_datetime(data["Time"], format="%H:%M:%S").dt.time
data.sort_values("Time", inplace=True)


def _create_fig():
    data = pd.read_csv("data.csv", encoding="UTF-8")
    data["Time"] = pd.to_datetime(data["Time"], format="%H:%M:%S").dt.time
    data.sort_values("Time", inplace=True)
    fig1 = go.Figure(
        data=px.line(x=data["Time"],
            y=data["Total Number of Rate"],
            markers=True)
    )
    fig1.update_layout(
        title="Real-time Monitor of Number of Rates",
        xaxis_title="time",
        yaxis_title="Total Number Of Rates",
        colorway=["#17B897"],
        height=500,
        width=1000,
        title_font_family="Old Standard TT",
    )
    return fig1


def _create_fig1():
    data = pd.read_csv("data.csv", encoding="UTF-8")
    data["Time"] = pd.to_datetime(data["Time"], format="%H:%M:%S").dt.time
    data.sort_values("Time", inplace=True)
    filtered_data = data.dropna()
    fig2 = go.Figure(
        data=go.Bar(
            x=["one", "two", "three", "four", "five"],
            y=filtered_data.iloc[-1, 2:7],
            # marker="True"
        )
    )
    fig2.update_layout(
        title="Distribution of Rates",
        xaxis_title="Level of Rate",
        yaxis_title="Number of Rates",
        colorway=["#E12D39"],
        height=500,
        width=1000,
        title_font_family="Old Standard TT"
    )
    return fig2


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Avocado Analytics: Understand Your Avocados!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥑", className="header-emoji"),
                html.H1(
                    children="Game Traffic Monitoring", className="header-title"
                ),
                html.P(
                    children="Real-time monitor for "
                             "the fluctuation of game popularity ",
                    className="header-description",
                ),
            ],
            className="header",
        ),

        html.Div(
            children=[
                dcc.Graph(
                    id='g1',
                    figure=_create_fig()
                ),
                dcc.Graph(
                    id='g2',
                    figure=_create_fig1()
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=1 * 1000,  # in milliseconds
                    n_intervals=0
                )
            ],
            className="wrapper",
        ),
    ]
)


@app.callback([Output('g1', 'figure'),
               Output("g2", "figure")],
              [Input('interval-component', 'n_intervals'),
               ],
              )
def refresh_data(n_clicks):
    return _create_fig(), _create_fig1()


if __name__ == "__main__":
    app.run_server(debug=True)
