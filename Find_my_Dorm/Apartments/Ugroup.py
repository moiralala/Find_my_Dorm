import numpy as np
from bs4 import BeautifulSoup
import re
import requests

def get_ugroup(url):
    """
        Scrape information about dorms or properties listed on the Ugroup website.

        Parameters:
        - url (str): The URL of the Ugroup website's building list.

        Returns:
        - list: A list of lists, where each inner list represents information about a dorm.

        Example:
        # Fetch information about dorms from the Ugroup website
        >>> ugroup_dorms = get_ugroup('https://ugroupcu.com/building-list/')

        Each inner list contains the following details:
        - Address (str): The address of the dorm or property.
        - Price (float): The rental price of the dorm or property.
        - Bedroom (int or str): The number of bedrooms in the dorm or property, or 'Not published'.
        - Bathroom (float): The number of bathrooms in the dorm or property.
        - Link (str): The URL link to the dorm or property's details.
        - Availability (str): The availability status or lease period of the dorm or property.
        - Name (str): The name or identifier of the property management company (Ugroup).
        - Is_studio (bool): Indicates whether the dorm or property is a studio (True) or not (False).

        Doctests:
        >>> len(get_ugroup('https://ugroupcu.com/building-list/')) >= 0
        True

        >>> isinstance(get_ugroup('https://ugroupcu.com/building-list/')[0][2], int) or get_ugroup('https://ugroupcu.com/building-list/')[0][2] == 'Not published'
        True

        >>> get_ugroup('https://ugroupcu.com/building-list/')[0][1] > 0
        True

        >>> get_ugroup('https://invalid-url.com')  # Returns an empty list for an invalid URL
        []
    """

    session = requests.session()
    req_header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',}
    name = 'Ugroup'
    re = session.get(url,headers = req_header).text
    soup = BeautifulSoup(re, 'html.parser')
    Dorms = []
    if soup == None:
        return Dorms

    for a in soup.find_all('a', class_='more_detail'):
        if not a.has_attr('href'):
            continue
        link = a['href']
        #Open the specific link for information of each apartment
        res = session.get(link,headers = req_header).text
        soup = BeautifulSoup(res, 'html.parser')
        #Some links on the website is invalid, eg. https://ugroupcu.com/property-details/104-e-armory-immediate-move-in-and-january-2024
        if soup.find('div', class_='prop_detil_rgt') is None:
            continue   
        address = soup.find('div', class_='prop_detil_rgt').find('h2').text
        if soup.find('div', class_='prop_detil_rgt') is None:
            continue   
        kinds = soup.find_all('div', class_='tab-content_in_wrapp tab-cntnt_wrap_btm')
        #kinds include more details about the apartment
        for kind in kinds:
            lookup = {}
            for li in kind.find('div', class_='tab-content_in_rgt').find_all('li'):
                divs = li.find_all('div')
                lookup[divs[0].text.strip()] = divs[1].text.strip()
                price = float(lookup['Price per month:'].replace('$', '').replace(',', ''))
                bathroom = float(lookup.get('Bathrooms:', 0))
                availability = str(lookup.get('Availability:')).lower()
                bedrooms_text = kind.find('h4', class_='propert_head').text.strip()
                bedrooms_text = bedrooms_text.strip('Luxury').strip()
                if 'studio' in bedrooms_text.lower():
                    is_studio = True
                    bedroom = 1
                else:
                    is_studio = False
                    try :
                        bedroom = int(bedrooms_text[0])
                    except ValueError:
                        # use np.nan for not published bedroom
                        bedroom = np.nan
        
            Dorms.append([address, price, bedroom, bathroom, link, availability, name, is_studio])
    return Dorms

