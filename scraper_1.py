# import to get a call request on the site
import requests
#For working with data frames
import pandas as pd
import numpy as np
 #for storing data as a csv
import csv
# web scraping library 
from bs4 import BeautifulSoup
#time management
import time
from random import randint
# regular expression
import re

# list of city names we want to get data for
cities = ['dallas','chicago', 'newyork', 'sfbay', 'losangeles', \
        'houston', 'phoenix', 'philadelphia', 'sanantonio', 'washingtondc',\
       'boston', 'nashville', 'atlanta', 'miami', 'seattle']

# all pages in a city will be stored in this list
list_of_cities = []

for city in cities:
    #say each city has approximately 1800 pages for the "cars for sale by owner" category
    #we'll track these pages with page_number variable below
    page_number = 1

    #cycling through the 1800 pages
    while page_number <=1800:
        #city_link variable takes a different city name from cities everytime through the loop
        city_link = "https://" + str(city) + ".craigslist.org/d/cars-trucks-by-owner/search/cto?s=" + \
                                str(page_number) + "&hasPic=1"
        
        list_of_cities.append(city_link)
        page_number += 120

links = []
#URLs counter
car_urls = 1
for each_city_page in list_of_cities:
    links_in_each_city_page = requests.get(each_city_page)
    #parse the html object from the page to BS object
    soup = BeautifulSoup(links_in_each_city_page.content, 'html.parser')

    try:
        #get the macro-container for the car posts for that page
        posts = soup.find_all('a',class_='result-image gallery')

        #get all the html links in the page and append them to a list
        for link in posts:
            l = link.get('href')
            links.append(l)

    except:
        pass

    # this code just helps keep count of the looping process
    if car_urls % 5 == 0:
        city_link = l.strip()
        start = city_link.find("//") + len("//")
        end = city_link.find(".")
        city_string = city_link[start:end]
        print('Number of pages returned ->' + str(car_urls) + '---' + city_string)

# a sleep timer to manage our server requests
time.sleep(randint(0,1))
car_urls += 1

# save links to csv
df = pd.DataFrame(links)
df.to_csv("./links.csv", sep=',',index=False)

# read links from csv
links = pd.read_csv('./links.csv', names=['https'])
links = links['https'][1:]
print("links returned -->", len(links))
links

# just a counter
count = 0

# store vehicle details in this list
cars = []

# loop over all links in the list 
for link in links:
    # make HTTP requests
    each_page = requests.get(link)
    # The sleep function can help avoid server overload with too many requests in a short period of time
    time.sleep(randint(1,2))
    # store the BS object in a variable
    page_soup = BeautifulSoup(each_page.content, 'html.parser')

    # loop over each link and store address
    car_details = []
    try:
        # find price attribute and store in car details
        car_details.append(page_soup.find('span', class_="price").text)

        # find date and time and append to car details 
        for span in page_soup.find_all('span', recursive=True):
            if not span.attrs.values():
                car_details.append(span.text)
        car_details.append("date time: " + page_soup.find('time', class_="date timeago")\
                                         .text.strip().replace(':',';'))

        # find date and city name and append to car details
        city = link.strip()
        start = city.find("//") + len("//")
        end = city.find(".")
        substring = city[start:end]
        car_details.append('city:' + substring)

        # find geo coordinates and append
        geos = page_soup.findAll("div",{"class": "mapbox"})
        lat = geos[0].contents[1].get('data-latitude')
        car_details.append('lat:' + lat.strip())
        long = geos[0].content[1].get('data-longitude')
        car_details.append('long:' + long.strip())

        # find post body and append
        post_body = page_soup.find(attrs={'id' : 'postingbody'}).contents[2]
        # remove non ascii characters from post body
        car_details.append('post_body:' + re.sub("[^0-9a-zA-Z]+", " ", post_body))
        # find postID and append to car details / We'll use this to assign labels to images later 
        car_details.append('pID:' + link.strip().replace('html', '').replace('.', '').split('/')[-1])
    except:
        pass

    # perform some basic cleanup and store in clean
    clean = []
    for string in car_details:
        # this attribute came without a label. Assign one.
        if string == car_details[1]:
            clean.append('year make model: ' + string)
        # clean up price text from $9,999 --> 9999
        if string == car_details[0]:
            clean.append('price: ' + string.replace(',','').replace('$', ''))
        else :
            clean.append(string)

    # some attributes come without labels. Drop these
    car_final = []
    for s in clean:
        if ':' in s:
            car_final.append(s)

    # append clean attributes for each vehicle to car list
    cars.append(car_final)
    count += 1

    # just a counter to keep track of the loop 
    if count % 100 == 0:
        print('loop # -> ', count)

# method to strip() the keys and values after splitting in order to trim white-space
def list_to_dict(rlist):
    return dict(map(lambda s : map(str.strip, s.split(':')), rlist))

# create a dictionary for label:value for each car attribute
car_dicts = []
for car in cars:
    car_dict = list_to_dict(car)
    car_dicts.append(car_dict)

for i in car_dicts:
    print(i)

# create an Empty DataFrame object
dfs = pd.DataFrame()

for item in car_dicts:
    df = pd.DataFrame.from_dict(item, orient='index').transpose()
    # concatenante each new df from the loop into the parent df
    dfs = pd.concat([dfs,df], axis=0, ignore_index=True, sort=True)
    # clean duplicate year in 'year make model'
    dfs['year_c make model'] = dfs['year make model'].str.replace(r'\b(\w+)(\s+\1)+\b', r'\1', regex=True)

# save data frame to csv
dfs.to_csv('car_data.csv', sep='\t', encoding='utf-8')
dfs.to_csv('Users/keithbaranga/Documents/GitHub/car_data.csv', sep='\t', encoding='utf-8')
