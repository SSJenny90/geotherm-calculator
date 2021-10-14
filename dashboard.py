from dash import html, dcc
# import dash_bootstrap_components as dbc
from app import app
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import compute

fig = go.Figure(
    data=[go.Scatter()],
    
    layout = go.Layout(
    # title='Geotherm',
    xaxis_title='Temperature [&deg;C]',
    yaxis_title='Depth [km]',
    xaxis = dict(side='top'),
    yaxis_range=[0,250],
    xaxis_range=[0,1500],
    yaxis = dict(
        autorange='reversed',
        ),

    font=dict(
        # family="Courier New, monospace",
        size=18,
    ))
)
    
fig.update_layout()


layout = html.Div(id='dashboard',
    children=[
        dcc.Graph(figure=fig, id='main-figure'),
        ],
    )

@app.callback(
    Output('main-figure', 'figure'),
    [
        Input('surface_hf','value'), 
        Input('p_value','value'), 
        Input('upper_hp','value'), 
        Input('middle_hp','value'), 
        Input('lower_hp','value'), 
        Input('mantle_hp','value'), 
        Input('dz','value'), 
        Input('middle_top','value'), 
        Input('lower_top','value'), 
        Input('moho','value'), 
        Input('max_depth','value'), 
        State('main-figure','figure')
        ]
        )
def display_output(surface_hf, p_value, upper_hp, middle_hp, lower_hp, mantle_hp, dz, middle_top,lower_top,moho, max_depth, fig):
    df = compute.geotherm(surface_hf,max_depth,dz,[middle_top,lower_top,moho], dict(
                    upper=upper_hp,
                    middle=middle_hp,
                    lower=lower_hp,
                    mantle=mantle_hp
                    ))


    fig['data'] = [
        {'type':'scatter', 'x':df.T_lower, 'y':df.z_lower, 'name':'Geotherm'},
        # {'type':'scatter', 'x':x, 'y':df.offset, 'name':'Buffer offset'},
        ]


    return fig