#!./env/bin/python

from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px      
import plotly.graph_objects as go
import base64
from genMatrix import generateMatrix, generateShopBarChart, generateEmptyFigure, extractReviewsFromLocalTSV, extractReviewsFromUploadedTSV, extractDfElementFromTSVString, compressDfElementToTSVString
from modals import drawModalStartupGuide, drawModalTipsGuide, drawModalAddReview

#TODO Now: change user's guide and make popup confirmation for replacing a review instead of print statement.
#TODO Later: user-definable scaling
#TODO Later: location selection

DefaultTSV = """Index >	Ambiance Index			Value Index			Study Suitability Index				
Sub-Index >	vibe	seating	spark	taste	cost	menu	space	tech	access	comments	[reserved for future updates]
Sub-Index Description >	decor / overall cafe vibe	crowdedness / seating availability	subjective vibe improvers. friendly baristas, active community, etc.	overall beverage taste	5=cheapest, 1=most expensive	menu diversity, food offerings, and specials	cafe area is study-friendly. Large tables, not cramped, etc.	outlet accessibility, wifi availability / quality	how early / late it's open, how easy to get there	any other uncategorized thoughts	
Sub-Index Importance Scaling [WIP] >	50%	30%	20%	50%	30%	20%	40%	30%	30%		
Best	5	5	5	5	5	5	5	5	5	The best possible score for a cafe.	
Worst	1	1	1	1	1	1	1	1	1	The worst possible score for a cafe.	"""

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
    """This spits out the submatrix with the bar charts for reviews"""
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
                            html.P(
                                '',
                                id='breakdown-text',
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
        placement="bottom",
        is_open=False,
        style={'min-height':'80vh'}
        # TODO (later) - force this to horizontal for PC
    )

