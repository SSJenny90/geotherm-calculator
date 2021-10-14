from dash import html, dcc
from dash.html.H6 import H6
from dash.html.Span import Span
import dash_bootstrap_components as dbc
from random import randint
import dash_daq as daq

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

def number_input(**kwargs):
    # nrange = kwargs.pop('nrange', None)
    return dbc.Input(**kwargs, type='number', debounce=True)

sidebar = html.Ul(
    className="navbar-nav bg-primary sidebar sidebar-dark accordion", id="accordionSidebar",children=[
        html.A(
            className="sidebar-brand d-flex align-items-center justify-content-center", href="/",
            children=[
                    html.Span('Geotherm', className='pr-1'),
                    html.I(className="fas fa-calculator"),
                ]),       
        html.Hr(className="sidebar-divider my-0"),

        sidebar_form('Heat Flow','fas fa-fire', children=[
            input('Surface', 3, number_input(id='surface_hf',value=65,)),
            ]),

        sidebar_form('Heat Production','fas fa-layer-group', children=[
                dbc.InputGroup([
                    dbc.Label('Partition', width=2),
                    dbc.Col(
                        daq.BooleanSwitch(id='my-boolean-switch', on=False),
                        width=8),
                    dbc.Label('Direct', width=2),
                    ]),
                input('P-value', 3, number_input(id='p_value',value=0.76,)),
                html.H6('Heat Production Values', className='collapse-header'),                
                input('Upper',  3, number_input(id='upper_hp',value=1.0563,)),
                input('Middle', 3, number_input(id='middle_hp',value=0.4,)),
                input('Lower',  3, number_input(id='lower_hp',value=0.4,)),
                input('Mantle',  3, number_input(id='mantle_hp',value=0.02,)),
            ]),
        sidebar_form('Model Depths','fas fa_layer-group', children=[
            input('Step', 3, number_input(id='dz',value=0.5,)),
            input('Middle', 3, number_input(id='middle_top',value=16,)),
            input('Lower', 3, number_input(id='lower_top',value=24,)),
            input('Moho', 3, number_input(id='moho',value=40,)),
            input('Max_Depth', 3, number_input(id='max_depth',value=250,)),
            ]),  
        html.Hr(className="sidebar-divider my-0"),
    ])

navbar = html.Nav(
    className="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow",
    children=html.H3(id='topnav-title', children='A simple geotherm calculator!')
    )



