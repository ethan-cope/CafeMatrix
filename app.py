#!./env/bin/python

from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px      
import plotly.graph_objects as go
import base64
from genMatrix import generateMatrix, generateShopBarChart, generateEmptyFigure, extractReviewsFromLocalTSV, extractReviewsFromUploadedTSV

# import json
# import pandas as pd
# not needed as of 11.26.2023

#TODO: user-definable scaling
#TODO: location selection
#TODO: better formatting for plotly graphs and different-sized screens
    # benchmark 13-inch computers since that's what most ppl have

# initial figure 
defaultView = 'Default' # Global variable, but read-only so should be ok
fig = px.scatter_3d()

colors = {
    'background': '#FFFDD1'
}
background = "#e5ecf6"

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
                       }
                ),

            ])
        ])
    ])

def drawModalStartupGuide():
    return [
        html.H4("Entering the Matrix",className="card-mono"),
        html.Ol( 
            children = [
                html.Li(children = ["Rate your favorite cafes with ", html.A("this spreadsheet template", href="https://docs.google.com/spreadsheets/d/1qIiK-8SHgQ4qp5Nry18LhIE_MRTTrKplktnkObQukdA/edit#gid=487713447",target="_blank"),"!"]), 
                html.Li(children = ["In Sheets, download the spreadsheet as a .tsv file:", html.P("(File > Download > Tab Separated Values (.tsv))", className="card-mono")]), 
                html.Li(children = ["Use the ", html.B("Upload ratings (.tsv)"), " button to warp your reviews to the Matrix!"]), 

            ]
        ),
        html.H4("Navigating the Matrix",className="card-mono"),
        html.Ol(children = [
            html.Li("Select a preset view, or click and drag the Matrix to your favorite angle!"),
            html.Li("Hover over a cafe datapoint to glance at its ratings."),
            html.Li("Click (or tap) a cafe datapoint for the most in-depth sub-matrix statistics."),
            html.Li("The Matrix remembers your reviews, storing them in your browser. No passwords needed!"),
            html.Li("Update the Matrix by uploading new .tsv."),
        ]),
        html.H4("Welcome to the CafeMatrix!", className="card-mono"),
    ]


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
                                ['Default', 'Value vs. Study','Study vs. Ambiance','Value vs. Ambiance'],
                                'Default',
                                id='axesSelectOption',
                                labelStyle={'marginTop':'5px',
                                            'cursor': 'pointer',}
                            ),
                        ]),

                        dbc.Col([
                            # you'll have to make this a method b/c this is way too big
                            html.H5("Enter the Matrix"),
                            dbc.Button("Get Started!", id="open", n_clicks=0, className = "btn-light",
                            style={             
                                  'width': '100%',             
                                  'height': '60px',             
                                  #'lineHeight': '60px',             
                                  #'borderWidth': '1px',             
                                  #'borderStyle': 'dashed',             
                                  #'borderRadius': '5px',             
                                  #'textAlign': 'center',             
                                  #'margin': '5px',
                                  #'cursor': 'pointer',
                            }),
                            # add a "support CafeMatrix bar that knows how whether our server costs are paid for or not!
                            dbc.Modal(
                                [
                                    dbc.ModalBody(drawModalStartupGuide()),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="close", className="ms-auto btn-light", n_clicks=0
                                        )
                                    ),
                                ],
                                id="modal",
                                size="lg",
                                is_open=False,
                            ),
                        ]),

                        dbc.Col([
                            html.H5("Update Matrix"),
                            dbc.Button("Get rating template", href = "https://docs.google.com/spreadsheets/d/1qIiK-8SHgQ4qp5Nry18LhIE_MRTTrKplktnkObQukdA/edit#gid=487713447", className = "btn-light",
                            style={             
                                    'width': '100%',             
                                    'height': '60px',             
                                    'display': 'flex',             
                                    'flexDirection': 'column',
                                    'justifyContent': 'center',
                                    'textAlign': 'center',             

                                  #'lineHeight': '60px',             
                                  #'borderWidth': '1px',             
                                  #'borderStyle': 'dashed',             
                                  #'borderRadius': '5px',             
                                  #'textAlign': 'center',             
                                  #'margin': '5px',
                                  #'cursor': 'pointer',
                            }),

                            dcc.Upload(         
                            id='upload-data',         
                            children=html.Div(
                                [             
                                    'Upload ratings (.tsv)'
                                ]),         
                                className = "btn btn-light",
                                style={             
                                    'width': '100%',             
                                    'height': '60px',             
                                    'display': 'flex',             
                                    'flexDirection': 'column',
                                    'justifyContent': 'center',
                                    'textAlign': 'center',             
                                },
                                # Allow multiple files to be uploaded         
                                # of course, actually trying to use multiple files breaks the program
                                # but I already wrote it to use the multiple option
                                # TODO:: change this it make multiple false.
                                multiple=True
                            ),     

                        ]),



                    ]),

                ])),

                dcc.Graph(
                    id='breakdown-graph',
                    style={'width':'90vh','height':'74vh'}
                )
            ])
        ])
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

# tried to make this client-side but it's hard to do. best to keep this combined for now.
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
        fig = generateEmptyFigure("No Matrix found. Get started now!")
        #raise PreventUpdate
    else:
        fig = generateMatrix(ratingData)
    views = {
            "Default": {'x': 1.35, 'y': 1.35, 'z': 2},
            "Value vs. Study": {'x': 2, 'y': 0, 'z': 0.1},
            "Study vs. Ambiance": {'x': 0.01, 'y': 2, 'z': 0},
            "Value vs. Ambiance": {'x': 0, 'y': 0.01, 'z': 2} 
    }

    scenes = {
            "Default": {},
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

# don't think we can generate this client-side, so we're stuck with this code
# hopefully minimal implications for performance / build minutes
@callback(
    Output('breakdown-graph', 'figure'),
    Input('big-matrix', 'clickData')
)
def displayBarChart(clickData):
    '''
    This callback generates the bar chart for the matrix the user clicks on.
    '''
    fig = go.Figure() 

    if clickData == None:
        fig = generateEmptyFigure(msg = "Select a datapoint to view the sub-matrix.")

    elif clickData:
        indexData = clickData["points"][0]['customdata'][1]
        shopName = (clickData["points"][0]['text'])
        fig = generateShopBarChart(indexData, shopName)
    return fig

@callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

App = Dash(
    __name__,
    title="CafeMatrix",
    # adding bootstrap
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

server = App.server

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

# uncomment for dev
#App.run_server(debug=True, use_reloader=True)

if __name__ == "__main__":
    #App.run_server(debug=True,use_reloader=True)
    App.run_server(port=5000, host='0.0.0.0',debug=True)

