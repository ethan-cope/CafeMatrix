from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

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


