import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the CSV data
df = pd.read_csv('all_df.csv')
df.n_person = df.n_person.astype('str')
r = pd.DataFrame(df.groupby(['hotel_name'])['review'].last().sort_values(ascending=True))
r = r.reset_index()

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the app layout
app.layout = html.Div([

    html.H1("Market Summary"),

     dcc.Graph(
        id='hotel-review-counts',
        figure=px.bar(r, x='review', y='hotel_name', orientation='h',
                      labels={'hotel_name': 'Hotel Name', 'review': 'Review Count'},
                      title='Hotel Review Counts',
                      ).update_layout(yaxis = dict(tickfont = dict(size=6)))
        
    ),
    

    # # Bar plot for hotel count by score
    # dcc.Graph(id='hotel-by-score'),
    # # Histogram plot for hotel count by review
    # dcc.Graph(id='hotel-by-review'),
    # # Histogram plot for stock count by hotel
    # dcc.Graph(id='stock-by-hotel'),

    html.H1("Hotel Summary"),
    
    # Dropdown to select unique hotel names
    dcc.Dropdown(
        id='hotel-dropdown',
        options=[{'label': hotel, 'value': hotel} for hotel in df['hotel_name'].unique()],
        value=df['hotel_name'].iloc[0]
    ),

    # Dropdown to select unique hotel names
    dcc.Dropdown(
        id='person-dropdown',
        options=[{'label': n_person, 'value': n_person} for n_person in df['n_person'].unique()],
        value='2'
    ),
    
    # Scatter plot for check_in vs price
    dcc.Graph(id='min-price-scatter-plot'),

    # Bar plot for check_in vs all stock
    dcc.Graph(id='all-stock-bar-plot'),

    # Bar plot for check_in vs stock to beat
    dcc.Graph(id='stock-to-beat-bar-plot'),
    
    # # Scatter plot for check_in vs price
    # dcc.Graph(id='stock-scatter-plot'),

    # Scatter plot for check_in vs price, colored by room_type
    dcc.Graph(id='room-type-scatter-plot'),

    # Scatter plot for check_in vs price, colored by room_type
    dcc.Graph(id='cancellation-scatter-plot'),
])

# Callback to update the scatter plots based on the selected hotel_name
@app.callback(
    [Output('min-price-scatter-plot', 'figure'),
    Output('all-stock-bar-plot', 'figure'),
    Output('stock-to-beat-bar-plot', 'figure'),
    Output('room-type-scatter-plot', 'figure'),
    Output('cancellation-scatter-plot', 'figure')],
    [Input('hotel-dropdown', 'value')],
    [Input('person-dropdown', 'value')]
)
def update_scatter_plots(selected_hotel, selected_person):
    n_person_filter = df[df['n_person'] == selected_person]
    filtered_df = df[(df['hotel_name'] == selected_hotel) & (df['n_person'] == selected_person)]
    stock_df = pd.DataFrame(n_person_filter.groupby(['hotel_name','room_id','check_in'])['stock'].last()).sort_values(['check_in']).groupby(['hotel_name', 'check_in'])['stock'].sum().reset_index()
    all_min_prices = pd.DataFrame(n_person_filter.groupby(['hotel_name','check_in'])['price'].min()).reset_index().sort_values(['check_in'])
    all_min_prices.hotel_name[all_min_prices[all_min_prices.hotel_name != selected_hotel].index] = 'Other Hotels'
    stock_df.hotel_name[stock_df[stock_df.hotel_name != selected_hotel].index] = 'Other Hotels'


    #get hotel data
    #hotel_detail = df[df.hotel_name == selected_hotel]
    hotel_score = filtered_df.score.iloc[-1]
    #find the cheapest offers by check in date
    cheapest = filtered_df.groupby(['check_in'])['price'].min()
    
    stock_to_beat = []
    for a in range(len(cheapest)):
        filtered = n_person_filter[(n_person_filter.check_in == cheapest.index[a]) & \
                            (n_person_filter.price <= cheapest[a]) & \
                            (n_person_filter.score >= hotel_score) & \
                            (n_person_filter.hotel_name != selected_hotel)]
        stock_to_beat.append(pd.DataFrame(filtered.groupby(['hotel_name','room_id','check_in'])['stock'].last()).sort_values(['check_in']).groupby(['hotel_name', 'check_in'])['stock'].sum().reset_index())

    stock_to_beat_df = pd.concat(stock_to_beat).reset_index()
    #stock_to_beat_df.hotel_name[stock_to_beat_df[stock_to_beat_df.hotel_name != selected_hotel].index] = 'Other Hotels'
    # # Scatter plot for check_in vs price, colored by room_type
    # price_scatter_fig = px.scatter(
    #     filtered_df,
    #     x='check_in',
    #     y='price',
    #     color='n_person',
    #     title=f'Prices for {selected_hotel} (Colored by Number of People)',
    # )

    # Scatter plot for check_in vs min price, selected hotel highlighted
    min_price_scatter_fig = px.scatter(
        all_min_prices,
        x='check_in',
        y='price',
        color = 'hotel_name',
        title=f'Prices for all hotels vs selected hotel',
    )

    #Bar plot for check_in vs all stock, colored by room_type
    stock_bar_fig = px.bar(
        stock_df,
        x='check_in',
        y='stock',
        color='hotel_name',
        title=f'Stock for all hotels vs selected hotel',
    )

    # Bar plot for check_in vs stock to beat, colored by room_type
    stock_to_beat_bar_fig = px.bar(
        stock_to_beat_df,
        x='check_in',
        y='stock',
        color='hotel_name',
        title=f'Stock to beat for all hotels vs selected hotel',
    )

    # Scatter plot for check_in vs price, colored by room_type
    room_type_scatter_fig = px.scatter(
        filtered_df,
        x='check_in',
        y='price',
        color='room_type',
        title=f'Prices for {selected_hotel} (Colored by Room Type)',
    )

    # # Scatter plot for check_in vs price, colored by room_type
    # stock_scatter_fig = px.bar(
    #     stock_df,
    #     x='check_in',
    #     y='stock',
    #     color='hotel_name',
    #     title=f'Stock for {selected_hotel} (Colored by Hotel name)',
    # )
    

    # Scatter plot for check_in vs price, colored by room_type
    cancellation_scatter_fig = px.scatter(
        filtered_df,
        x='check_in',
        y='price',
        color='cancellation',
        title=f'Prices for {selected_hotel} (Colored by Cancellation type)',
    )
    
    return min_price_scatter_fig, stock_bar_fig, stock_to_beat_bar_fig, room_type_scatter_fig, cancellation_scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
