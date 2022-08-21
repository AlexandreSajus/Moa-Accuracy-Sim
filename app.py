"""
MOA Simulation

The goal of this app is to illustrate MOA accuracy of a rifle
using a simulation of shooting at a static target

The inputs are the following:
    - Distance to target in meters
    - Target diameter in meters
    - MOA of the rifle

The output is the hit probability and an output plot
with a circle representing the target and green and red dots representing
hits and misses.
"""

import math
import random
import numpy as np

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objects as go

simulation_shots = 10000
shots = 100

app = dash.Dash(__name__)
server = app.server
app.title = "MOA Accuracy Simulator"


def simulate_shots(distance, target_size, moa):
    """
    Simulates [simulation_shots] shots using input parameters
    and returns the hit probability and a plot of the shots on target

    Shots are simulated by considering that a shot will land at a random point
    with distance to center of target uniformly distributed between 0 and
    the dispersion cone of the rifle.
    """
    moa_radian = math.radians(moa / 60)
    target_radius = target_size / 2
    fig = go.Figure()

    hits = 0
    hits_x = []
    hits_y = []
    misses_x = []
    misses_y = []

    for i in range(simulation_shots):
        radius = random.uniform(0, distance * math.sin(moa_radian / 2))
        angle = random.uniform(0, 2 * math.pi)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        if (x**2 + y**2) ** 0.5 <= target_radius:
            hits += 1
            if i < shots:
                hits_x.append(x)
                hits_y.append(y)
        elif i < shots:
            misses_x.append(x)
            misses_y.append(y)

    fig.add_trace(
        go.Scatter(
            x=hits_x,
            y=hits_y,
            mode="markers",
            marker=dict(color="green"),
            name="Hits",
            hovertemplate=None,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=misses_x,
            y=misses_y,
            mode="markers",
            marker=dict(color="red"),
            name="Misses",
            hovertemplate=None,
            hoverinfo="skip",
        )
    )
    fig.add_shape(
        type="circle",
        xref="x",
        yref="y",
        x0=-target_radius,
        y0=-target_radius,
        x1=target_radius,
        y1=target_radius,
        line=dict(
            color="red",
            width=2,
        ),
    )
    fig.update_layout(
        title=f"Hit probability: {str(round(hits / simulation_shots * 100, 2))}%"
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return [fig]


# Creating the page
main_div_style = {}

distance_slider = dcc.Slider(
    id="distance-slider",
    min=0,
    max=2000,
    step=50,
    value=1000,
    marks={i: f"{i}m" for i in range(0, 2001, 100)},
    updatemode="drag",
    tooltip={"placement": "bottom"},
)

target_size_slider = dcc.Slider(
    id="target-size-slider",
    min=0,
    max=1,
    step=0.05,
    value=0.3,
    marks={i: f"{int(i*100)}cm" for i in [0, 0.2, 0.4, 0.6, 0.8, 1]},
    updatemode="drag",
    tooltip={"placement": "bottom"},
)

moa_slider = dcc.Slider(
    id="moa-slider",
    min=0,
    max=5,
    step=0.1,
    value=4,
    marks={i: f"{i}MOA" for i in range(0, 6)},
    updatemode="drag",
    tooltip={"placement": "bottom"},
)

Graphs = html.Div(
    children=[
        html.Div(
            children=[dcc.Graph(id="runsScored")],
            style={"width": "60%", "height": "100%"},
        )
    ]
)

Title = html.Div(children=[html.H1(children="MOA Accuracy Simulator")])

distance_title = html.Div(children=[html.H3(children="Distance to target")])
target_size_title = html.Div(children=[html.H3(children="Target diameter")])
moa_title = html.Div(children=[html.H3(children="MOA")])

app.layout = html.Div(
    id="main_div",
    children=[
        Title,
        distance_title,
        distance_slider,
        target_size_title,
        target_size_slider,
        moa_title,
        moa_slider,
        Graphs,
    ],
    style=main_div_style,
)


@app.callback(
    [Output(component_id="runsScored", component_property="figure")],
    [Input(component_id="distance-slider", component_property="value")],
    [Input(component_id="target-size-slider", component_property="value")],
    [Input(component_id="moa-slider", component_property="value")],
)
def the_callback_function(distance, target_size, moa):
    fig1 = simulate_shots(distance, target_size, moa)
    return fig1


if __name__ == "__main__":
    app.run_server(debug=False, port=8080)
