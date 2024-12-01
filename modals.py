from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# this file contains all of the modals and callbacks that deal with interactions with them.

# this callback opens the startup modal
@callback(
    Output("modalStartup", "is_open"),
    [Input("openStartupGuide", "n_clicks"), Input("closeStartup", "n_clicks")],
    [State("modalStartup", "is_open")],
)
def toggle_startup_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# this callback opens the tips modal
@callback(
    Output("modalTips", "is_open"),
    [Input("openTipsGuide", "n_clicks"), Input("closeTips", "n_clicks")],
    [State("modalTips", "is_open")],
)
def toggle_tips_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# this callback opens and closes the add review modal
# triggered when we request to add a new review, or interact with either button in the modal
@callback(
    Output("modalAddReview", "is_open"),
    Input("openAddReviewButton", "n_clicks"), 
    Input("closeAddReview", "n_clicks"),
    Input("addReviewButton", "n_clicks"),
    State("modalAddReview", "is_open"),
)
def toggle_addReview_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

# this callback opens and closes the backup matrix modal
# triggered when we add a new review or interact with either button in the modal
@callback(
    Output("modalDownloadBackup", "is_open"),
    Input("addReviewButton", "n_clicks"),
    Input("closeBackup", "n_clicks"),
    Input("downloadTSVModal", "n_clicks"),
    State("modalDownloadBackup", "is_open"),
)
def toggle_backup_modal(reviewAdded, n1, n2, is_open):
    if n1 or n2 or reviewAdded:
        return not is_open
    return is_open


def drawModalAddReview():
    return [
        html.H3("Add a Review",className="card-mono"),
        dbc.Col([
            dbc.Row([
                dbc.Card(
                    dbc.CardBody([
                        #html.H4("Cafe Name",className="card-mono"),
                        dbc.InputGroup([
                            dbc.InputGroupText("Cafe Name"),
                            html.Br(),
                            dbc.Input(id="cafeName", type="text", placeholder="Starbucks, etc.", required=True)
                        ]),
                        dbc.Textarea(id="comments", placeholder="Brief thoughts / opinions..."),
                        html.I("Tap a category for rating suggestions!")
                    ])
                )
            ]),
            dbc.Row([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Ambiance Ratings",className="card-mono"),
                        dbc.Row([
                            dbc.Col("Vibe (Coolness)", id="vibeTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'}, # poor
                                        3 : {'label':'good'}, # fine
                                        5 : {'label':'great!'}, # great
                                    },
                                    step=2,
                                    id="vibe"
                                )],width=8, className="inputSliderDiv")
                        ]),
                        dbc.Row([
                            dbc.Col("Seating (Availablity)", id="seatingTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'},
                                        3 : {'label':'good'},
                                        5 : {'label':'great!'},
                                    },
                                    step=2,
                                    id="seating"
                                )],width=8, className="inputSliderDiv")
                        ]),
                        dbc.Row([
                            dbc.Col("Spark (Quirkiness)", id="sparkTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'},
                                        3 : {'label':'good'},
                                        5 : {'label':'great!'},
                                    },
                                    step=2,
                                    id="spark"
                                )],width=8, className="inputSliderDiv")
                        ]),
                    ])
                ),
                dbc.Tooltip("Is the decor / vibe good?",target="vibeTT"),
                dbc.Tooltip("Are seats easy to find and the cafe non-crowded?",target="seatingTT"),
                dbc.Tooltip("Anything special about this place? Nice baristas? tabletop games? Becomes a bar at night? Active part of community?",target="sparkTT"),
            ]),
            dbc.Row([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Value and Taste Ratings",className="card-mono"),
                        dbc.Row([
                            dbc.Col("Taste", id="tasteTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'}, # poor
                                        3 : {'label':'good'}, # fine
                                        5 : {'label':'great!'}, # great
                                    },
                                    step=2,
                                    id="taste"
                                )],width=8, className="inputSliderDiv")
                        ]),
                        dbc.Row([
                            dbc.Col("Price", id="costTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'},
                                        3 : {'label':'good'},
                                        5 : {'label':'great!'},
                                    },
                                    step=2,
                                    id="cost"
                                )],width=8, className="inputSliderDiv")
                        ]),
                        dbc.Row([
                            dbc.Col("Menu Variety", id="menuTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'},
                                        3 : {'label':'good'},
                                        5 : {'label':'great!'},
                                    },
                                    step=2,
                                    id="menu"
                                )],width=8, className="inputSliderDiv")
                        ]),
                    ])
                ),
                dbc.Tooltip("How good do the drinks taste here?",target="tasteTT"),
                dbc.Tooltip("Are the drinks worth the price here?",target="costTT"),
                dbc.Tooltip("Do they have cool specialty drinks? Do they roast or sell their own beans? Good food / cocktails too? all that goes here.",target="menuTT"),

            ]),
            dbc.Row([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Study Suitability Ratings",className="card-mono"),
                        dbc.Row([
                            dbc.Col("Study Space", id="spaceTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'}, # poor
                                        3 : {'label':'good'}, # fine
                                        5 : {'label':'great!'}, # great
                                    },
                                    step=2,
                                    id="space"
                                )],width=8, className="inputSliderDiv")
                        ]),
                        dbc.Row([
                            dbc.Col("Outlets / WiFi", id="techTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'},
                                        3 : {'label':'good'},
                                        5 : {'label':'great!'},
                                    },
                                    step=2,
                                    id="tech"
                                )],width=8, className="inputSliderDiv")
                        ]),
                        dbc.Row([
                            dbc.Col("Hours / Accessibility", id="accessTT",className="inputSliderLabelDiv"),
                            dbc.Col([
                                dcc.Slider(1,5,
                                    value=3,
                                    marks={
                                        1 : {'label':'meh...'},
                                        3 : {'label':'good'},
                                        5 : {'label':'great!'},
                                    },
                                    step=2,
                                    id="access"
                                )],width=8, className="inputSliderDiv")
                        ]),
                    ])
                ),
                dbc.Tooltip("How good is the space for studying? Big tables? Lots of room to spread out?",target="spaceTT"),
                dbc.Tooltip("How fast is the internet here? Are there lots of charging outlets?",target="techTT"),
                dbc.Tooltip("How long does it stay open? Is it easy to park at or get to?",target="accessTT"),
            ]),

            #line = "Ding Tea	5	5	2	3	4	4	4	4	5	Somewhat loud local study spot. Couches for groups of 4.	"

            # generate review

            # invisible text box that becomes tab separated
            html.Div(id="generatedTSVString")
        
        ])
    ]




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
                                    html.B("Update > Add a Cafe Review."),
                                    html.Br(),
                                    html.Br(),
                                    "Then, fill in the cafe's Ambiance, Value, and Study Suitability categories from 1-5! Don't forget to add a name and any additional comments you have.",
                                ]
                            ),
                            html.Img(src="assets/addReviewFormat.jpg", className="img-fluid"),
                        ],
                        title = "1. Add a Cafe Review",
                    ),
                    dbc.AccordionItem(
                        [
                            html.P(children = [
                                    "Sometimes, browsers will delete the review data. If that happens, you can upload your .tsv backup file!",
                                    html.Br(),
                                    html.Br(),
                                    "Back on CafeMatrix.net, click the ", 
                                    html.B("Upload ratings (.tsv)"), 
                                    " button. Select your downloaded data (.tsv) file to populate the matrix!",
                                ]
                            ),
                        ],
                        title = "2. Upload backup matrix",
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

