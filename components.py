from dash.html.Div import Div
import dash_bootstrap_components as dbc
from dash import html, dcc

def graphic_card(header, children):

    return dbc.Card([
        dbc.CardHeader([
            html.H6(header,className='m-0 font-weight-bold text-primary'),
            html.Div(className='dropdown no-arrow', children=[
                html.A(className="dropdown-toggle", href="#", role="button", id="dropdownMenuLink", 
                **{'data-toggle':"dropdown"}, children=[
                    html.I(className="fas fa-ellipsis-v fa-sm fa-fw text-gray-400")
                ]),
                html.Div(className="dropdown-menu dropdown-menu-right shadow animated--fade-in", children=[
                    dbc.DropdownMenuItem('Link 1',href='#'),
                ]),
            ]),

            
            ], 
            className='py-3 d-flex flex-row align-items-center justify-content-between'),
        dbc.CardBody(children=children),
    ],
    className='mb-4 shadow',
)