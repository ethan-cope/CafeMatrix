#!./env/bin/python

from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px      
import plotly.graph_objects as go
import base64
from genMatrix import generateMatrix, generateShopBarChart, generateEmptyFigure, extractReviewsFromLocalTSV, extractReviewsFromUploadedTSV
from guides import drawModalStartupGuide, drawModalTipsGuide

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
    return  dbc.Col([
                dbc.Row([
                    html.Div([dcc.Graph(
                        figure=fig, 
                        id='big-matrix',
                        style={
                            #'minWidth': '65vw',
                            #'maxheight': '100vh',
                            #'width': '93 vw',
                            #'minheight': '80 vh',
                            'cursor':'pointer',
                            }
                        ),

                    ],  className="ratio", 
                             #style={'minHeight': '80vh'}
                             style={'--bs-aspect-ratio': '130%', 'max-height' : '73vh'}
                    )
                   ]),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("View Options", className="card-mono"),
                                html.Div([
                                    dbc.RadioItems(
                                        ['Default', 'Value vs. Study','Study vs. Ambiance','Value vs. Ambiance'],
                                        'Default',
                                        inline=True,
                                        id='axesSelectOption',
                                        labelStyle={'marginTop':'5px',
                                                    'cursor': 'pointer',}
                                    )
                                    ],
                                    style={"gap":"10px"},
                                ),
                            ])
                        ])
                    ])
                ],
                className=".order-sm-1",
                ),
            ])

def drawSubMatrix():
    return dbc.Offcanvas([
            dbc.Col([
                dbc.Row([
                    #dbc.Card([
                        #dbc.CardBody([
                            dcc.Graph(
                                id='breakdown-graph',
                                style={
                                    'height':'65vh'
                                    }
                            ),
                        #])
                    #])
                ])
            ]
                    #,style={'max-width':'90vw',
                    # 'min-width':'75vw',}
            )
        ],
        id="subMatrixCanvas",
        is_open=False,
        style={'min-width':'75vw'}
    )



def drawIntroTipsModal():       
    '''
    This spits out 2 invisible guides on how to use the CafeMatrix.
    It's only called on page reload.
    '''
    return html.Div([
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
    ])

def drawNavBar():
    return dbc.NavbarSimple(
        children = [
            dbc.NavItem(dbc.NavLink("Start!", id="openStartupGuide", n_clicks=0, style={"cursor":"pointer"})),
            dbc.NavItem(dbc.NavLink("Tips", id="openTipsGuide", n_clicks=0, style={"cursor":"pointer"})),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem(dbc.NavLink("Get Rating Template", href="https://docs.google.com/spreadsheets/d/1qIiK-8SHgQ4qp5Nry18LhIE_MRTTrKplktnkObQukdA/copy", style={"cursor":"pointer"})),
                    dbc.DropdownMenuItem(
                        dcc.Upload(         
                            id='upload-data',         
                            multiple=False,
                            children=html.Div([             
                                'Upload ratings (.tsv)'
                            ])         
                        ),     
                    ),
                ],
                className="dropdown-menu-end",
                nav = True,
                in_navbar=True,
                label="Update"
            )



        ],
        brand = "CafeMatrix",
        className = "card-mono"
    )
 

@callback(Output('user-ratings', 'data'),
          Input('upload-data', 'contents'),
          State('user-ratings', 'data'))
def update_output(contentData, stored_data):
    """
    This callback is triggered if the user uploads new data through the dialog boxes.
    """
    if contentData is None:
        raise PreventUpdate

    # octet stream decoding seems to work fine on linux and windows...

    contentData = contentData.split(',')[1]
    # dataString is the TSV file as a string
    dataString = base64.b64decode(contentData).decode('ascii').strip()
    # dataString = base64.b64decode(contentData).decode('utf-8').strip()
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
    if ratingData is None or not ratingData:
        fig = generateEmptyFigure("Error parsing rating data.")
        #raise Exception(str(ratingData))
        #raise PreventUpdate
    else:
        #print(ratingData)
        #raise Exception(str(ratingData))

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
    Output('subMatrixCanvas','is_open'),
    Input('big-matrix', 'clickData'),
    [State('subMatrixCanvas','is_open')],
)
def displayBarChart(clickData, is_open):
    '''
    This callback generates the bar chart for the matrix the user clicks on.
    '''
    fig = go.Figure() 
    openStat = False

    if clickData == None:
        fig = generateEmptyFigure(msg = "Select a datapoint to view the sub-matrix.")

    elif clickData:
        indexData = clickData["points"][0]['customdata'][1]
        shopName = (clickData["points"][0]['text'])
        fig = generateShopBarChart(indexData, shopName)
        openStat = not is_open

    return fig, openStat

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
    drawNavBar(),
    dbc.Container([
        drawSubMatrix(),
        drawCafeMatrix(),
        drawIntroTipsModal(),
        dcc.Store(id='user-ratings', storage_type='local')
    ], fluid=True)
])

# uncomment for dev
#App.run_server(debug=True, use_reloader=True)

if __name__ == "__main__":
    #App.run_server(debug=True,use_reloader=True)
    App.run_server(port=5000, host='0.0.0.0',debug=True)

