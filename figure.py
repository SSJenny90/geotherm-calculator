from plotly import graph_objects as go

geotherm = go.Figure(
    data=[go.Scatter()],
    layout = go.Layout(
        xaxis_title='Temperature [&deg;C]',
        yaxis_title='Depth [km]',
        xaxis = dict(side='top'),
        yaxis_range=[0,250],
        xaxis_range=[0,1450],
        yaxis = dict(
            autorange='reversed',
            ),
        margin=dict(l=30, r=30, t=30, b=20),
        height=550,
        )
    )
    
parameters = go.Figure(
    data=[go.Scatter()],
    layout = go.Layout(
        xaxis_title='Heat Flow [mW m<sup>-2</sup>]',
        yaxis_title='Depth [km]',
        xaxis = dict(side='top'),
        yaxis_range=[0,500],
        xaxis_range=[0,3.5],
        yaxis = dict(autorange='reversed'),
        margin=dict(l=30, r=30, t=30, b=20),
        height=550,
        ),

    )

conductivity = go.Figure(
    data=[go.Scatter()], 
        layout = go.Layout(
        # title='Geotherm',
        xaxis_title='&#955; [W m<sup>-1</sup> K<sup>-1</sup>]',
        yaxis_title='Depth [km]',
        xaxis = dict(side='top'),
        yaxis_range=[0,500],
        xaxis_range=[0,3.5],
        yaxis = dict(autorange='reversed',),
        )
    )

heat_flow = go.Figure(
    data=[go.Scatter()],
        layout = go.Layout(
        # title='Geotherm',
        xaxis_title='Heat Flow [mW m<sup>-2</sup>]',
        yaxis_title='Depth [km]',
        xaxis = dict(side='top'),
        yaxis_range=[0,500],
        xaxis_range=[0,3.5],
        yaxis = dict(
            autorange='reversed',
            ),
        )
    )

expansivity = go.Figure(
    data=[go.Scatter()],
    
    layout = go.Layout(
    # title='Geotherm',
    xaxis_title='Alpha [mW m<sup>-2</sup>]',
    yaxis_title='Depth [km]',
    xaxis = dict(side='top'),
    yaxis_range=[0,500],
    xaxis_range=[0,3.5],
    yaxis = dict(autorange='reversed'),
    )
)

heat_prod = go.Figure(
    data=[go.Scatter()],
    
    layout = go.Layout(
    # title='Geotherm',
    xaxis_title='&#956; [m<sup>-3</sup>]',
    yaxis_title='Depth [km]',
    xaxis = dict(side='top'),
    yaxis_range=[0,500],
    xaxis_range=[0,3.5],
    yaxis = dict(autorange='reversed'),
    )
)

