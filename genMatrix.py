#!./env/bin/python
import plotly.express as px      
import plotly.graph_objects as go
from random import randrange
import hashlib

import pandas as pd

# coffee spreadsheeters, rejoice.
# hey, this should normalize so it scales to people always being nice, and has outliers and bar plots and stuff

DefaultSubIndices = [["vibe", "seating", "spark", "taste", "cost", "menu", "space", "tech", "access"], # name of sub-index
 ["ambianceIdx","ambianceIdx","ambianceIdx","valueIdx","valueIdx","valueIdx","studyIdx","studyIdx","studyIdx"], #parent index of subindex
 [5,5,5,5,5,5,5,5,5], # what the ranking is out of (changed everything to out of 5!!!)
 [5,3,2,5,3,2,4,3,3] # scaling of the ranking (makes everything in each category add up to 10
]

        # [AMBIANCE INDEX]
        # weightings of ambiance
        # [VIBE] - SUBJECTIVE ranking of decor / vibe from 0-5. 
        # [SEATING AVAILABILITY]["scaling"] - SEMI-SUBJECTIVE. How difficult was it to find seats? 0-5.
        # [SPARK]["scaling"] - SUBJECTIVE. Was there anything special not captured in the previous category? Nice baristas? fun games? Becomes a bar at night / open mic night? Activities / active part of community?  rank here, from 0-5. 

        # [VALUE INDEX]

        # [TASTE] - SUBJECTIVE ranking of how good the coffee was. 
        # [COST] - OBJECTIVE price of a cup of drip coffee here. 
        # [MENU / SPARK] - SUBJECTIVE ranking of specials, or quality. Do they roast or sell their own beans? Have cool specials? Good food / cocktails also? all that goes here. 

        # [STUDY INDEX]

        # weightings of study suitability index
        # [SPACE SUITABILITY] - SUBJECTIVE. whether the existing space is good suitable for studying.
        # 0-5 (not many spaces - normal - tons of space) 
        # [TECH-FRIENDLINESS] - OBJECTIVE ranking of internet functionality and outlet availability. 
        # 0-5, (spotty / nonfunctional internet - fine internet) ditto for outlets
        # [ACCESSIBILITY] - SEMI-OBJECTIVE ranking of how late / early it's open, and what days. 
        # Is it close to highways / public transit / easy to get to? Is parking good? 
        # 0-5. (hard to reach / bad hours - great hours / convenient location)

