#!./env/bin/python
import plotly.express as px      
import plotly.graph_objects as go
from random import randrange

import numpy  as np
import pandas as pd

# coffee spreadsheeters, rejoice.
# hey, this should normalize so it scales to people always being nice, and has outliers and bar plots and stuff

DefaultSubIndices = [["vibe", "seating", "spark", "taste", "cost", "menu", "space", "tech", "access"], # name of sub-index
 ["ambianceIdx","ambianceIdx","ambianceIdx","valueIdx","valueIdx","valueIdx","studyIdx","studyIdx","studyIdx"], #parent index of subindex
 [5,2,2,5,2,2,2,2,2], # what the ranking is out of
 [1,1.5,1,1,1.5,1,2,1.5,1.5] # scaling of the ranking (makes everything in each category add up to 10
]

        # [AMBIANCE INDEX]
        # weightings of ambiance
        # [VIBE] - SUBJECTIVE ranking of decor / vibe from 0-5. 
        # [SEATING AVAILABILITY]["scaling"] - SEMI-SUBJECTIVE. How difficult was it to find seats? 0-2.
        # [SPARK]["scaling"] - SUBJECTIVE. Was there anything special not captured in the previous category? Nice baristas? fun games? Becomes a bar at night / open mic night? Activities / active part of community?  rank here, from 0-2. 

        # [VALUE INDEX]

        # [TASTE] - SUBJECTIVE ranking of how good the coffee was. 
        # [COST] - OBJECTIVE price of a cup of drip coffee here. 
        # [MENU / SPARK] - SUBJECTIVE ranking of specials, or quality. Do they roast or sell their own beans? Have cool speicals? Good food / cocktails also? all that goes here. 

        # [STUDY INDEX]

        # weightings of study suitability index
        # [SPACE SUITABILITY] - SUBJECTIVE. whether the existing space is good suitable for studying.
        # 0-2 (not many spaces - normal - tons of space) 
        # [TECH-FRIENDLINESS] - OBJECTIVE ranking of internet functionality and outlet availability. 
        # 0-2, (spotty / nonfunctional internet - fine internet) ditto for outlets
        # [ACCESSABILITY] - SEMI-OBJECTIVE ranking of how late / early it's open, and what days. 
        # Is it close to highways / public transit / easy to get to? Is parking good? 
        # 0-2. (hard to reach / bad hours - great hours / convenient location)


