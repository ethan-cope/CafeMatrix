#!./env/bin/python

from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
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
#globalCookieReviewArray = extractReviewsFromLocalTSV(localTSVPath = "default.csv")

#fig = generateMatrix(globalCookieReviewArray)
fig =  px.scatter_3d()

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
                id='big-matrix',
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
                    dbc.Row([

                        dbc.Col([

                            html.H5("View Options"),
                            dcc.RadioItems(
                                ['Value vs. Study','Study vs. Ambiance','Value vs. Ambiance'],
                                defaultView,
                                id='axesSelectOption',
                                labelStyle={'marginTop':'5px'}
                            ),
                        ]),

                        dbc.Col([
                            html.H5("Update Matrix"),
                            dcc.Upload(         
                            id='upload-data',         
                            children=html.Div([             
                                               'Upload Tab-Separated .txt File'
                                              ]),         
                           style={             
                                  'width': '100%',             
                                  'height': '60px',             
                                  'lineHeight': '60px',             
                                  'borderWidth': '1px',             
                                  'borderStyle': 'dashed',             
                                  'borderRadius': '5px',             
                                  'textAlign': 'center',             
                                  'margin': '5px',
                                  },         

                                # Allow multiple files to be uploaded         
                                # of course, actually trying to use multiple files breaks the program
                                # but I already wrote it to use multiple so IDK
                            multiple=True
                            ),     

                        ]) 
                    ]),

                ])),
                # end of cards


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

    dcc.Store(id='user-ratings', storage_type='local'),
])

@callback(Output('user-ratings', 'data'),
          Input('upload-data', 'contents'),
          State('user-ratings', 'data'))
def update_output(list_of_contents, stored_data):
    if list_of_contents is None:
        raise PreventUpdate

    contentData = list_of_contents[0].split(',')[1]
    dataString = base64.b64decode(contentData).decode('ascii').strip()
    # dataString is the CSV file as a string
    dataArray=dataString.split('\n')

    # this doesnt' work and global variables don't work. 
    # need to migrate to cookies and stuff.

    return extractReviewsFromUploadedTSV(dataArray)


@callback(
    Output('big-matrix', 'figure'),
    Input('axesSelectOption', 'value'),
    Input('user-ratings', 'data')
)

def reparseGraphView(cameraView,ratingData):
    '''
    This callback re-generates the matrix, but changes the view depending on the user's selection on the radio buttons.
    '''
    #print(ratingData)
    if ratingData is None:
        raise PreventUpdate
    else:
        fig = generateMatrix(ratingData)
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
    Input('big-matrix', 'clickData')
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
