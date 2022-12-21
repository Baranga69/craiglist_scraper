# import to get a call request on the site
from requests import get

#get the first page of the page
response = get('https://sfbay.craigslist.org/search/eby/apa?hasPic=1&availabilityMode=0')
# filter applied to remove any listings posted without a picture

from bs4 import BeautifulSoup
html_soup = BeautifulSoup(response.text, 'html.parser')

# get the macro container for the housing posts
posts =  html_soup.find_all('li', class_='result-row')
print(type(posts)) #to double check we got a ResultSet
print(len(posts)) #to double check I got 120 (elements/page)


