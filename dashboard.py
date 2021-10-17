from dash import html, dcc
from dash.html.Col import Col
from dash.html.Div import Div
import dash_bootstrap_components as dbc
from app import app
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from components import graphic_card
from figure import geotherm, conductivity, heat_prod, heat_flow, expansivity, parameters
from geotherms.models import Hasterok
from geotherms import Layer
import pandas as pd
layout = html.Div(id='dashboard',
    children=[

        dbc.Row([
            dbc.Col([
                graphic_card('Geotherm', children=[
                    html.Div(className='d-flex flex-row align-items-center', children=[
                        dcc.RangeSlider(id='depth_slider', className='px-5',
                            min=-85, max=0, 
                            value=[-40,-24,-16], 
                            pushable=5, 
                            vertical=True,     
                            step=2,
                            marks={-i*10: f'{i*10}' for i in range(9)}),
                        dcc.Graph(figure=geotherm, id='geotherm-plot', className='flex-fill'),
                        ])
                ])
            ]),

            # dbc.Col([
            #     graphic_card('Parameters',parameters, plot_id='parameter-plot')
            # ], lg=5),

            ]),
        ],
    )

@app.callback(
    Output('geotherm-plot', 'figure'),
    [   Input('surface_hf','value'), 
        Input('surface_temp','value'), 
        Input('model-props','data'), 
        Input('model-props','columns'), 
        Input('depth_slider','value'),
        Input('max_depth','value'), 
        State('geotherm-plot','figure')
        ])
def display_output(surface_hf, surface_temp, data, columns, depth_slider, max_depth, fig):
       
    input = pd.DataFrame(data,columns=[c['name'] for c in columns])
    input.columns = ['label','heat_production','density']
    input['top'] = [0] + sorted([abs(i) for i in depth_slider])
    input['bottom'] = sorted([abs(i) for i in depth_slider]) + [max_depth]

    input[['heat_production','density']] = input[['heat_production','density']].astype('float64')

    # input['density'] = pd.to_numeric(input['density'])
    print(input.dtypes)

    model = Hasterok(
        surface_hf=surface_hf,
        surface_temp=surface_temp+273,
        layers=[Layer(**row.to_dict()) for i, row in input.iterrows()])

    df = model.compute(dz=1)

    l, r = df.T_upper.min() if df.T_upper.min() < 0 else 0, df.adiabat_lower.max()-273
    t, b = 0, df.z_lower.max()

    fig['layout']['yaxis'].update({'range':[t,b],'autorange':'reversed'})
    fig['layout']['xaxis'].update({'range':[l,r]})
    fig['data'] = [
        go.Scatter(
            name=f'{layer.label.capitalize()}', 
            fillcolor=c,
            x=[l,l,r,r],
            y=[layer.top,layer.bottom,layer.bottom,layer.top],
            marker={'opacity':0,'color':c},
            text=str(layer),
            fill = "toself",
            opacity = 0.2, 
            showlegend = False) for layer,c in zip(model.layers,['#F1C40F','#D68910','#6E2C00','#186A3B'])
    ]


    fig['data'].extend([
        go.Scatter(name='Geotherm', x=df.T_upper, y=df.z_upper,  
            marker={'color':'red'}),
        go.Scatter(name='Adiabat', x=df.adiabat_upper-273, y=df.z_upper, 
            line={'dash':'dash'}, 
            marker={'color':'red'}),
        ])

    return fig