class ShopReview:

    # class variable of reviewIndices - we only want to set this once for all classes.
    IndicesMetadata = {}

    def __init__(self, rID, shopIndex, shopName, extraComments, ambianceIdx = 0, valueIdx = 0, studyIdx = 0):
        self.rID       = rID         # ID of specific review in RDBS
        self.shopIndex = shopIndex   # Index of shop being reviewed in RDBS
        self.shopName = shopName     # name of the shop being reviewed
        self.ambianceIdx = ambianceIdx
        self.valueIdx = valueIdx
        self.studyIdx = studyIdx

        self.subIndexData = {}

        self.Total  = 0
        self.extraComments = extraComments

    def initIndex(self):
        # turn spreadsheet into 2d array here, overwrite the existing array if so.
        # maybe only have this do something once, so we're not checking in with the ss for every rating.

        # set the CLASS VARIABLE to the spreadsheetmockupindex
        IndicesMeta2DArr = DefaultSubIndices 

        for subIndexCounter in range(len(IndicesMeta2DArr[0])):
            #print("generating subIndex for \"%s\"." % IndicesMeta2DArr[0][subIndexCounter])
            # example initialization:

            subIndexName = IndicesMeta2DArr[0][subIndexCounter]
            ShopReview.IndicesMetadata[subIndexName] = {}
            ShopReview.IndicesMetadata[subIndexName]["parentIdx"] = IndicesMeta2DArr[1][subIndexCounter]
            ShopReview.IndicesMetadata[subIndexName]["ratingOutOf"] = IndicesMeta2DArr[2][subIndexCounter]
            ShopReview.IndicesMetadata[subIndexName]["scaling"] = IndicesMeta2DArr[3][subIndexCounter]
            
   
    def calcIndices(self, ratings):
        if not self.IndicesMetadata:
            self.initIndex()

        # start of mouseover hover flavor text.
        hitsMissesString = "---------------<br>"
        missesString = ""
        hitsString = ""

        subIndexCounter = 0
        for subIndexName in ShopReview.IndicesMetadata.keys():
            # why -1? so 1/5 will equate to 0, and 3/5 will equate to average.
            percentVal = (ratings[subIndexCounter]-1) / (ShopReview.IndicesMetadata[subIndexName]["ratingOutOf"]-1)
            if percentVal < 0:
                percentVal = 0

            if ShopReview.IndicesMetadata[subIndexName]["parentIdx"] == "ambianceIdx":
                # using subIndexCounter to extract the same index from ratings row and subindex row
                self.ambianceIdx += percentVal * ShopReview.IndicesMetadata[subIndexName]["scaling"]
            elif ShopReview.IndicesMetadata[subIndexName]["parentIdx"] == "valueIdx":
                self.valueIdx += percentVal * ShopReview.IndicesMetadata[subIndexName]["scaling"]
            elif ShopReview.IndicesMetadata[subIndexName]["parentIdx"] == "studyIdx":
                self.studyIdx += percentVal * ShopReview.IndicesMetadata[subIndexName]["scaling"]

            # adding to hits/misses 
            # miss if it's < 20%, hit if it's > 80

                # all of this code also makes these strings pretty
            if (percentVal > .8):
                hitsString += "- %s (%s) <br>" % (subIndexName, ShopReview.IndicesMetadata[subIndexName]["parentIdx"][0:3].capitalize()) 

            elif (percentVal < .2):
                missesString += "- %s (%s) <br>" % (subIndexName, ShopReview.IndicesMetadata[subIndexName]["parentIdx"][0:3].capitalize()) 

            self.subIndexData[subIndexName] = {
                "parentIdx": ShopReview.IndicesMetadata[subIndexName]["parentIdx"],
                "rating":  ratings[subIndexCounter],
                "scaling": ShopReview.IndicesMetadata[subIndexName]["scaling"],
            }

            subIndexCounter += 1
        
        if hitsString :
            hitsString = "<b>Hits:</b><br>" + hitsString 

        if missesString :
            missesString = "<b>Misses:</b><br>" + missesString 

        hitsMissesString = hitsString + missesString
        self.Total = self.ambianceIdx + self.valueIdx + self.studyIdx

        # use the extra text to make a list of hits / misses 
        # this will get passed to the plot generator code

        modifiedCommentsString = ""
        # add line breaks to comments when hovered
        if self.extraComments is not None:
            #modifiedCommentsString = "<b>Comments:</b><br>" + interpolateLineBreaks(self.extraComments, 75)
            modifiedCommentsString = "<b>Comments:</b><br>" + interpolateLineBreaks(self.extraComments, 45)
            #modifiedCommentsString = "<b>Comments:</b><br>" + self.extraComments

        self.extraComments = hitsMissesString + modifiedCommentsString

    def __str__(self):
        return """Review %s 
of %s (IDX %s)
-----
Ambiance Index: %.01d / 10 
Value Index:    %.01d / 10
Study Index:    %.01d / 10
Total:          %.01d / 30
-----"""% (self.rID, self.shopName, self.shopIndex, self.ambianceIdx, self.valueIdx, self.studyIdx, self.Total)

    def toDfElement(self):
        # this is just a list of all of the class's elements
        return vars(self)

def generateShopBarChart(indexData, shopName):
    """This method generates a bar chart breakdown of the Cafe's submatrices.
    """
    fig = go.Figure()

    #TODO later: put the lowest rated index at the bottom of the bar chart (maybe by sorting dataframe?)

    # magic scaling that I no longer understand. one goal would be to make this user scalable 
    df = pd.DataFrame.from_dict(indexData, orient='index')
    row = (df.loc[:,"rating"] - 1)/4 * df.loc[:,"scaling"]
    df["normalizedVal"] = row
    df["normalizedScale"] = df.loc[:,"scaling"] * 10
    df["normalizedRate"] = df.loc[:,"rating"] - 1

    df["normalizedRate"] = df["normalizedRate"].clip(lower = 0) # magic replaces all negatives with 0
    df["normalizedVal"] = df["normalizedVal"].clip(lower = .25) # magic replaces all negatives with .25 (so the bar is still visible, doesn't affect ranking)
    
    # for df manipulation shenanigans
    # print(df)

    # note that the color range is a little strange.
    # bar graph colors are based on the subindex's POST SCALING value.
    # thus, the best color is 3.5 (the AVERAGE largest value an index can have), and the worst is at 0.

    fig = px.bar(df, 
                 x='parentIdx', 
                 y='normalizedVal', 
                 color='normalizedVal', 
                 color_continuous_scale='tropic',
                 range_color = [0,3.5], 
                 text=df.index,
                 title="SubMatrix: %s" % (shopName),
                 custom_data=["normalizedRate","normalizedScale","normalizedVal"] # here we're passing df values into graph
                 )

    fig.update_layout(barmode='stack', 
                      xaxis={'categoryorder':'category ascending'},
                      xaxis_title='Rating Index',
                      yaxis_title='Aggregate Rating',
                      coloraxis_colorbar=dict(title="SubIndex<br>Rating"),
                      )

    fig.update_yaxes(range=[0,10])
    fig.update_traces(marker_line_color = 'black', 
                      marker_line_width = 2, 
                      opacity = .55,
                      hovertemplate="<b>%{text}: %{customdata[0]} / 4</b><br>Weighting: %{customdata[1]}%<br>of total index "
                      )
    return fig



