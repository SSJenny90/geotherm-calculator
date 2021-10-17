from typing import Container
from dash import html, dcc, dash_table
from dash.html.H6 import H6
from dash.html.Span import Span
import dash_bootstrap_components as dbc
from random import randint
import dash_daq as daq
import pandas as pd

df = pd.DataFrame(dict(
            Label=['upper crust','middle crust','lower crust','mantle'],
            HP=[1.0563,0.4,0.4,0.02],
            Density=[2850,2850,2850,3350],
        ))

def li(label,href,icon):
    return  html.Li(className="nav-item", children=[
        html.A(
            className="nav-link",
            href=href, children=[
                html.I(className=f"fas fa-lg {icon}"),
                html.Span(label)
            ])
        ])

def nav_link(label, href):
    return html.A(className="collapse-item", href=href, children=label)
  
def sidebar_dropdown(label, icon, children=[]):
    sidebar_links = []
    for child in children:
        sidebar_links.append(nav_link(*child))

    return html.Li(className='nav-item', children=[
        html.A(
            className="nav-link collapsed", 
            href="#",
            **{'data-toggle':"collapse",
            'data-target':f"#{label}"},
            children=[  
                html.I(className=f"fas {icon}"),
                html.Span(label)]
            ),
        html.Div(id=label,
            className="collapse",
            **{'data-parent':'#accordionSidebar'},
            children=[
                html.Div(
                    className="bg-white py-2 collapse-inner rounded",
                    children=sidebar_links)
            ])  
        ])

def sidebar_form(label, icon, children=[]):
    return html.Li(className='nav-item', children=[
        html.A(
            className="nav-link collapsed", 
            href="#",
            # **{'data-toggle':"collapse",
            # 'data-target':f"#{label}"},
            children=[  html.I(className=f"fas {icon}"),
                        html.Span(label) ]),
        # html.Span(label),
        html.Div(id='-'.join(label.split(' ')),
            className="collapse show",
            **{'data-parent':'#accordionSidebar'},
            children=[
                html.Div(
                    className="bg-white py-2 collapse-inner rounded",
                    children=children)
                    ]
            )  
    ])

def input(label, width, children=[]):
    fid=f"{label.lower()}-{randint(0,10000)}" 
    return dbc.InputGroup(
            [
                dbc.Label(label, html_for=fid, width=width),
                dbc.Col(
                    children=children,
                    width=12-width),
            ],
            className='pb-1',
        )

def dual_input(label, width, children=[]):
    fid=f"{label.lower()}-{randint(0,10000)}" 

    children = [dbc.Col(child, width=12/2-width) for child in children]

    return dbc.InputGroup([
                dbc.Label(label, html_for=fid, width=width)].extend(children),
            className='pb-1',
        )

def number_input(**kwargs):
    # nrange = kwargs.pop('nrange', None)
    return dbc.Input(**kwargs, type='number', debounce=True)

sidebar = html.Ul(
    className="navbar-nav bg-primary sidebar sidebar-dark accordion", id="accordionSidebar",children=[
        html.A(
            className="sidebar-brand d-flex align-items-center justify-content-center", href="/",
            children=[
                    html.Span('My Geotherm',className='pr-2'),
                    html.I(className="fas fa-calculator"),
                ]),       
        html.Hr(className="sidebar-divider my-0"),
        sidebar_form('Model Setup','fas fa-layer-group', children=[
                html.H6('Heat Flow', className='collapse-header'),                
                input('Surface Heat Flow', 6, number_input(id='surface_hf',value=65,)),
                input('Surface Temp [°C]', 6, number_input(id='surface_temp',value=24,)),
                input('Model Depth', 6, number_input(id='max_depth',value=250,)),

                # dbc.InputGroup([
                    # dbc.Label('Partition', width=2),
                    # dbc.Col(
                    #     daq.BooleanSwitch(id='my-boolean-switch', on=False),
                    #     width=8),
                    # dbc.Label('Direct', width=2),
                    # ]),
                # input('P-value', 4, number_input(id='p_value',value=0.76,)),
                html.H6('Layer Properties', className='collapse-header'),    
                dbc.Container(            
                    dash_table.DataTable(
                        id='model-props', data=df.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in df.columns],
                        editable=True,
                        style_as_list_view=True,
                        style_cell={'textAlign': 'center'},
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Label'},
                                'textAlign': 'left'
                            }]   
                    ),
                )
            ]), 
        html.Hr(className="sidebar-divider my-0"),
    ])

navbar = html.Nav(
    className="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow",
    children=html.H3(id='topnav-title', children='Welcome to my geotherm calculator!')
    )



