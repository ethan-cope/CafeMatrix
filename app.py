#!./env/bin/python

from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px      
import plotly.graph_objects as go
import base64
from genMatrix import generateMatrix, generateShopBarChart, extractReviewsFromLocalTSV, extractReviewsFromUploadedTSV

# import json
# import pandas as pd
# not needed as of 11.26.2023

#TODO: use cool monospaced font and dark mode?
#TODO: user guide
#TODO: user-definable scaling
#TODO: points are selectable cursor

# initial figure 
defaultView = 'Value vs. Study' # Global variable, but read-only so should be ok
fig =  px.scatter_3d()

camera = {"eye": {'x': 2, 'y': 0, 'z': 0.1}}
fig.update_layout(
    scene_camera=camera,
    clickmode='event+select'
)

# adding bootstrap
App = Dash(__name__,
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
            html.H4("Cafe Matrix", className="card-title card-mono"),
            html.Div([dcc.Graph(
                figure=fig, 
                id='big-matrix',
                style={'width':'90vh',
                       'height':'90vh',
                       'cursor':'pointer',
                       }),

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
            html.H4("Matrix Options", className="card-title card-mono"),
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
                                labelStyle={'marginTop':'5px',
                                            'cursor': 'pointer',}
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
                                  'cursor': 'pointer',
                                  },         

                                # Allow multiple files to be uploaded         
                                # of course, actually trying to use multiple files breaks the program
                                # but I already wrote it to use the multiple option
                                # TODO:: change this it make multiple false.
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
    """
    This callback is triggered if the user uploads new data through the dialog boxes.
    """
    if list_of_contents is None:
        raise PreventUpdate

    contentData = list_of_contents[0].split(',')[1]
    dataString = base64.b64decode(contentData).decode('ascii').strip()
    # dataString is the TSV file as a string
    dataArray=dataString.split('\n')

    return extractReviewsFromUploadedTSV(dataArray)

@callback(
    Output('big-matrix', 'figure'),
    Input('axesSelectOption', 'value'),
    Input('user-ratings', 'data')
)

def reparseGraphView(cameraView,ratingData):
    '''
    This callback re-generates the matrix, but changes the view depending on the user's selection on the radio buttons.
    Maybe this can be split into two callbacks which determine if the graph needs to be reparsed or not?
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
    }

    scenes = {
            "Value vs. Study": {'yaxis': {}},
            "Study vs. Ambiance": {'yaxis': {'autorange':'reversed'}},
            "Value vs. Ambiance": {'zaxis': {'autorange':'reversed'}, 'yaxis': {'autorange':'reversed'}, 'xaxis': {'autorange':'reversed'}}
            # some views need to be reversed so the best review is always top+right+back.
    }

    camera = {"eye": views[cameraView]}
    # handles direction we're looking
    sceneDir = scenes[cameraView]

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
