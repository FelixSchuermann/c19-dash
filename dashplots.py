import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import math
from flask import Flask
from dash.dependencies import Input, Output
server = Flask(__name__)
import random

"""
Dash web page for C19 visualisation
Data from "Our world in data" and destatis
"""
data= pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")
#data= pd.read_csv("owid-covid-data.csv")
deathdata = pd.read_csv("sterbefallzahlen.csv", delimiter =";")                 # manually download csv or register for API access @destatis


# stats about total amount of deaths
coronaweeklydeaths2020 = deathdata['2020 (davon COVID-19)']
deaths2020withoutcorona = deathdata['2020']-coronaweeklydeaths2020


def GetCountryData(countryname,table=data):
    return data[data.values==countryname]       #chose data from dataframe on specific country


def days_average(data_in,days,dfvalue):
    """
    calculation of test positive per last number of days (moving average)
    """
    dayavg=[]
    daydate=[]
    number_of_values = int(math.trunc(data_in.shape[0]/days))
    relevant_data= data_in[dfvalue]
    relevant_data= np.array(relevant_data)

    for l in range(0,data_in.shape[0]):
        if l <= days:
            print("days<7")
            pass
        else:
            avg = (np.sum(relevant_data[l-days:l])/days)
        dayavg.append(avg)
        daydate.append(np.array(data_in['date'])[l])

    return daydate, dayavg

#random color generation
number_of_colors = 52
color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(number_of_colors)]

#specifying styling colors
colors = {
    'background': '#111111',
    'text': '#000099',
    'plot_color': '#D3D3D3',
    'paper_color':'#3333ff',
    'fontcolor':'#FFFFFF'
}

#initializing graph data for first setup
cdata= GetCountryData("Germany")

xdaydates,ydayavg = days_average(cdata,7,'new_cases')

prate = np.array(cdata['positive_rate'])*100     # to percent
pratedates = cdata['date'][~np.isnan(prate)]     #removing empty columns from dataset and getting non-empty dates
prate = prate[~np.isnan(prate)]