class ShopReview:

    # class variable of reviewIndices - we only want to set this once for all classes.
    IndicesMetadata = {}

    def __init__(self, rID, shopIndex, shopName, extraComments, ambianceIdx = 0, valueIdx = 0, studyIdx = 0):
        self.rID       = rID         # holdover from desire to make this a review aggregator.
        self.shopIndex = shopIndex   # holdover from desire to make this a review aggregator. 
        self.shopName = shopName     # name of the shop being reviewed
        self.ambianceIdx = ambianceIdx
        self.valueIdx = valueIdx
        self.studyIdx = studyIdx

        self.subIndices = {}

        self.Total  = 0
        self.extraComments = extraComments

    def initIndex(self, spreadSheetMatrix):
        # this should only pull data from the spreadsheet once. Once that's been done, we just use the class.
        # this will eventually calcIdx from a spreadsheet. but for now, just do what we do.

        # turn spreadsheet into 2d array here, overwrite the existing array if so.
        # maybe only have this do something once, so we're not checking in with the ss for every rating.

        if not spreadSheetMatrix and not self.IndicesMetadata:
            # if we're not using the spreadsheet's values, use the default matrix
            print("No spreadsheet provided. Using default sub-indices.")
            # set the CLASS VARIABLE to the spreadsheetmockupindex
            IndicesMeta2DArr = DefaultSubIndices 
        else:
            # verify that everything adds up to 10 here
            print("User-defined sub-indices detected. Be sure to verify that everything adds up to 10!")
 

        for subIndexCounter in range(len(IndicesMeta2DArr[0])):
            print("generating subIndex for \"%s\"." % IndicesMeta2DArr[0][subIndexCounter])
            # example initialization:
            # subIndices["vibe"]    = {"parentIdx":"","rating":0,"ratingOutOf":0,"scaling":0} 

            subIndexName = IndicesMeta2DArr[0][subIndexCounter]
            ShopReview.IndicesMetadata[subIndexName] = {}
            ShopReview.IndicesMetadata[subIndexName]["parentIdx"] = IndicesMeta2DArr[1][subIndexCounter]
            ShopReview.IndicesMetadata[subIndexName]["ratingOutOf"] = IndicesMeta2DArr[2][subIndexCounter]
            ShopReview.IndicesMetadata[subIndexName]["scaling"] = IndicesMeta2DArr[3][subIndexCounter]
            
   
    def calcIndices(self, ratings):
        # this needs to be done for each method, since we don't want to call the spreadsheet but do want to 

        # maybe just always call this when initializing... good performance improvement
        if not self.IndicesMetadata:
            self.initIndex([])


        subIndexCounter = 0
        for subIndexName in ShopReview.IndicesMetadata.keys():
            if ShopReview.IndicesMetadata[subIndexName]["parentIdx"] == "ambianceIdx":
                # using subIndexCounter to extract the same index from ratings row and subindex row
                self.ambianceIdx += ShopReview.IndicesMetadata[subIndexName]["scaling"] * ratings[subIndexCounter]
            elif ShopReview.IndicesMetadata[subIndexName]["parentIdx"] == "valueIdx":
                self.valueIdx += ShopReview.IndicesMetadata[subIndexName]["scaling"] * ratings[subIndexCounter]
            elif ShopReview.IndicesMetadata[subIndexName]["parentIdx"] == "studyIdx":
                self.studyIdx += ShopReview.IndicesMetadata[subIndexName]["scaling"] * ratings[subIndexCounter]

            subIndexCounter += 1

        self.Total = self.ambianceIdx + self.valueIdx + self.studyIdx

    def __str__(self):
        return """Review %s 
of %s (IDX %s)
-----
Ambiance Index: %.1d / 10 
Value Index:    %.1d / 10
Study Index:    %.1d / 10
Total:          %.1d / 30
-----"""% (self.rID, self.shopName, self.shopIndex, self.ambianceIdx, self.valueIdx, self.studyIdx, self.Total)

    def toDfElement(self):
        # this is just a list of all of the class's elements
        return vars(self)

    def generateShopBarChart(self):
        #returns a figure of the review's breakdown
        print('nothing yet')

        #x_data = [[self.

def generateShopsMatrix(reviewsArray):
    # accepts an array of reviews for different coffee shops
    # returns a figure that's the matrix
    dfArray = list(map(lambda r: r.toDfElement(),reviewsArray))
    df  = pd.DataFrame(dfArray)

    # now find a good way to print this boy
    fig =  px.scatter_3d(df,
                         x='ambianceIdx',
                         y='valueIdx',
                         z='studyIdx', 
                         color='Total',
                         color_continuous_scale='Fall',
                         text='shopName',
                         hover_name='shopName',
                         )

    fig.update_layout(scene = dict(
        xaxis = dict(range = [10,0]),
        xaxis_title='Ambiance Index',
        yaxis = dict(range = [10,0]),
        yaxis_title='Value Index',
        zaxis = dict(range = [0,10]),
        zaxis_title='Study Suitability Index',
        ))

    # making hover look pretty 
    fig.update_traces(hovertemplate="<b>%{text}</b><br>Ambiance Index: %{x}<br>Value Index: %{y}<br>Study Suitability Index: %{z}")

    return fig

reviews = []

shopNames = ["Ding Tea", "BoneAppleTea", "ShareTea", "Chatime", "TeaLattebar", "Starbucks"]

# generating a few reviews

r = ShopReview(rID = 0, shopIndex = 0, shopName = shopNames[0], extraComments = "") 
r.calcIndices([5,2,2,5,2,2,2,2,2])

for i in range(0,len(shopNames)):
    idx = i
    r = ShopReview(rID = i, shopIndex = idx, shopName = shopNames[idx], extraComments = "") 
    r.calcIndices([randrange(0,6),randrange(0,3),randrange(0,2), randrange(0,6),randrange(0,3),randrange(0,2), randrange(0,3),randrange(0,3),randrange(0,2)])
    reviews.append(r)
    print(r)

review = reviews[0]
#figure = review.generateShopBarChart()
figure = generateShopsMatrix(reviews)
figure.show()

# have a thing on mouse-over for what people say about it (bad internet, etc)
