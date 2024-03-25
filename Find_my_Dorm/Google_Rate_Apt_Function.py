import googlemaps
import matplotlib.pyplot as plt
import pandas as pd


def dataframe_to_list(df):
    """
    Transforms a dataframe of apartment listings into a list of unique listings by address.

    Cleans 'Address' column by removing extraneous information, groups by address, and
    aggregates to ensure unique entries. Outputs a list with the format "Address, Agency Name".

    Parameters:
    - df (pandas.DataFrame): Dataframe with 'Address' and 'Name' columns.

    Returns:
    - list: Unique listings as strings.
    """
    df['Address'] = df['Address'].str.replace(', Champaign', '').replace(', Urbana', '').replace(' - January 2024','').replace('. / Champaign,','').replace('. / Urbana,','').replace(' / Urbana,','')
    combined_apartments = df.groupby('Address').apply(lambda x: f"{x.name}, {x['Name'].iloc[0]}").tolist()
    return combined_apartments



# Initialize Google Maps client
gmaps = googlemaps.Client(key='')  # input your Google API



def get_place_rating(address):
    """
    Fetches the Google Maps place rating for a given address.

    Args: address (str): The address to search for.

    Returns: str: The rating as a string, or 'null' if not available.
    """
    try:
        place_details = gmaps.places(address)
        if 'results' in place_details and place_details['results']:
            return str(place_details['results'][0].get('rating', 'null'))
        else:
            return 'null'
    except Exception as e:
        print(f"Error fetching place details: {e}")
        return 'null'


def append_ratings_to_listings(combined_list):
    """
    Appends Google Maps ratings to each listing in combined listings.
    Excludes listings with a rating of '0' or 'null'.

    Args: combined_list (list of str): The list of apartment listings.

    Returns: list of str: The updated list with ratings appended, excluding '0' or 'null' ratings.
    """
    updated_list = []

    for listing in combined_list:
        address = listing.split()[0]  # Assuming the address is the first element in the listing
        rating = get_place_rating(address)

        # Skip adding the rating if it's '0' or 'null'
        if rating not in ('0', 'null'):
            updated_list.append(f"{listing}, {rating}")

    return updated_list



def create_apartment_ranking_table(updated_list):
    """
    Generates and displays a table ranking apartments.

    Parameters:
        df (pd.DataFrame): DataFrame containing apartment information.
    """
    # Adjusted columns to match the updated_list format
    columns = [
        'Apartment Name', 'Agency Name', 'Rating'
    ]
    # Split each item in the updated_list and check for the correct number of elements
    data_for_df = []

    for item in updated_list:
        split_item = item.split(', ')
        if len(split_item) == 3:  # If the split list has three elements, it matches the columns
            data_for_df.append(split_item)

    # Create DataFrame with the correct number of columns
    df = pd.DataFrame(data_for_df, columns=columns)

    # Convert 'Rating' to numeric and sort by it
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df.dropna(subset=['Rating'], inplace=True)
    df.sort_values('Rating', ascending=False, inplace=True)

    # Add 'Ranking' column based on the sorted 'Rating'
    df['Ranking'] = range(1, len(df) + 1)

    # Reorder the columns to include 'Ranking'
    df = df[['Ranking', 'Apartment Name', 'Agency Name', 'Rating']]

    # Calculate the figure height dynamically
    figsize_height = max(4, 0.4 * len(df))
    fig, ax = plt.subplots(figsize=(10, figsize_height))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1.2, 2)
    
    # Increase the 'pad' parameter to provide more space for the title
    fig.tight_layout(pad=6.0)

    # Adjust the 'y' parameter to provide more space between the title and the table
    plt.suptitle('The Ranking of Apartments in Champaign', fontsize=16, weight='bold', y=1.00000001, va='bottom')
    plt.show()





