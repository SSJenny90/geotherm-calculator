from dash import html, Dash
import dash_bootstrap_components as dbc
from flask_caching import Cache


stylesheets = [
    {
        'href': 'https://use.fontawesome.com/releases/v5.15.1/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-vp86vTRFVJgpjF9jiIGPEEqYqlDwgyBgEF109VFjmqGmIY/Y4HV4d3Gp2irVfcrp',
        'crossorigin': 'anonymous'
    },
    "assets\css\sb-admin-2.css",
    # dbc.themes.DARKLY,
]

external_scripts = [
    "assets\js\jquery.min.js",
    "assets\js\jquery.easing.min.js",
    # "assets\js\sb-admin-2.js",
]

app = Dash(__name__, 
    external_stylesheets=stylesheets,
    external_scripts=external_scripts,
    suppress_callback_exceptions=True,
    )


CACHE_CONFIG = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