def generateMatrix(reviewsArray):
    """ accepts an array of review -> Dataframe elements 
        returns a figure that's the matrix
    """
    #print(json.dumps(reviewsArray[0], indent=2))
    df  = pd.DataFrame(reviewsArray)

    fig =  px.scatter_3d(df,
                         x='ambianceIdx',
                         y='valueIdx',
                         z='studyIdx', 
                         color='Total',
                         color_continuous_scale='Fall',
                         text="shopName",
                         # note that shopName was previously set as Text, but this looks ugly when too many cafes have been rated. I had to move it to custom_data[2]
                         custom_data=['extraComments', 'subIndexData', 'shopName'],
                         )

    fig.update_layout(
        scene = dict(
            xaxis = dict(range = [10,0]),
            xaxis_title='Ambiance Index',
            yaxis = dict(range = [0,10]),
            yaxis_title='Value Index',
            zaxis = dict(range = [0,10]),
            zaxis_title='Study Suitability Index',
        )
    )
    #fig.update_coloraxes(colorbar={'thickness':10})
    fig.update_coloraxes(colorbar={'orientation':'h','thickness':10})
    fig.update_layout(
        margin = dict(
            l=5,
            r=5,
            t=5,
            b=5,
        )
    )

    # add a short description of cafe on mouseover hover of point
    fig.update_traces(hovertemplate="<b>%{customdata[2]}</b><br>Ambiance Index: %{x}<br>Value Index: %{y}<br>Study Suitability Index: %{z}<br>%{customdata[0]}")

    #to add the names back in, you will need a different generation command

    return fig

def generateEmptyFigure(msg = "No rating data found!"):
    background = "#e5ecf6"
    fig = go.Figure() 
    #pretty blank figure
    fig.update_layout(
        paper_bgcolor=background,
        plot_bgcolor=background,    
        xaxis = dict(
            visible=False,
            showgrid=False,
            gridcolor=background,
            zerolinecolor=background),
        yaxis = dict(
            visible=False,
            showgrid=False,
            gridcolor=background,
            zerolinecolor=background
            ),
        annotations = [
            {
                "text": msg,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 22
                }
            }
        ]
    )

    return fig




def extractReviewsFromUploadedTSV(uploadedTSVData = ""):
    """
    This should operate the same as the other "extractreviews" method.
    it'll take in an array, with each index being a line of the TSV file.
    This allows for maximum crossover with code from the other example.

    Errors handled:
    - no comments section
    - not a long enough list (unfinished values)
    - values are not a number
    - value not between 1 and 5

    There will be more, but this is good for a 1.0!
    """

    reviewsArr = []


    if uploadedTSVData:

        rIdx = -1 #initialized to -1.
        # it gets set to 0 when we detect the row starting with "Shop Name", which signals that every further row is a cafe review

        for line in uploadedTSVData:

            # I think this latching thing works ok. no idea though.
            # now we're erroring with the index. I'll troubleshoot later 2/29/24

            latchLine = True
            if (rIdx == -1):
                # if we haven't latched (rIdx == -1, search for LatchLine
                for val in line.split('\t')[1:10]:
                    if not val.isdigit():
                        latchLine = False
                # if we make it through this loop and LL is still true, it's our latch line.
                if (latchLine == True):
                    rIdx = 0

            if rIdx != -1:
                rIdx += 1 # rIDx is the unique index of the review, NOT the cafe itself.
                # if we ever want to support multiple reviews of the same restaurant, etc.

                # parse TSV line into a Df, and add it to the dictionary
                reviewsArr.append(extractDfElementFromTSVString(rIdx,line))

#               except IndexError as e:
#                   print("%s\n Error generating indices for cafe. Continuing..." % (e))
#               except ValueError as e:
#                   print("%s\n Invalid Index: Continuing..." % (e))

    return reviewsArr

def extractDfElementFromTSVString(rIdx, TSVLine):
    """Accepts TSV string, Returns dataframe element"""
    lineArr=TSVLine.split('\t') 
    # hash the shop name, which will be compared for duplicate reviews of the same place if that's ever a feature to add
    # could be a good thing for future database integration
    # TODO (later): this this doesn't work... 
    uniqueShopIdx = hash(lineArr[0]) % 100000000 

    # initialize ShopReview object from the line
    r = ShopReview(rID = rIdx, shopIndex = uniqueShopIdx, shopName = lineArr[0], extraComments = lineArr[10] if len(lineArr) > 10 else "") 
    # If no comments, don't throw error (inline conditional)

    # calculate index information
    r.calcIndices(sanitizeRatingList(lineArr[1:10]))
    return r.toDfElement()

