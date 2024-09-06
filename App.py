import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

import Modelo

app = dash.Dash(__name__)
server = app.server

data = pd.read_csv('SeoulBikeDataClean.csv')
originalData = pd.read_csv('SeoulBikeData_utf8.csv')

app.layout = html.Div([
    html.H1("Seoul Bike Sharing Demand", style={'text-align': 'center'}),

    html.H2("Historic Demand", style={'text-align': 'center', 'align': 'center'}),

    dcc.Dropdown(
        id='dropdownSeason',
        options= [{'label': i, 'value': i} for i in originalData['Seasons'].unique()],
        value='Winter'
    ),
    dcc.Graph(id='historicDemand'),

    html.Div([
    html.Div([
        html.Label(['Select as many variables as you want to predict demand on those conditions'], style={'font-weight': 'bold'}),
        dcc.Checklist(
            id='checkBoxDummies',
            options=[
                 {'label': 'Holiday', 'value': 'Holiday'},
            {'label': 'Functioning Day', 'value': 'Functioning Day'},
            {'label': 'Seasons_Spring', 'value': 'Seasons_Spring'},
            {'label': 'Seasons_Summer', 'value': 'Seasons_Summer'},
            {'label': 'Seasons_Winter', 'value': 'Seasons_Winter'}]
        ),

        html.Br(),

        html.Label(['Select the temperature:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='temperatureSlider', min=-20, max=50, step=1, value=0),

        html.Br(),
        html.Label(['Select solar radiation:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='solarRadiationSlider', min=0, max=4, step=0.1, value=0),

        html.Br(),

        html.Label(['Select the humidity:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='humiditySlider', min=0, max=100, step=1, value=0, marks={i: f'{i}%' for i in range(0, 101, 5)}),

        html.Br(),

        html.Label(['Select the wind speed:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='windSpeedSlider', min=0, max=8, step=0.5, value=0),

        html.Br(),

        html.Label(['Select the rain fall:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='rainfallSlider', min=0, max=35, step=1, value=0),

        html.Br(),

        html.Label(['Select the snow fall:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='snowfallSlider', min=0, max=10, step=1, value=0),

        html.Br(),

        html.Label(['Select the hour:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='hourSlider', min=0, max=23, step=1, value=0),

        html.Br(),
        html.Label(['Select dew point temperature:'], style={'font-weight': 'bold'}),
        dcc.Slider(id='dewPointTemperatureSlider', min=-30, max=30, step=1, value=0),

        html.Br(),

        html.Div(
            html.Button('Predict', id='buttonPredict', n_clicks=0, style={'font-weight': 'bold'}),
            style={'text-align': 'center'}
        ),
    ],
    style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),

    html.Div([
            html.H2('Demand Predicted:'),
            html.H1(id='outputDemand', style={'fontSize': '50px'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'})
    ])
])

@app.callback(
    Output('outputDemand', 'children'),
    Input('buttonPredict', 'n_clicks'),
    Input('checkBoxDummies', 'value'),
    Input('temperatureSlider', 'value'),
    Input('humiditySlider', 'value'),
    Input('windSpeedSlider', 'value'),
    Input('rainfallSlider', 'value'),
    Input('snowfallSlider', 'value'),
    Input('hourSlider', 'value'),
    Input('solarRadiationSlider', 'value'),
    Input('dewPointTemperatureSlider', 'value')
)
def updateDemand(n_clicks, checkBoxDummies, temperatureSlider, humiditySlider, windSpeedSlider, rainfallSlider,
                snowfallSlider, hourSlider, solarRadiationSlider, dewPointTemperatureSlider):
    x = []
    model = Modelo.modeloRLS()
    coef = model.coef_
    demand = model.intercept_
    if n_clicks > 0:
        x.append(hourSlider)
        x.append(temperatureSlider)
        x.append(humiditySlider)
        x.append(windSpeedSlider)
        x.append(dewPointTemperatureSlider)
        x.append(solarRadiationSlider)
        x.append(rainfallSlider)
        x.append(snowfallSlider)
        for dummy in checkBoxDummies:
            if dummy == 'Holiday':
                x.append(1)
            else:
                x.append(0)
            if dummy == 'Functioning Day':
                x.append(1)
            else:
                x.append(0)
            if dummy == 'Seasons_Spring':
                x.append(1)
            else:
                x.append(0)
            if dummy == 'Seasons_Summer':
                x.append(1)
            else:
                x.append(0)
            if dummy == 'Seasons_Winter':
                x.append(1)
            else:
                x.append(0)
        for i in range(len(coef)):
            demand = demand + coef[i] * x[i]
        
    else:
        demand = '0'
    return str(demand)

@app.callback(
    Output('historicDemand', 'figure'),
    Input('dropdownSeason', 'value')
)
def updateHistoricDemand(season):
    filteredData = originalData[originalData['Seasons'] == season]
    fig = go.Figure()

    fig.add_trace(go.Bar(x=filteredData['Hour'], y=filteredData['Rented Bike Count'], name='Rented Bike Count'))

    fig.update_layout(xaxis_title='Hour',
                    yaxis_title='Rented Bike Count')
    return fig

    
if __name__ == '__main__':
    app.run_server(debug=True)