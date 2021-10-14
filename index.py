from dash import dcc, html
from dash.dependencies import Input, Output
from app import app
import dashboard
from navbar import navbar, sidebar

pages = {
    '/': dashboard.layout,
}

app.layout = html.Div(id='wrapper',children=[
    dcc.Location(id='url', refresh=False),
    sidebar,
    html.Div(id='content-wrapper',className="d-flex flex-column",children=[
        html.Div(id='content', children=[
            navbar,
            html.Div(id='page-content', className='container-fluid')
        ]),
    ]),
    dcc.Store(id='signal', storage_type='session'),
    ],
    )


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    # print(pages.get(pathname,'404'))
    layout = pages.get(pathname,'404')
    if callable(layout):
        return layout()
    else:
        return layout


if __name__ == '__main__':
    app.run_server(
        # host='0.0.0.0',
        port=9999,
        debug=True
        )