def compressDfElementToTSVString(dfElement):
    """Accepts dataframe element, Returns TSV string"""

    cafeName  = dfElement["shopName"]
    vibe      = dfElement["subIndexData"]["vibe"]["rating"]
    seating   = dfElement["subIndexData"]["seating"]["rating"]
    spark     = dfElement["subIndexData"]["spark"]["rating"]
    taste     = dfElement["subIndexData"]["taste"]["rating"]
    cost      = dfElement["subIndexData"]["cost"]["rating"]
    menu      = dfElement["subIndexData"]["menu"]["rating"]
    space     = dfElement["subIndexData"]["space"]["rating"]
    tech      = dfElement["subIndexData"]["tech"]["rating"]
    access    = dfElement["subIndexData"]["access"]["rating"]
    comments  = dfElement["extraComments"]

    # remove the "hits/misses" text which gets generated when the review is added
    # split by brs and take the last text which should be just the user's comments 
    if "<br>" in comments:
        comments = comments.split("<br>")[-1]

    line = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t" % (cafeName, vibe, seating, spark, taste, cost, menu, space, tech, access, comments)
    return line

def sanitizeRatingList(rawValues):
    """Accepts a list of ratings, returns a list of ratings that are scaled 0-5"""
    # this may no longer be necessary if I can find a way to implement form in a pythonic way
    ratingList = (list(map(lambda val: returnValidIndexValue(val), rawValues)))
    while(len(ratingList) < 9):
        ratingList.append(0)

    return ratingList

def interpolateLineBreaks(string, increment):
    """Accepts in a string (comments string
    Returns a strign with html <br> linebreaks interpolated
    """
    for i in range(increment, len(string), increment):
        # find the next space so we don't chop a word by mistake
        nextSpaceIndex = string.find(" ",i)
        # you could find a way to strip the space here this but it causes issues when we pull out the <br>s later
        string = string[:nextSpaceIndex] + "<br>" + string[nextSpaceIndex:]

    return string


def returnValidIndexValue(rawVal):
    """
    Coerce user's ranking into a 1-5 ranking
    """
    indexVal = int(rawVal)

    if indexVal < 1:
        indexVal = 1
    elif indexVal > 5:
        indexVal = 5
    #coerce into correct value

    return indexVal

def extractReviewsFromLocalTSV(localTSVPath = ""):
    # semi-useless method but good for debugging I guess
    """
    This method takes an a path to a local TSV (which I will shortly change as of 11/18/23) and spits out an array of review objects. 
    Why review objects? Because I wanted to mess with OOP even though a dictionary would have probably worked just as well. 0_0
    """
    reviewsArr = []

    if localTSVPath:
        # this is for testing 
        f = open(localTSVPath,"r")

        rIdx = 0
        for line in f:
            if line.split('\t')[0] == "Shop Name":
                continue
            else:
                rIdx += 1 # rIDx is the unique index of the review.
                reviewsArr.append(extractDfElementFromTSVString(rIdx,line))
                
    return reviewsArr

# this block generates a bunch of random reviews for testing purposes.

"""
shopNames = ["Ding Tea", "BoneAppleTea", "ShareTea", "Chatime", "TeaLattebar", "Starbucks"]
# generating a few reviews
r = ShopReview(rID = 0, shopIndex = 0, shopName = shopNames[0], extraComments = "Coffee") 
r.calcIndices([0,0,0,0,0,0,0,0,0])
reviews.append(r)

for i in range(0,len(shopNames)):
    idx = i
    r = ShopReview(rID = i, shopIndex = idx, shopName = shopNames[idx], extraComments = "This is a coffeeshop in Dallas, TX.<br> My thoughts should end here.<br> Maybe one more sentence.") 
    r.calcIndices([randrange(0,6),randrange(0,6),randrange(0,6), randrange(0,6),randrange(0,6),randrange(0,6), randrange(0,6),randrange(0,6),randrange(0,6)])
    reviews.append(r)
    print(r)
"""

"""
no need for this wrapper method anymore, renamed generateShopsMatrix to generateMatrix
def generateMatrix():
    reviews = extractReviewsFromLocalTSV(localTSVPath = "ratings.csv")
    reviews = extractReviewsFromUploadedTSV(externalTSVArray):
    figure = generateShopsMatrix(reviews)
    return figure
"""
