# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                            [{'label': s, 'value': s} for s in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ), 
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                
                                
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[min_payload, max_payload]
                                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# TASK 2: pie chart callback
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Sum of successes (class=1) per site
        df_all = (
            spacex_df.groupby('Launch Site', as_index=False)['class']
                     .sum()
        )
        fig = px.pie(
            df_all,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Filter to site and show Success vs Failure counts
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = (
            df_site['class'].value_counts()
                  .rename_axis('Outcome')
                  .reset_index(name='count')
        )
        counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            counts,
            values='count',
            names='Outcome',
            title=f'Success vs Failure for {selected_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

# TASK 4: scatter chart callback
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range

    # Filter by payload range first
    df = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]

    # Then filter by site (if not ALL)
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
        title = f'Payload vs. Outcome for {selected_site} ({low}–{high} kg)'
    else:
        title = f'Payload vs. Outcome for All Sites ({low}–{high} kg)'

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=title
    )
    fig.update_layout(yaxis_title='Launch Outcome (class)')
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