def build_all_graphs(cdata,countryname,xdaydates,ydayavg,pratedates,prate):
    """
    Function to build first Graph, returning subgraphs and layout for use in dash Figure
    """

    newcases = go.Scatter(
                name="New Cases",
                x = cdata['date'],
                y = cdata['new_cases'],
                mode = 'markers',
                marker=dict(
                    color='LightSkyBlue',
                    size=2,
                    opacity=0.5,
                    line=dict(
                        color='LightSkyBlue',
                        width=2)),
                marker_color='LightSkyBlue',
                yaxis='y1'
                )

    casestotaldeaths=go.Scatter(
                name="Total Deaths",
                x = cdata['date'],
                y = cdata['total_deaths'],
                mode = 'lines',
                marker_color='#ff4d4d',
                #text=ger['new_cases'],
                yaxis='y1',
                fill='tozeroy',
                fillcolor='rgba(255, 77, 77,0.3)'
                )

    sevendays = go.Scatter(
                name="Seven Day Average",
                x = xdaydates,
                y = ydayavg,
                mode = 'lines+markers',
                #marker_color="#995c00",
                marker=dict(
                    color='#995c00',
                    size=1,
                    opacity=0.5),
                yaxis='y1',
                fill='tozeroy',
                fillcolor='rgba(255, 153, 0,0.8)'
                )

    percentpositive = go.Scatter(
                name="Positive Rate in Percent",
                x = pratedates,
                #y = ger['positive_rate'],
                y= prate,
                mode = 'lines+markers',
                line = dict(color='#ccffcc', width=2, dash='dot'),
                marker_color='#ccffcc',
                #text=ger['new_cases'],
                yaxis='y2'
                )


    layout = go.Layout(
                title={
                        'text': 'COVID-19 in {}'.format(countryname),
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                activeshape={"fillcolor": "#ff0000"},

                plot_bgcolor='#1a1a1a',
                paper_bgcolor=colors['background'],
                font= {'color' : colors['fontcolor']},
                xaxis = {'title': 'Date',"gridcolor":colors['background'],"gridwidth": 0.5},
                yaxis = {'title': 'Number of Test Positives', "gridcolor":colors['background'],"gridwidth": 0.5},
                yaxis2 = {'title': 'Test Positive in Percent', "gridcolor":"#4d4d4d","gridwidth": 0.5,'overlaying':'y','side':'right', "zerolinecolor": colors['background'] },
                #yaxis2=dict(title='Test Positive in Percent',overlaying='y',side='right', gridcolor= "#cccccc", gridwidth= 0.5),
                height = 700)



    return newcases, casestotaldeaths,sevendays, percentpositive, layout    # all subplots + layout


def getGermanIGraph(cdata,years201519avg):
    #Line Chart average Influenza Deaths
    gig  = go.Scatter(
                name="2015-2019 Influenza Deaths",
                x = cdata['date'],
                y = years201519avg,
                mode = 'lines',
                line = dict(color='firebrick', width=2, dash='dot'),
                marker_color='#ccffcc',
                #text=ger['new_cases'],
                yaxis='y1')
    return gig

## first initialization with germany on page load
newcases, casestotaldeaths,sevengraph,percentpositive,layout =build_all_graphs(cdata,"Germany",xdaydates,ydayavg,pratedates,prate)
fig = go.Figure(data = [newcases, casestotaldeaths,sevengraph,percentpositive], layout = layout)

# configuring dropdown menue
dropmenue= dcc.Dropdown(id='my_dropdown',
            options=[
                     {'label': 'Sweden', 'value': 'Sweden'},
                     {'label': 'Germany', 'value': 'Germany'},
                     {'label': 'France', 'value': 'France'},
                     {'label': 'Belgium', 'value': 'Belgium'},
                     {'label': 'Poland', 'value': 'Poland'},
                     {'label': 'Austria', 'value': 'Austria'},
                     {'label': 'Spain', 'value': 'Spain'},
                     {'label': 'Chile', 'value': 'Chile'},
            ],
            optionHeight=35,                    #height/space between dropdown options
            value='Germany',                    #dropdown value selected automatically when page loads
            disabled=False,                     #disable dropdown value selection
            multi=False,                        #allow multiple dropdown values to be selected
            searchable=False,                    #allow user-searching of dropdown values
            search_value='',                    #remembers the value searched in dropdown
            placeholder='Please select...',     #gray, default text shown when no option is selected
            clearable=True,                     #allow user to removes the selected value
            style={'fontSize': 16,'text-align': 'center','backgroundColor':'#1a1a1a'},
            )


# css stylesheets:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','/static/reset.css']

# setting up Dash App
app = dash.Dash(name='app1',server=server,assets_external_path=external_stylesheets)




# Graph for death of all causes in germany
deathgraph= dcc.Graph(
    id='deathstats-chart',
    figure = {
        'data':[
            go.Scatter(
            name="2020 without Corona",
            x = deathdata['Kalenderwoche'],
            y = deaths2020withoutcorona,
            #y = deathdata['2020 (davon COVID-19)'],
            mode = 'lines',
            line = dict(color='#e6e600', width=3, dash='dot'),
            marker_color='#ccffcc'
                        ),
            go.Scatter(
            name="2020",
            x = deathdata['Kalenderwoche'],
            y = deathdata['2020'],
            mode = 'lines',
            line = dict(color='firebrick', width=3),
            marker_color='#ccffcc',
            fill='tonexty'
            ),

            go.Scatter(
            name="2019",
            x = deathdata['Kalenderwoche'],
            y = deathdata['2019'],
            mode = 'lines',
            line = dict(color='#3399ff', width=1, dash='dot'),
            marker_color='#ccffcc',
            ),
            go.Scatter(
            name="2018",
            x = deathdata['Kalenderwoche'],
            y = deathdata['2018'],
            mode = 'lines',
            line = dict(color='#006600', width=1, dash='dot'),
            marker_color='#ccffcc',
            ),
            go.Scatter(
            name="2017",
            x = deathdata['Kalenderwoche'],
            y = deathdata['2017'],
            mode = 'lines',
            line = dict(color='#cc3399', width=1, dash='dot'),
            marker_color='#ccffcc',
            )

        ],
        'layout' : go.Layout(
            title= 'Deaths per Calender Week Germany',
            plot_bgcolor='#1a1a1a',
            paper_bgcolor=colors['background'],
            font= {'color' : colors['fontcolor']},
            xaxis = {'title': 'Week Number'},
            #yaxis = {'title': 'Total Deaths of all Causes', 'range': "[0,30000]"},
            yaxis= dict(range=[16000, 28000],title='Total deaths of all causes'),
            height = 700
        )}) # /deathgraph



# setting Page Layout:
app.layout = html.Div([dropmenue,
    dcc.Graph(id="graph", figure=fig),
    html.H6('Disclaimer: Usage of PCR / Antigen Tests differs between countries',style={'color': '#FFFFFF', 'fontSize': 14,'backgroundColor': '#1a1a1a','text-align': 'center'}),
    deathgraph
],style={'backgroundColor': '#1a1a1a', 'height':'2000px'})


"""
Callback functions
Changing graph values on dropdown callback
"""
@app.callback(
    Output("graph", "figure"),
    [Input("my_dropdown", "value")])
def build_graph(value):
    # init again with chosen country
    cdata= GetCountryData(value)

    xdaydates,ydayavg = days_average(cdata,7,'new_cases')
    prate = np.array(cdata['positive_rate'])*100
    pratedates = cdata['date'][~np.isnan(prate)]
    prate = prate[~np.isnan(prate)]

    # buildung graphs with countrydata
    newcases, casestotaldeaths, sevengraph,percentpositive, layout = build_all_graphs(cdata,value,xdaydates,ydayavg,pratedates,prate)

    # Average Influenza deathstats only available in germany:
    if value=='Germany':
        years201519avg=[23000]*cdata.shape[0]
        gig = getGermanIGraph(cdata,years201519avg)
        fig = go.Figure(data = [newcases, casestotaldeaths, sevengraph,percentpositive,gig], layout = layout)
    else:
        fig = go.Figure(data = [newcases, casestotaldeaths, sevengraph,percentpositive], layout = layout)

    return fig

if __name__ == '__main__':
    app.run_server(host="127.0.0.1",port=80,debug=True)
