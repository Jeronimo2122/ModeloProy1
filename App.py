import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

import Modelo

app = dash.Dash(__name__)
server = app.server

data = pd.read_csv('SeoulBikeDataClean.csv')
originalData = pd.read_csv('SeoulBikeData_utf8.csv')

base_style = {
    'font-family': 'Arial, sans-serif',
    'color': '#333',
    'padding': '10px'
}

title_style = {
    'font-family': 'Arial, sans-serif',
    'color': '#0056b3',
    'text-align': 'center',
    'padding': '10px',
    'border-bottom': '2px solid #0056b3',
}

section_style = {
    'padding': '20px',
    'background-color': '#f9f9f9',
    'border-radius': '5px',
    'margin': '20px'
}

app.layout = html.Div([
    html.H1("Seoul Bike Sharing Demand", style=title_style),

    html.Div(style=section_style, children=[
        html.H2("Historic Demand", style={'text-align': 'center'}),
        html.Label(['Select the season:'], style={'font-weight': 'bold', 'margin': '0 auto'}),
        dcc.Dropdown(
            id='dropdownSeason',
            options=[{'label': i, 'value': i} for i in originalData['Seasons'].unique()],
            value='Winter',
            style={'width': '50%', 'margin': '0 auto'}
        ),
        dcc.Graph(id='historicDemand')
    ]),

    html.Div(style=section_style, children=[
        html.H2("Demand Prediction", style={'text-align': 'center'}),
        html.Label(['Select variables for demand prediction:'], style={'font-weight': 'bold'}),
        dcc.Checklist(
            id='checkBoxDummies',
            options=[{'label': i, 'value': i} for i in ['Holiday', 'Functioning Day']],
            value=['Functioning Day'],
            style={'padding': '10px'}
        ),

        # Sliders de parámetros
        html.Div([
            html.Label(['Select the season:'], style={'font-weight': 'bold'}),
            dcc.Dropdown(id='dropdownSeason2', options=[{'label': i, 'value': i} for i in originalData['Seasons'].unique()]),
            html.Br(),
            html.Label(['Temperature:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='temperatureSlider', min=-20, max=50, step=1, value=0, marks={i: f'{i}' for i in range(-20, 51, 5)}),
            html.Br(),
            html.Label(['Solar Radiation:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='solarRadiationSlider', min=0, max=4, step=0.2, value=0),
            html.Br(),
            html.Label(['Humidity:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='humiditySlider', min=0, max=100, step=1, value=0, marks={i: f'{i}%' for i in range(0, 101, 10)}),
            html.Br(),
            html.Label(['Wind Speed:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='windSpeedSlider', min=0, max=8, step=0.5, value=0),
            html.Br(),
            html.Label(['Rainfall:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='rainfallSlider', min=0, max=35, step=1, value=0),
            html.Br(),
            html.Label(['Snowfall:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='snowfallSlider', min=0, max=10, step=0.5, value=0),
            html.Br(),
            html.Label(['Hour:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='hourSlider', min=0, max=23, step=1, value=0),
            html.Br(),
            html.Label(['Dew Point Temperature:'], style={'font-weight': 'bold'}),
            dcc.Slider(id='dewPointTemperatureSlider', min=-30, max=30, step=1, value=0, marks={i: f'{i}' for i in range(-30, 31, 5)}),
        ], style={'columnCount': 2}),

        # Botón de predicción
        html.Div(html.Button('Predict', id='buttonPredict', n_clicks=0, style={
            'font-weight': 'bold', 'background-color': '#007bff', 'color': 'white', 'border': 'none',
            'padding': '10px 20px', 'cursor': 'pointer', 'border-radius': '5px'
        }), style={'text-align': 'center', 'margin': '20px 0'}),

        html.Div([
            html.H2('Demand Predicted (CI):'),
            html.H1(id='outputDemand', style={'fontSize': '40px', 'color': '#28a745'})
        ], style={'text-align': 'center'}),
    ]),

    html.Div(style=section_style, children=[
        html.H2("Cost Analysis", style={'text-align': 'center'}),

        # Inputs de costos
        html.Div([
            html.Label(['Enter fixed cost per hour:'], style={'font-weight': 'bold'}),
            dcc.Input(id='fixedCost', type='number', style={'width': '50%', 'padding': '10px'}),
            html.Br(),
            html.Label(['Enter variable cost per bike:'], style={'font-weight': 'bold'}),
            dcc.Input(id='variableCost', type='number', style={'width': '50%', 'padding': '10px'}),
            html.Br(),
            html.Label(['Enter profitability (decimal):'], style={'font-weight': 'bold'}),
            dcc.Input(id='profitability', type='number', style={'width': '50%', 'padding': '10px'}),
        ], style={'width': '60%', 'margin': '0 auto'}),

        # Botón de cálculo
        html.Div(html.Button('Calculate', id='buttonCalculatePrice', n_clicks=0, style={
            'font-weight': 'bold', 'background-color': '#007bff', 'color': 'white', 'border': 'none',
            'padding': '10px 20px', 'cursor': 'pointer', 'border-radius': '5px'
        }), style={'text-align': 'center', 'margin': '20px 0'}),

        # Salida de precio sugerido
        html.Div([
            html.H2('Suggested Price per Bike per hour:', style={'font-weight': 'bold'}),
            html.H1(id='outputPrice', style={'fontSize': '40px', 'color': '#28a745'}),
        ], style={'text-align': 'center'}),
        
        # Gráfico de distribución de costos
        html.Div([
            dcc.Graph(id='costDistribution')
        ], style={'width': '70%', 'margin': '0 auto', 'padding-top': '20px'}),
    ])
])

@app.callback(
    Output('outputDemand', 'children'),
    Input('buttonPredict', 'n_clicks'),
    State('checkBoxDummies', 'value'),
    State('dropdownSeason2', 'value'),
    State('windSpeedSlider', 'value'),
    State('rainfallSlider', 'value'),
    State('snowfallSlider', 'value'),
    State('hourSlider', 'value'),
    State('temperatureSlider', 'value'),
    State('humiditySlider', 'value'),
    State('solarRadiationSlider', 'value'),
    State('dewPointTemperatureSlider', 'value')
)
def updateDemand(n_clicks, checkBoxDummies, dropdownSeason2, temperatureSlider, humiditySlider, windSpeedSlider, rainfallSlider,
                snowfallSlider, hourSlider, solarRadiationSlider, dewPointTemperatureSlider):
    demand = 0
    response = ''
    if n_clicks > 0:
        if 'Functioning Day' in checkBoxDummies:
            x = []
            model = Modelo.modeloRLS()[0]
            coef = model.coef_
            demand = model.intercept_

            x.append(hourSlider)
            x.append(temperatureSlider)
            x.append(humiditySlider)
            x.append(windSpeedSlider)
            x.append(dewPointTemperatureSlider)
            x.append(solarRadiationSlider)
            x.append(rainfallSlider)
            x.append(snowfallSlider)
            x.append(1 if 'Holiday' in checkBoxDummies else 0)
            x.append(1)
            if dropdownSeason2 == 'Spring':
                x.append(1)
                x.append(0)
                x.append(0)
            elif dropdownSeason2 == 'Summer':
                x.append(0)
                x.append(1)
                x.append(0)
            elif dropdownSeason2 == 'Winter':
                x.append(0)
                x.append(0)
                x.append(1)
            else:
                x.append(0)
                x.append(0)
                x.append(0)

            for i in range(len(coef)):
                demand = demand + coef[i] * x[i]

            if demand < 0:
                response = '0'
            else:
                inf = demand - 1.44 * Modelo.modeloRLS()[1]
                sup = demand + 1.44 * Modelo.modeloRLS()[1]
                response = f'({inf:.2f} , {sup:.2f})\nMedia: {demand:.2f}'
        
    return response

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

@app.callback(
    Output('outputPrice', 'children'),
    Input('buttonCalculatePrice', 'n_clicks'),
    State('checkBoxDummies', 'value'),
    State('dropdownSeason2', 'value'),
    State('windSpeedSlider', 'value'),
    State('rainfallSlider', 'value'),
    State('snowfallSlider', 'value'),
    State('hourSlider', 'value'),
    State('temperatureSlider', 'value'),
    State('humiditySlider', 'value'),
    State('solarRadiationSlider', 'value'),
    State('dewPointTemperatureSlider', 'value'),
    State('fixedCost', 'value'),
    State('variableCost', 'value'),
    State('profitability', 'value')
)
def updatePrice(n_clicks, checkBoxDummies, dropdownSeason2, temperatureSlider, humiditySlider, windSpeedSlider, rainfallSlider,
                snowfallSlider, hourSlider, solarRadiationSlider, dewPointTemperatureSlider, fixedCost, variableCost, profitability):
    price = 0
    response = 'The sistem is on mantainance'
    if n_clicks > 0:
        if 'Functioning Day' in checkBoxDummies:
            x = []
            model = Modelo.modeloRLS()[0]
            coef = model.coef_
            demand = model.intercept_

            x.append(hourSlider)
            x.append(temperatureSlider)
            x.append(humiditySlider)
            x.append(windSpeedSlider)
            x.append(dewPointTemperatureSlider)
            x.append(solarRadiationSlider)
            x.append(rainfallSlider)
            x.append(snowfallSlider)
            x.append(1 if 'Holiday' in checkBoxDummies else 0)
            x.append(1)
            if dropdownSeason2 == 'Spring':
                x.append(1)
                x.append(0)
                x.append(0)
            elif dropdownSeason2 == 'Summer':
                x.append(0)
                x.append(1)
                x.append(0)
            elif dropdownSeason2 == 'Winter':
                x.append(0)
                x.append(0)
                x.append(1)
            else:
                x.append(0)
                x.append(0)
                x.append(0)

            for i in range(len(coef)):
                demand = demand + coef[i] * x[i]
            
            if demand > 0:
                price = ((fixedCost + variableCost * demand) / (demand)) + profitability
                response = f'{price:.2f}'
            else:
                response = 'The predicted demand is 0, the price can not be calculated'

    return response

@app.callback(
    Output('costDistribution', 'figure'),
    Input('buttonCalculatePrice', 'n_clicks'),
    State('checkBoxDummies', 'value'),
    State('dropdownSeason2', 'value'),
    State('windSpeedSlider', 'value'),
    State('rainfallSlider', 'value'),
    State('snowfallSlider', 'value'),
    State('hourSlider', 'value'),
    State('temperatureSlider', 'value'),
    State('humiditySlider', 'value'),
    State('solarRadiationSlider', 'value'),
    State('dewPointTemperatureSlider', 'value'),
    State('fixedCost', 'value'),
    State('variableCost', 'value'),
    State('profitability', 'value')
)
def updateCostDistribution(n_clicks, checkBoxDummies, dropdownSeason2, temperatureSlider, humiditySlider, windSpeedSlider, rainfallSlider,
                snowfallSlider, hourSlider, solarRadiationSlider, dewPointTemperatureSlider, fixedCost, variableCost, profitability):
    if n_clicks > 0:
        demand = 0
        if 'Functioning Day' in checkBoxDummies:
            x = []
            model = Modelo.modeloRLS()[0]
            coef = model.coef_
            demand = model.intercept_

            x.append(hourSlider)
            x.append(temperatureSlider)
            x.append(humiditySlider)
            x.append(windSpeedSlider)
            x.append(dewPointTemperatureSlider)
            x.append(solarRadiationSlider)
            x.append(rainfallSlider)
            x.append(snowfallSlider)
            x.append(1 if 'Holiday' in checkBoxDummies else 0)
            x.append(1)
            if dropdownSeason2 == 'Spring':
                x.append(1)
                x.append(0)
                x.append(0)
            elif dropdownSeason2 == 'Summer':
                x.append(0)
                x.append(1)
                x.append(0)
            elif dropdownSeason2 == 'Winter':
                x.append(0)
                x.append(0)
                x.append(1)
            else:
                x.append(0)
                x.append(0)
                x.append(0)

            for i in range(len(coef)):
                demand = demand + coef[i] * x[i]

    if None in [fixedCost, variableCost]:
        fig = go.Figure()  # Retorna una figura vacía si alguno de los inputs no es válido.

    else: 
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=['Fixed Cost', 'Variable Cost'],
                             values=[fixedCost, variableCost * demand]))
        fig.update_layout(
            title_text="Hour Expenses",
            title_x=0.5
        )

    return fig
    
if __name__ == '__main__':
    app.run_server(debug=True)