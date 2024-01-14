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
        html.Div(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P(children = [
                                    "Welcome to CafeMatrix, the only user-friendly decision matrix for coffeeshops!", 
                                    html.Br(),
                                    html.Br(),
                                    "Rate your favorite cafes in categories like ambiance, value, and study suitability. Then see how they stack up against other cafes you've been to! Deciding on a coffee shop has never been easier. Get started today!",
                                ]
                            ),
                            html.Img(src="assets/cafeMatrixCoolTopshot.jpg", className="img-fluid"),
                        ],
                        title = "0. Welcome to CafeMatrix!",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P(children = [
                                    "To get started, click ", 
                                    html.A("this link", href="https://docs.google.com/spreadsheets/d/1qIiK-8SHgQ4qp5Nry18LhIE_MRTTrKplktnkObQukdA/copy",target="_blank"),
                                    " to make your own copy of the template spreadsheet! ", 
                                    html.Br(),
                                    html.I("Note: You'll only do this step once."),
                                    ]
                            ),
                        ],
                        title = "1. Copy matrix template",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P(children = [
                                "In this template, every", 
                                html.B(" row  "),
                                "is a",
                                html.B(" unique cafe and your ratings of it. "),
                                "To add a new rating, simply start a new row with the cafe's name. ",
                                "Then fill in the cafe's Ambiance, Value, and Study Suitability categories from 1-5! ",
                                "",
                            ]),
                            html.Img(src="assets/addingNewCafeRedBlue.jpg", className="img-fluid"),
                        ],
                        title = "2. Rate your cafes",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P(children = ["Once you're done rating, export your data from Sheets with ",
                                    html.B("File > Download > Tab Separated Values (.tsv)"),
                                    "."
                                    ]
                                ),
                            html.Img(src="assets/downloadingAsTSV.jpg", className="img-fluid"),
                        ],
                        title = "3. Export your ratings",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P(children = [
                                    "Back on CafeMatrix.net, click the ", 
                                    html.B("Upload ratings (.tsv)"), 
                                    " button. Select your downloaded data (.tsv) file to populate the matrix!",
                                    html.Br(),
                                    html.I("Note: to update the matrix, just repeat steps 2-4!")
                                ]
                            ),
                        ],
                        title = "4. Upload to matrix",
                    ),
                ]
            )
        )
    ]

def drawModalTipsGuide():
    return [
        html.H4("Matrix Tips",className="card-mono"),
        html.Div(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                    #html.Li("Select a preset view, or click and drag the Matrix to your favorite angle!"),
                        [
                            html.P(children = [
                                    "Click the  the buttons in ",
                                    html.B("View Options "),
                                    "to see the preset views. ",
                                    "You can also click and drag to rotate the matrix manually."
                                ]
                            ),
                        ],
                        title = "0. View Options",
                    ),
                    dbc.AccordionItem(
                        [
                            #html.Li("Hover over a cafe datapoint to glance at its ratings."),
                            html.P(children = [
                                    html.B("Hovering "),
                                    "over a cafe datapoint displays an overview of it's rankings.",
                                    ]
                            ),
                            html.Img(src="assets/hoverDemo.jpg", className="img-fluid"),
                        ],
                        title = "1. Matrix Interactions",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P(children = [

                                    html.B(" Clicking"),
                                    " a datapoint in the matrix generates an in-depth sub-matrix bar chart."
                                ]
                            ),
                            html.Img(src="assets/subMatrixDemo.jpg", className="img-fluid"),
                        ],
                        title = "2. Sub-Matrix Breakdowns",
                    ),

                    dbc.AccordionItem(
                        [
                            html.P(children = [
                                    "The matrix stores the ranking data in your browser. This means no logins, and no need to re-upload!",
                            ]),
                        ],
                        title = "3. Matrix Memory",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P(children = [
                                    "To update the matrix, modify the template spreadsheet and upload it again!"
                                    ]
                                ),
                        ],
                        title = "4. Updating the matrix",
                    )
                ]
            )
        )
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
                            html.H5("Enter the Matrix"),
                            dbc.Button("Get Started!", id="openStartupGuide", n_clicks=0, className = "btn-light",
                            style={             
                                  'width': '100%',             
                                  'height': '60px',             
                            }),
                            # add a "support CafeMatrix bar that knows how whether our server costs are paid for or not!

                            dbc.Button("Matrix Tips", id="openTipsGuide", n_clicks=0, className = "btn-light",
                            style={             
                                  'width': '100%',             
                                  'height': '60px',             
                            }),

                            dbc.Modal(
                                [
                                    dbc.ModalBody(drawModalStartupGuide()),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="closeStartup", className="ms-auto btn-light", n_clicks=0
                                        )
                                    ),
                                ],
                                id="modalStartup",
                                size="lg",
                                is_open=False,
                            ),

                            dbc.Modal(
                                [
                                    dbc.ModalBody(drawModalTipsGuide()),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close", id="closeTips", className="ms-auto btn-light", n_clicks=0
                                        )
                                    ),
                                ],
                                id="modalTips",
                                size="lg",
                                is_open=False,
                            ),

                        ]),

                        dbc.Col([
                            html.H5("Update Matrix"),
                            dbc.Button("Get rating template", href = "https://docs.google.com/spreadsheets/d/1qIiK-8SHgQ4qp5Nry18LhIE_MRTTrKplktnkObQukdA/copy", className = "btn-light",
                            style={             
                                    'width': '100%',             
                                    'height': '60px',             
                                    'display': 'flex',             
                                    'flexDirection': 'column',
                                    'justifyContent': 'center',
                                    'textAlign': 'center',             
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

# this callback opens the startup modal
@callback(
    Output("modalStartup", "is_open"),
    [Input("openStartupGuide", "n_clicks"), Input("closeStartup", "n_clicks")],
    [State("modalStartup", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# this callback opens the tips modal
@callback(
    Output("modalTips", "is_open"),
    [Input("openTipsGuide", "n_clicks"), Input("closeTips", "n_clicks")],
    [State("modalTips", "is_open")],
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

