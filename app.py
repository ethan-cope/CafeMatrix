#!./env/bin/python

from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px      
import plotly.graph_objects as go
import base64
import pandas as pd
import json
from genMatrix import generateMatrix, generateShopBarChart, extractReviewsFromLocalTSV, extractReviewsFromUploadedTSV

defaultView = 'Value vs. Study'

# initial figure stuff
# globalCookieReviewArray is part of a failed experiment. I need to do caching if I want to do this too.
globalCookieReviewArray = []
globalCookieReviewArray = extractReviewsFromLocalTSV(localTSVPath = "ratings.csv")

fig = generateMatrix(globalCookieReviewArray)

views = {
        "AmbVsStu": {'x': 0, 'y': 2, 'z': 0},
        "ValVsStu": {'x': 2, 'y': 0, 'z': 0.1},
        "ValVsAmb": {'x': 0, 'y': 0, 'z': 2} # this view is broken, though. maybe you'll need to encode this stuff.
        }
camera = {"eye": views["ValVsStu"]}

fig.update_layout(
    scene_camera=camera,
    clickmode='event+select'
)

App = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP]
)

colors = {
        'background': '#FFFDD1'
}

def drawCafeMatrix():
    '''
    This spits out a bootstrap card that has the cafe matrix in it.
    It's only called on page reload.
    '''
    return dbc.Card([
        dbc.CardBody([
            html.H4("Cafe Matrix", className="card-title"),
            html.Div([dcc.Graph(
                figure=fig, 
                id='basic-interactions',
                style={'width':'90vh','height':'90vh'})
            ])
        ])
    ])

def drawSelectPane():       
    '''
    This spits out a bootstrap card with the matrix options and the sub-matrix bar chart.
    It's only called on page reload.
    '''
    return dbc.Card([
        dbc.CardBody([
            html.H4("Matrix Options", className="card-title"),
            html.Div([
                dbc.Card(
                dbc.CardBody([
                html.H5("View Options"),
                dcc.RadioItems(
                    ['Value vs. Study','Study vs. Ambiance','Value vs. Ambiance'],
                    defaultView,
                    id='axesSelectOption',
                    labelStyle={'marginTop':'5px'}
                ),
                ])),
                dcc.Graph(
                    id='breakdown-graph',
                    style={'width':'90vh','height':'74vh'}
                )
            ])
        ])
    ])

App.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
               dbc.Col([
                   drawCafeMatrix()
                ]),
               dbc.Col([
                   drawSelectPane(),
                ]) 

            ])
        ])
    ),
    dcc.Upload(         
               id='upload-data',         
               children=html.Div([             
                                  'Drag and Drop or ',             
                                  html.A('Select Files')         
                                  ]),         
               style={             
                      'width': '100%',             
                      'height': '60px',             
                      'lineHeight': '60px',             
                      'borderWidth': '1px',             
                      'borderStyle': 'dashed',             
                      'borderRadius': '5px',             
                      'textAlign': 'center',             
                      'margin': '10px'         },         
               # Allow multiple files to be uploaded         
               multiple=True     
               ),     
    html.Div(id='output-data-upload'),
])

@callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents:
        contentData = list_of_contents[0].split(',')[1]
        dataString = base64.b64decode(contentData).decode('ascii').strip()
        # dataString is the CSV file as a string
        dataArray=dataString.split('\n')

        # this doesnt' work and global variables don't work. 
        # need to migrate to cookies and stuff.
        globalCookieReviewArray = extractReviewsFromUploadedTSV(dataArray)

        print(len(globalCookieReviewArray))

        # need way to update graph figure without clicking it and being able to return directly
        # reparseGraphView(defaultView)
        # extracting content data from import format
        

@callback(
    Output('basic-interactions', 'figure'),
    Input('axesSelectOption', 'value')
)

def reparseGraphView(cameraView):
    '''
    This callback re-generates the matrix, but changes the view depending on the user's selection on the radio buttons.
    '''
    fig = generateMatrix(globalCookieReviewArray)
    print(len(globalCookieReviewArray))
    views = {
            "Value vs. Study": {'x': 2, 'y': 0, 'z': 0.1},
            "Study vs. Ambiance": {'x': 0.01, 'y': 2, 'z': 0},
            "Value vs. Ambiance": {'x': 0, 'y': 0, 'z': 2} 
            # this one is a little messed up, b/c the graph is on the wrong side.
    }

    scenes = {
            "Value vs. Study": {'yaxis': {}},
            "Study vs. Ambiance": {'yaxis': {'autorange':'reversed'}},
            "Value vs. Ambiance": {'zaxis': {'autorange':'reversed'}, 'yaxis': {'autorange':'reversed'}, 'xaxis': {'autorange':'reversed'}}
            # handles the axes reversed or not
    }

    camera = {"eye": views[cameraView]}
    # handles direction we're looking
    sceneDir = scenes[cameraView]
    # handles the 

    fig.update_layout(
        scene_camera=camera,
        scene=sceneDir,
        clickmode='event+select'
    )
    return fig

@callback(
    Output('breakdown-graph', 'figure'),
    Input('basic-interactions', 'clickData')
)
def displayBarChart(clickData):
    '''
    This callback generates the bar chart for the matrix the user clicks on.
    '''
    fig = go.Figure() 
    if clickData:
        indexData = clickData["points"][0]['customdata'][1]
        shopName = (clickData["points"][0]['text'])
        fig = generateShopBarChart(indexData, shopName)
    return fig

App.run_server(debug=True, use_reloader=True)
