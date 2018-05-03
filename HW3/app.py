# imports
import altair as alt
import pandas as pd
import json
from flask import Flask, Response
#import urllib.request, json


app = Flask(__name__, static_url_path='', static_folder='.')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/vis/<zipcode>')
def hello(zipcode):
    df = dataPull(zipcode)
    response = ''
    if df is not None:
        response = createChart(df).to_json()

    return Response(response,
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

# function for arranging data on called zipcode in a df

# function for arranging data on called zipcode in a df

def dataPull(zipcode):
    """
    Function to read in restaurant data per zip from
    Json file and convert to dataframe
    """
    # loading data
    data = json.load(open('nyc_restaurants_by_cuisine.json', 'r'))

    # Create empty array for storing data
    cuisine = []

    # Run function for specified zipcode to detrmine all cuisine types and number of restaurants
    for i in range(len(data)):

        # Try-except to ensure if the key does not exist for that zip a 0 value is pulled
        try:
            # Append array with actual value
            cuisine.append([data[i]['cuisine'], data[i]['perZip'][zipcode]])
        except KeyError:
            # Append array with 0
            cuisine.append([data[i]['cuisine'],0])


    # Store as dataframe
    zipdf = pd.DataFrame(cuisine, columns=['cuisine','perZip']).sort_values('perZip', ascending=False)[:15]

    # If incorrect zipcode, sum will be zero. To ensure empty plot is returned
    if zipdf.perZip.sum() == 0:
        zipdf = 0

    return zipdf

# chart of cuizines by zipcode

def createChart(data):
    color_expression    = "highlight._vgsid_==datum._vgsid_"
    #color_condition     = alt.ConditionalPredicateValueDef(color_expression, "SteelBlue")
    highlight_selection = alt.selection_single(name="highlight", empty="all", on="mouseover")
    rating_selection    = alt.selection_single(name="rating", empty="all", encodings=['y'])
    maxCount            = int(data['restaurants'].max())

    barMean = alt.Chart() \
        .mark_bar(stroke="Black") \
        .encode(
            alt.X("mean(restaurants):Q", axis=alt.Axis(title="Restaurants")),
            alt.Y('cuisine:O', axis=alt.Axis(title="Cuisine"),
                  sort=alt.SortField(field="restaurants", op="mean", order='descending')),
            alt.ColorValue("LightGrey"),#, condition=color_condition), # Remove color condition
        ).properties(
            width=200,
            height=350,
            selection = highlight_selection+rating_selection,
        )

    return alt.hconcat(barMean,
        data=data
    )
