import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_table
import dash_daq as daq
import dash_auth




#Import dataframes

users = pd.read_csv('users.csv')
additionals = pd.read_csv('additionals.csv')

additionals.rename(columns={'user_name':'name'}, inplace=True)

df= pd.merge(users,additionals,on='name')

#Clean Data

df.drop_duplicates('name',inplace=True, keep='first')
df.drop(['user_id','Id'],1,inplace=True)
df.fillna('not_defined',inplace=True)


#Customize Time for Users graph over time

import datetime as dt
df['created_at'] = df['created_at'].apply(lambda x: x.replace('/','-'))
df['created_at'] = pd.to_datetime(df['created_at'], format='%m-%d-%Y')
df['Day'] = df['created_at'].dt.day
df['Week'] = df['created_at'].dt.week
df['Month'] = df['created_at'].dt.month
df['Year'] = df['created_at'].dt.year

print(df.head())

#Fix special columns

df["Gender"]= df["Gender"].str.replace("Female", "Mujer")
df["Gender"]= df["Gender"].str.replace("Male", "Hombre")


#Programing Languages for Table
pro_language = df.groupby(['programming_language_name','Gender']).id.count().reset_index()
pro_language.rename(columns={'id':'Number_of_Users'},inplace=True)
suma = pro_language.Number_of_Users.sum()
pro_language['UsersPercentage'] = ((pro_language.Number_of_Users / suma) * 100).round(1)
pro_language.sort_values(by='Number_of_Users',ascending=False,inplace=True)
pro_language.rename(columns={'programming_language_name':'language','Number_of_Users':'Users'},inplace=True)


#Growth

growth = df.groupby(['created_at','Day','Week','Month','Year',]).id.count().reset_index()
growth.rename(columns={'id':'Number_of_Users'},inplace=True)

#Countries
countries = df.groupby('country_name').id.count().reset_index()
countries.rename(columns={'id':'Number_of_Users'},inplace=True)
sum_count = countries.Number_of_Users.sum()
countries['UsersPercentage'] = ((countries.Number_of_Users / sum_count) * 100).round(1)
countries.sort_values(by='Number_of_Users',ascending=False,inplace=True)
countries.rename(columns={'country_name':'Country','Number_of_Users':'Users'},inplace=True)
countries.loc[countries['Users'] <10, 'Country'] = 'other countries'


# Define app and style and Auth

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


USERNAME_PASSWORD_PAIRS =  [['username','password'],['Jamesbond','007']]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


#Static figures

fig2 = go.Figure(data=go.Scatter(x=growth.created_at, y=growth.Number_of_Users))
fig2.update_layout(autosize=False,width=800,height=500)
fig2.update_layout(title_text='Monthly Users Growth',title_font_size=18,title_x=0.5)
fig2.update_layout(xaxis_title='Time',yaxis_title='Number of Users')


fig4 = px.pie(countries,names='Country',values='Users')
fig4.update_layout(title_text='Users Distribution', title_font_size=18, title_x=0.5)
fig4.update_layout(margin=dict(t=60, b=45, l=0, r=0))

# App layout

app.layout = html.Div([
    html.H1(children='Datasource Data Monitor',style={'textAlign':'center','color':'green'}),
    daq.LEDDisplay(
        id='myusers',
        label='Users',
        value=df['id'].count(),
        labelPosition='bottom',
        size=50,
        color="green"
    ),
    dcc.Slider(
        id='month-slider',
        updatemode='mouseup',
        min=df['Month'].min(),
        max=df['Month'].max(),
        value=df['Month'].min(),
        marks= {str(month): str(month) for month in df['Month'].unique()},
        step=1

    ),
        html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=html.Div([

                    dcc.Dropdown(
                        id='profiles',
                        value='Education',
                        options=[
                            {'label':'Education','value':'Education'},
                            {'label':'Work','value':'Work'},
                            {'label':'Training','value':'Training'},
                            {'label':'Experience','value':'Experience'},
                            {'label':'Employment','value':'Employment'},
                        ],placeholder="Select Profile",


                    ),
                    dcc.Graph(
                        id='left-graph1',

                    ),

                    dash_table.DataTable(
                        id= 'data-table',
                        data=pro_language.to_dict('records'),
                        style_cell={'text_align':'center','font_size': '18px',},
                        style_header={ 'border': '1px solid green' },
                        columns=[{'id': c, 'name': c,'selectable':True} for c in pro_language.columns],
                        editable=True,
                        filter_action="native",
                        page_action="native",
                        page_current= 0,
                        page_size= 10
                ),


                    dcc.Graph(
                        id='left-Graph3',
                        figure=fig4
                    )



            ]),

        ),
            html.Div(
                className="six columns",
                children=html.Div([
                    dcc.Graph(
                        id='right-top-graph',
                    ),
                    dcc.Graph(
                        id='right-bottom-graph',
                        figure=fig2
                    ),


                ])
            )
        ]
    )
])


@app.callback(
    Output('left-graph1', 'figure'),
    [Input('profiles', 'value')])

def update_figure(selected_profile):
    dff = df.groupby(selected_profile).id.count().reset_index()
    dff.rename(columns={'id': 'Number_of_Users'}, inplace=True)
    suma2 = dff.Number_of_Users.sum()
    dff['UsersPercentage'] = ((dff.Number_of_Users / suma2) * 100).round(1)
    dff.sort_values(by='Number_of_Users', ascending=False, inplace=True)

    fig = px.pie(dff , values= 'Number_of_Users',names = selected_profile,title='Datasource users Profile')
    fig.update_layout(margin=dict(t=30, b=45, l=0, r=0))
    fig.update_layout(showlegend=False)

    return fig

@app.callback(
    [Output('right-top-graph', 'figure'),
     Output('myusers','value')],
    [Input('month-slider', 'value')])

def update_user_graphs(selected_months):

    dff2 = df.groupby(['country_name','created_at','Day','Week','Month','Year']).id.count().reset_index()
    dff2.rename(columns={'id': 'Number_of_Users'}, inplace=True)
    suma = dff2.Number_of_Users.sum()
    dff2['UsersPercentage'] = ((dff2.Number_of_Users / suma) * 100).round(1)
    dff2.sort_values(by='Number_of_Users', ascending=False, inplace=True)

    dff2= dff2[(dff2['Month'] <=  selected_months)  & (dff2['Year'] == 2020)]


    #figure = px.bar(dff2, x='country_name',y = 'Number_of_Users')
    figure = go.Figure(data=[go.Bar(x=dff2.country_name, y=dff2.Number_of_Users)])
    figure.update_layout(title_text='Users per Country', title_font_size=18, title_x=0.5)
    figure.update_layout(xaxis_title='Country', yaxis_title='Number of Users')


    value = dff2['Number_of_Users'].sum()

    return figure, value


if __name__  == '__main__':
    app.run_server(debug=True)
