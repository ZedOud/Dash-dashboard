# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from importlib import import_module


from datetime import datetime as dt
from itertools import zip_longest

from os.path import isfile, isdir
import pandas as pd
from pandas_datareader import data as web

# from flask_caching import Cache

''' TODO
Find a nice style
Caching module requests
Get default args from modules?
Modules in a folder
    Import all modules in a folder
    Have default dfuncs population from modules
    Support multiple functions: using buttons?


'''


'''

                INITIALIZATION

'''

# https://bootswatch.com/
external_stylesheets = [
    # 'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # dbc.themes.BOOTSTRAP
    dash_bootstrap_components.themes.LUX
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# We need to suppress, as we have not generated the element IDs for the callbacks we will initiate
app.config['suppress_callback_exceptions'] = True


# cache = Cache(app.server,
#               config={'CACHE_TYPE': 'filesystem',
#                       'CACHE_DIR': 'cache_directory'})

dfuncs = {
    'elements_chemistry': {
        'name': 'Chemical Formula Calculator',
        'func': 'run',
        'path_start': '/molecular-mass',
        'default_args': [
            'H2O'
        ]
    },
    'logic_parser_min': {
        'name': 'Logic Parser',
        'func': 'process_statement',
        'path_start': '/CST-215',
        'default_args': [
            'x & y -> z'
        ]
    },
    'caesar_shift': {
        'name': 'Simple Caesar Shift',
        'func': 'process_caesar_shift',
        'path_start': '/caesar-shift',
        'default_args': [
            'Example message.',
            '1'
        ]
    },
}

pathkeys = {page['path_start']: name for name, page in dfuncs.items()}

default_style = {
    'font-family': 'monospace',
    'font-size': '20px',
    'width': '600px',
    'height': '600px'
}

textarea_style = {
    'font-family': 'monospace',
    'white-space': 'pre-wrap'
}

'''

                INITIAL APP LAYOUT

'''

app.layout = html.Div(children=[

    ### Header section
    html.H2(children='Hello, Nayalytics! Exploratory demo below.'),
    html.H3(children=f'Last updated: {dt.now()}'),
    html.Div([
        '''This is built using ''',
        html.A('Dash\n', href="https://plot.ly/products/dash/")
    ]),

    html.H1('Stock Tickers'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
    dcc.Graph(id='my-graph'),


    html.Hr(),

    ### Link section
    # represents the URL bar, doesn't render anything
    # used to determine the callback action in generated callbacks
    dcc.Location(id='url', pathname='/', refresh=False),

    dbc.Container([
        dbc.Card([
            dbc.CardBody([
                # TODO : Format "Navigate to..."
                dcc.Link('Navigate to Home', href='/'),
                html.Br(),
                dcc.Link('Navigate to config page.', href='/config'),
                html.Br(),
                html.Br(),
                *[
                    a
                    for b in [(dcc.Link('Navigate to {} page.'.format(page['name']), href=page['path_start']), html.Br()) for page in dfuncs.values()]
                    for a in b
                ],
            ])
        ])
    ]),

    html.Hr(),

    # content will be rendered in this element
    html.Div(id='page-content')
])


'''

                NORMAL APP CALLBACKS

'''


@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    # TODO: pickling thread-safe? probably?
    data_source = 'robinhood'
    dirname = 'pickle_cache'
    pname = f'{dirname}/{data_source}-{selected_dropdown_value}.pkl.xz'
    if not isdir(dirname):
        from os import mkdir
        mkdir(dirname)
        print('created cache directory:', dirname)
    if isfile(pname):
        df = pd.read_pickle(pname)
        print('retrieved from cache:', pname)
    else:
        df = web.DataReader(
            selected_dropdown_value, data_source=data_source,
            # start=dt(2017, 1, 1), end=dt.now()
        )
        df.to_pickle(pname)
        print('created cache:', pname)

    return {
        'data': [{
            'x': df.index.levels[1],
            'y': df.close_price
        }]
    }


'''

                ESTABLISHING APP CALLBACKS FROM MODULES

'''

dcallbacks = {}
dcbf = {}
dfinal = {}

for file, page in dfuncs.items():
    dcbf[file] = {}
    dcbf[file]['module'] = import_module(file)
    dcbf[file]['function'] = dcbf[file]['module'].__dict__[page['func']]
    output_id_name = f'{file}-output-logic-state'
    # Here we are getting the names of the functions' arguments
    fargs = dcbf[file]['function'].__code__.co_varnames[:dcbf[file]['function'].__code__.co_argcount]
    input_id_names = [f'{arg}-input-{i}-state' for i, arg in enumerate(fargs)]

    dfinal[file] = app.callback(
        output=Output(output_id_name, 'children'),
        inputs=[Input(n, 'value') for n in input_id_names],
        state=[State('url', 'pathname')]
    )(lambda *args, **kwargs, : dcbf[pathkeys[args[-1]]]['function'](*args[:-1], **kwargs))

    dcallbacks[file] = {
        'link_html': [
            dbc.Container([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Form([
                            a
                            # We reverse the inputs to the zip_longest so missing values are filled first, than order is corrected
                            # This way we get default arguments listed last and in order
                            # arg and fargs are cosmetic here
                            for b in [
                                [
                                    dbc.FormGroup(
                                        [
                                            dbc.Label(arg, html_for=n,
                                                      width=2
                                                      ),
                                            dbc.Col(
                                                dbc.Input(id=n, type="text", value=v),
                                                # width=3,
                                            ),
                                        ],
                                        row=True,
                                    ),
                                    # html.Span(children=f' {arg} ', style=default_style),
                                    # dcc.Input(id=n, type='text', value=v)
                                ] for arg, n, v in list(zip_longest(fargs[::-1], input_id_names[::-1], page['default_args'][::-1], fillvalue=''))[::-1]
                            ]
                            for a in b
                        ])
                    ]),
                ]),
                html.Hr(),
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardText(id=output_id_name, style=textarea_style)
                    ])
                ]),
                # html.Div([
                #     dcc.Textarea(
                #         id=output_id_name,
                #         # style=default_style
                #     )
                # ])
            ])
        ],
        'fargs': fargs,
        'output_id_name': output_id_name,
        'input_id_names': input_id_names
    }

'''

                APP NAVIGATION LINKS

'''


# Link Callback
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/config':
        pass
    else:
        for module in dcallbacks:
            # if pathname.startswith(dfuncs[module]['path_start']):
            if pathname == dfuncs[module]['path_start']:
                return dcallbacks[module]['link_html']
        else:
            return dbc.Container([dbc.Card([dbc.CardBody([
                html.H3('Default page: You are on page {}'.format(pathname))
            ])])])


'''

                APP START

'''

if __name__ == '__main__':
    app.run_server(debug=True)
