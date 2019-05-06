# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from importlib import import_module


from datetime import datetime as dt
from itertools import zip_longest
import re

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
    dbc.themes.LUX
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

stock_values = {
    'open':     'open',
    'close':    'close',
    'high':     'high',
    'low':      'low',
    'volume':   'volume',
}

stock_tickers = {
    'Coke':         'COKE',
    'Tesla':        'TSLA',
    'Apple':        'AAPL',
    'Qualcomm':     'QCOM',

    'S&P 500':                      '^GSPC',
    'Russel 2000':                  '^RUT',
    'NASDAQ Composite Index':       'NASDAQ:^IXIC',
    'Dow Jones Industrial Average': '^DJI',

    'Apple - Qualcomm':             'AAPL-QCOM'
}

stock_tickers_temp = {}

'''

                INITIAL APP LAYOUT

'''

app.layout = html.Div(children=[


    ### Link section
    # represents the URL bar, doesn't render anything
    # used to determine the callback action in generated callbacks
    dcc.Location(id='url', pathname='/', refresh=False),

    dbc.Container([
        dbc.Card([
            dbc.CardBody([
                ### Header section
                html.H2(['Hello and welcome to my exploratory demo of Dash!']),
                html.Div([
                    'Built by Andrew Parsadayan',
                    html.Br(),
                    'Graduated from Grand Canyon University in the Fall of 2019 with a Bachelors in Computer Science with an emphasis in Big Data',
                    html.Br(),
                    html.A(
                        'Code posted here.',
                        href="https://github.com/ZedOud/Dash-dashboard/blob/master/Dashboard/dashapp.py",
                        target="_blank"  # "_top" for "full body of the window" or "_blank" for new tab/window
                    ),
                    html.Br(),
                    'Contact: ',
                    html.A(
                        'zed_oud@mac.com',
                        href="mailto:zed_oud@mac.com?Subject=Hello%20from%20Dash",
                        target="_top"  # "_top" for "full body of the window" or "_blank" for new tab/window
                    ),
                    ' (from the MobileMe days)'
                ]),
                html.Div([
                    '''This is built using ''',
                    html.A('Dash\n', href="https://plot.ly/products/dash/")
                ]),
                html.Div([f'Last updated: {dt.now()}']),
                html.Div([f'MoTD: Try the "stocks" page!']),
            ]),
        ]),
        dbc.Card([
            dbc.CardBody([
                # TODO : Format "Navigate to..."
                dcc.Link('Navigate to Home', href='/'),
                html.Br(),
                dcc.Link('Navigate to empty page.', href='/empty'),
                html.Br(),
                dcc.Link('Navigate to stocks page.', href='/stocks'), ' (Add extra stock tickers)',
                dcc.Input(id='text-tickers-input', value='LYFT, GOOG', type='text'),
                ' (comma delimited)',
                html.Br(),
                html.Br(),
                '''Navigate to imported functions:''',
                html.Br(),
                *[
                    a
                    for b in [(
                        dcc.Link(f'{page["name"]} page.', href=page['path_start']+'#page-content'),
                        html.Br()
                    )
                        for page in dfuncs.values()
                    ]
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


def get_fin_df(ticker):
    data_source = 'av-daily'  # 'robinhood'
    dirname = 'pickle_cache'
    pname = f'{dirname}/{data_source}-{ticker}.pkl.xz'
    print(f'attempting: {pname}')
    if not isdir(dirname):
        from os import mkdir
        mkdir(dirname)
        print('created cache directory:', dirname)
    if isfile(pname):
        df = pd.read_pickle(pname)
        print('retrieved from cache:', pname)
    else:
        df = web.DataReader(
            ticker, data_source=data_source,
            start=dt(2016, 1, 1), end=dt.now(),
            access_key='FGSVWS9KZYCDUREQ'
        )
        df.to_pickle(pname)
        print('created cache:', pname)
    return df


def get_complex_fin_df(ticker):
    if '-' in ticker:
        df1, df2 = [get_fin_df(t) for t in ticker.split('-')]
        df = pd.DataFrame()
        for k, v in stock_values.items():
            df[v] = df1[v] - df2[v]
    else:
        df = get_fin_df(ticker)
    return df


@app.callback(Output('my-graph', 'figure'),
              [
                  Input('stock-dropdown-ticker', 'value'),
                  Input('stock-dropdown-metric', 'value'),
                  Input('stock-dropdown-normalize', 'value')
              ])
def update_graph(dropdown_tickers, dropdown_metric, dropdown_normalize):
    # TODO: pickling thread-safe? probably?
    fig = {'data': []}
    if dropdown_normalize:
        dfn = get_complex_fin_df(dropdown_normalize)
    for ticker in dropdown_tickers:
        df = get_complex_fin_df(ticker)
        if dropdown_normalize:
            for k, v in stock_values.items():
                df[v] = df[v] / dfn[v]
        fig['data'].append({
            'x': df.index,
            'y': df[dropdown_metric],
            'name': ticker
        })
    return fig


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
              [dash.dependencies.Input('url', 'pathname'),
               dash.dependencies.Input('text-tickers-input', 'value')])
def display_page(pathname, extra_tickers):
    # pathname, *query = [*pathname.split('?'), None]
    # query.pop()  # eliminates None inserted to prevent tuple unpacking issues
    if pathname == '/empty':
        pass
    elif pathname == '/stocks':
        global stock_tickers_temp

        try:
            # stock_tickers_temp = {v: v for v in query.split('?')}
            stock_tickers_temp = {v: v for v in re.sub(r'\s', '', extra_tickers).split(',')}
            print(stock_tickers_temp)
        except:
            stock_tickers_temp = {}
        return dbc.Container([
            dbc.Card([
                dbc.CardBody([
                    html.H4('Stock Tickers'),
                    dcc.Dropdown(
                        id='stock-dropdown-ticker',
                        options=[
                            {'label': k, 'value': v} for k, v in [*stock_tickers.items(), *stock_tickers_temp.items()]
                        ],
                        value=['COKE', 'TSLA'],
                        multi=True
                    )
                ]),
                dbc.CardBody([
                    html.H4('Stock Values'),
                    dcc.Dropdown(
                        id='stock-dropdown-metric',
                        options=[
                            {'label': k, 'value': v} for k, v in stock_values.items()
                        ],
                        value='close'
                    )
                ]),
                dbc.CardBody([
                    html.H4('Normalize to...'),
                    dcc.Dropdown(
                        id='stock-dropdown-normalize',
                        options=[
                            {'label': k, 'value': v} for k, v in [*stock_tickers.items(), *stock_tickers_temp.items()]
                        ]
                    )
                ]),
                dbc.CardBody([
                    dcc.Graph(id='my-graph'),
                ])
            ])
        ])
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