def drawIntroTipsModal():       
    '''
    This spits out 2 invisible guides on how to use the CafeMatrix.
    It also draws the modal that lets users enter a new review
    It's only called on page reload.
    These are found in the modals file.
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

        dbc.Modal(
            [
                dbc.ModalBody(drawModalAddReview()),
                dbc.ModalFooter(dbc.ButtonGroup([
                    dbc.Button(
                        "Discard Review", id="closeAddReview", className="ms-auto btn-danger", n_clicks=0
                    ),
                    dbc.Button(
                        "Add Review", id="addReviewButton", className="ms-auto btn-success", n_clicks=0
                    )
                ])),
            ],
            id="modalAddReview",
            size="lg",
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalBody("Back up your matrix?",className="card-mono"),
                dbc.ModalFooter(dbc.ButtonGroup([
                    dbc.Button(
                        "Don't back up", id="closeBackup", className="ms-auto btn-danger", n_clicks=0
                    ),
                    dbc.Button(
                        "Back up Matrix", id="downloadTSVModal", className="ms-auto btn-success", n_clicks=0
                    )
                ])),
            ],
            id="modalDownloadBackup",
            size="lg",
            is_open=False,
        )
    ])

def drawNavBar():
    return dbc.NavbarSimple(
        children = [
            dbc.NavItem(dbc.NavLink("Start!", id="openStartupGuide", n_clicks=0, style={"cursor":"pointer"})),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem([
                        html.Div(["Add a Cafe Review"], id="openAddReviewButton"),
                        #dbc.NavLink("Get Rating Template", id="downloadTSV", style={"cursor":"pointer"})
                    ]),

                    dbc.DropdownMenuItem(
                        dcc.Upload(         
                            id='upload-tsv-data',         
                            multiple=False,
                            children=html.Div([             
                                'Upload ratings (.tsv)'
                            ])         
                        ),     
                    ),

                    dbc.DropdownMenuItem([
                        dcc.Download(
                            id="downloadTSV", 
                        ),
                        html.Div(["Get Rating Template"], id="downloadTSVNavbar"),
                    ]),
                ],
                className="dropdown-menu-end",
                nav = True,
                in_navbar=True,
                label="Update"
            ),
            dbc.NavItem(dbc.NavLink("Tips", id="openTipsGuide", n_clicks=0, style={"cursor":"pointer"})),

        ],
        brand = "CafeMatrix",
        className = "card-mono"
    )

@callback(
    Output('downloadTSV', 'data'),
    State('user-ratings', 'data'),
    Input('downloadTSVNavbar', 'n_clicks'),
    Input('downloadTSVModal', 'n_clicks'),
    prevent_initial_call=True,
)
def func(storedData, Navbar_n_clicks, Modal_n_clicks):
    populatedTSVString = DefaultTSV
    
    for review in storedData:
        # make sure we don't duplicate the "Best" or "Worst" axis anchors (which is dumb but the only way to enforce the bounds :(
        if review["shopName"] != "Best" and review["shopName"] != "Worst":
            populatedTSVString +="\n"
            populatedTSVString += compressDfElementToTSVString(review)

    return dict(content=populatedTSVString, filename="localBackupCafeMatrix.tsv")

#   # this is a fallback of just sending a blank tsv. hopefully this doesn't need to be used but I'm keeping it here
#   return dcc.send_file(
#       "./CafeMatrixTemplate.tsv"
#   )

# this callback updates the cache with either the uploaded TSV or the new review
@callback(Output('user-ratings', 'data'),
          Input("addReviewButton", "n_clicks"),
          Input('upload-tsv-data', 'contents'),
          State('user-ratings', 'data'),

          State("cafeName", "value"),
          State("comments", "value"),

          State("vibe", "value"),
          State("seating", "value"),
          State("spark", "value"),
          
          State("taste", "value"),
          State("cost", "value"),
          State("menu", "value"),

          State("space", "value"),
          State("tech", "value"),
          State("access", "value"),

          prevent_initial_call=True,
          )
def update_cache_data(nclicks, contentData, stored_data, 
                      # the state indices
                      cafeName, comments,
                      vibe, seating, spark, 
                      taste, cost, menu, 
                      space, tech, access):
                      #downloadCheckboxValue):
    """
    This callback is triggered if the user uploads new data through the dialog boxes or they upload their own review
    """

    #print(nclicks, cafeName, vibe, seating, spark, taste, cost, menu, space, tech, access, comments)

    #TODO later: this is stateless but contentData and nclicks are consistent across sessions so we can't know which one to execute (doesn't flush)
    if contentData is None and (nclicks is None or nclicks == 0):
        # 2 ways to trigger callback - if both were a mistake then do this
        raise PreventUpdate

    elif contentData is not None:
        # if the callback was triggered by the upload button

        # octet stream decoding seems to work fine on linux and windows...
        contentData = contentData.split(',')[1]
        # dataString is the TSV file as a string
        dataString = base64.b64decode(contentData).decode('ascii').strip()
        # dataString = base64.b64decode(contentData).decode('utf-8').strip()
        dataArray=dataString.split('\n')

        return extractReviewsFromUploadedTSV(dataArray)

    elif nclicks != 0 and nclicks is not None:
        # if the callback was triggered by the user adding a new review

        # if this is their first review, use the default TSV
        if stored_data is None:
            localReviewData = extractReviewsFromUploadedTSV(DefaultTSV.split('\n'))

        # take stored data
        else:
            localReviewData = stored_data

        # if their added index isn't valid, don't do anything
        # if it is valid, calculate the tsv line for just the new shop
        #   if the review is for an existing shop, update that shop in the matrix 
        #   then download the TSV
        #   if the review is a new shop, add that shop to the matrix
        #   then download the TSV

        # validate user input
        if (cafeName is None):

            #TODO Later: inline input sanitization with client-side callbacks
            # note that the matrix will quietly coerce values that are outside the 1-5 boundaries to 1-5. it's a massive pain to introduce HTML form stuff since this is python instead of HTML.
            pass
            #print("you're dumb")

        else:
            # calculate ID of new review
            rIdx = localReviewData[-1]["rID"] + 1

            #line = "Ding Tea	5	5	2	3	4	4	4	4	5	Somewhat loud local study spot. Couches for groups of 4.	"
            line = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t" % (cafeName, vibe, seating, spark, taste, cost, menu, space, tech, access, comments)

            reviewDfElement = extractDfElementFromTSVString(rIdx, line)

            # if there's already a review for this cafe...
            for i in range(len(localReviewData)):
                # if we have a duplicate review, replace the existing review
                #print(localReviewData[i]["shopIndex"], " ---- ", reviewDfElement["shopIndex"])
                if localReviewData[i]["shopName"] == reviewDfElement["shopName"]:
                    #TODO - make this in the frontend
                    #print("replaced an existing review")
                    localReviewData[i] = reviewDfElement

                    return localReviewData
            
            # if the review is not a duplicate, then append it to the list.
            localReviewData.append(reviewDfElement)

        return localReviewData

    # to catch all other special cases I didn't think of
    else:
        raise PreventUpdate


# reparse the graph     
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
        fig = generateEmptyFigure("No rating data found. Add a rating or upload your backup file!")
        #raise Exception(str(ratingData))
        #raise PreventUpdate
    else:
        #print(ratingData)
        #raise Exception(str(ratingData))

        fig = generateMatrix(ratingData)
    views = {
            "Default": {'x': 1.4, 'y': 1.4, 'z': 2.2},
            "Value vs. Study": {'x': 2.1, 'y': 0, 'z': 0.1},
            "Study vs. Ambiance": {'x': 0.01, 'y': 2.1, 'z': 0},
            "Value vs. Ambiance": {'x': 0, 'y': 0.01, 'z': 2.1} 
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
    Output('breakdown-text','children'),
    Input('big-matrix', 'clickData'),
    [State('subMatrixCanvas','is_open')],
)
def displayBarChart(clickData, is_open):
    '''
    This callback generates the bar chart for the matrix the user clicks on.
    '''
    fig = go.Figure() 
    openStat = False
    shopDescription = ""

    if clickData == None:
        fig = generateEmptyFigure(msg = "Select a datapoint to view the sub-matrix.")

    elif clickData:
        indexData = clickData["points"][0]['customdata'][1]
        shopName = (clickData["points"][0]['text'])
        # description with the html stuff stripped out
        shopDescription = clickData["points"][0]['customdata'][0].split("Comments:</b><br>")[-1].replace("<br>","")
        fig = generateShopBarChart(indexData, shopName)
        openStat = not is_open

    return fig, openStat, shopDescription

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

if __name__ == "__main__":
    #App.run_server(debug=True,use_reloader=True)
    App.run_server(port=5000, host='0.0.0.0',debug=True)

