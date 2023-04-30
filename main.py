import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from iso3166 import countries
from datetime import datetime, timedelta
df_data = pd.read_csv('mission_launches.csv')
df_data['Date']=pd.to_datetime(df_data['Date'],utc=True,format='mixed')
date = df_data['Date'].dt.year
date = pd.DataFrame(date)
country = df_data['Location'].str.split(' ').str[-1]
country = pd.DataFrame(country)
df_new = pd.concat([date,country],axis=1)
df_country = df_new.groupby(['Location'])['Date'].value_counts()
df_country = df_country.to_frame().sort_values('Location')
df_country = df_country.reset_index(level=['Date'])
df=df_data.drop('Price',axis=1)
df.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis = 1)
countries_dict = {
    'Russia' : 'Russian Federation',
    'New Mexico' : 'USA',
    "Yellow Sea": 'China',
    "Shahrud Missile Test Site": "Iran",
    "Pacific Missile Range Facility": 'USA',
    "Barents Sea": 'Russian Federation',
    "Gran Canaria": 'USA'
}
country_dict = dict()
df["country"] = df["Location"].str.split(", ").str[-1].replace(countries_dict)
for c in countries:
    country_dict[c.name] = c.alpha3
df["alpha3"] = df["country"]
df = df.replace({
    "alpha3":country_dict
})
df.loc[df["country"]== "North Korea","alpha3"] = "PRK"
df.loc[df["country"]== "South Korea","alpha3"] = "KOR"
df["country"] = df["Location"].str.split(", ").str[-1].replace(countries_dict)
sun = df.groupby(["country","Organisation","Mission_Status"])["Date"].count().reset_index()
figln2 = px.sunburst(sun, path = ["country", "Organisation", "Mission_Status"], values = "Date",)
df_map =df['country'].value_counts().reset_index()
country_dict = dict()
for c in countries:
    country_dict[c.name] = c.alpha3
df_map["alpha3"] = df_map["country"]
df_map = df_map.replace({
    "alpha3":country_dict
})
df_map.loc[df_map["country"]== "North Korea","alpha3"] = "PRK"
df_map.loc[df_map["country"]== "South Korea","alpha3"] = "KOR"
df_map.head()
fig_m = px.choropleth(df_map, locations = "alpha3", hover_name = "count", color = "country",)
df_ind = df.loc[df.Organisation=='ISRO'].reset_index(drop = True)
df_ind['rocket'] = df_ind['Detail'].str.split('|').str[0]
df_ind['Date'] = pd.to_datetime(df_ind['Date'],utc=True,format='mixed')
df_ind['year'] = df_ind['Date'].dt.year
df_roc = df_ind[['rocket','year']]
df_launch  = df_roc.groupby(['year'])['rocket'].value_counts().reset_index()
fig_ind = px.bar(df_launch,x='year',y='count',color='rocket')
df_success = df_ind[['rocket','Mission_Status']]
df_success = df_success.groupby(['rocket'])['Mission_Status'].value_counts().reset_index()
###APP LAYOUT
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
#Layout section
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Space Flight Analysis",
                        className='text-center text-white mb-4'),
                width=12)
    ),
dbc.Row([

        dbc.Col([
            html.H4("Launches per Year",className='text-center text-white'),
            dcc.Dropdown(id='my-dpdn', multi=False, value='Australia',
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df_country.index.unique())],
                         ),
            dcc.Graph(id='line-fig', figure={})
        ],width={'size':12,'offset':0, 'order':1},
        #xs=12, sm=12, md=12, lg=5, xl=5
        ),

], justify='center'),
    dbc.Row([
            dbc.Col([
            html.H4("Summary of Launches",className='text-center text-white'),
            dcc.Graph(id='line-fig2', figure= figln2)
        ],  width={'size':12,'offset':0, 'order':2},
            #xs=12, sm=12, md=12, lg=5, xl=5
    ),
    ]),
        dbc.Row([
            dbc.Col([
                html.H4("Total launches by each country",className='text-center text-white'),
                dcc.Graph(id='map-fig', figure= fig_m)
            ], width={'size': 12},
                # xs=12, sm=12, md=12, lg=5, xl=5
            )
]
),
dbc.Row(
        dbc.Col(html.H1("ISRO Analysis",
                        className='text-center text-white mb-4'),
                width=12)
    ),
dbc.Row([

        dbc.Col([
            html.H4("Rockets of Isro", className='text-center text-white'),
            dcc.Dropdown(id='my-ind', multi=False, value=1979,
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df_ind['year'].unique())],
                         ),
            dcc.Graph(id='ind-fig', figure={})
        ],width={'size':12,'offset':0, 'order':1},
        #xs=12, sm=12, md=12, lg=5, xl=5
        )
], justify='center'),
dbc.Row([

        dbc.Col([
            html.H4("Success of Rockets", className='text-center text-white'),
            dcc.Dropdown(id='my-roc', multi=False, value="ASLV ",
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df_success['rocket'].unique())],
                         ),
            dcc.Graph(id='ind-roc', figure={})
        ],width={'size':12,'offset':0, 'order':1},
        #xs=12, sm=12, md=12, lg=5, xl=5
        )
], justify='center'),

])

@app.callback(
    Output('line-fig', 'figure'),
    Input('my-dpdn', 'value')
)
def update_graph(stock_slctd):
    dff = df_country[df_country.index == stock_slctd]
    figln = px.bar(dff, x='Date', y='count')
    return figln
@app.callback(
    Output('ind-fig', 'figure'),
    Input('my-ind', 'value')
)
def update_graph(stock_slctd):
    dff = df_launch[df_launch['year'] == stock_slctd]
    figln = px.pie(dff, names = 'rocket', values='count')
    return figln
@app.callback(
    Output('ind-roc', 'figure'),
    Input('my-roc', 'value')
)
def update_graph(stock_slctd):
    dff = df_success[df_success['rocket'] == stock_slctd]
    figln = px.pie(dff, names = 'Mission_Status', values='count')
    return figln
# @app.callback(
#     Output('line-fig2', 'figure'),
#     Input()
# )
# def update_graph(stock_slctd):
#     sun = df.groupby(["country","Organisation","Mission_Status"])["Date"].count().reset_index()
#     figln2 = px.sunburst(sun, path = ["country", "Organisation", "Mission_Status"], values = "Date", title = "Sunburst Chart for some Countries")
#     return figln2
if __name__ == '__main__':
    app.run_server(debug=True, port=8000)