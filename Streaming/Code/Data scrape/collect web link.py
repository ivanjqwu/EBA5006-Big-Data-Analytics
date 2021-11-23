import requests
from bs4 import BeautifulSoup
from Scrape_function import google_web_scrape
from scrape_function_sep import file_to_csv
import re
import pandas as pd

 
result = requests.get('https://play.google.com/store/apps/category/GAME')

# check validation
# print(result.status_code)
# print(result.headers)

cate_paths = []
game_paths = []
AppInfo = []

# web source of the page
src = result.content
soup = BeautifulSoup(src, 'lxml', from_encoding='utf-8')

catelink = soup.find_all('li', {'class': 'KZnDLd'})
for cate in catelink:
    link = cate.find('a')
    path = link.attrs['href']
    cate_paths.append(path)

cate_paths = cate_paths[36:]


# collect the links of all games, based on different links of each category
for category in cate_paths:
    url = 'https://play.google.com' + category
    web = requests.get(url)
    
    src = web.content
    soup = BeautifulSoup(src, 'lxml', from_encoding='utf-8')
    
    gamelinks = soup.find_all('div', {'class': 'b8cIId ReQCgd Q9MA7b'})
    for gamelink in gamelinks:
        link = gamelink.find('a')
        path = link.attrs['href']
        game_paths.append(path)
        

game_paths = list(set(game_paths))

# Extract information based on the links 
for path in game_paths:
    url = 'https://play.google.com' + path
    appInfo = google_web_scrape(url)
    
    
    AppInfo.append(appInfo)
    
    
# import json
# with open('AppInfo.txt', 'w') as json_file:
#  json.dump(AppInfo, json_file)


# write into csv file

title = []
NumberOfRate = [] 
grene = []
Rate = []
AgeRating = []
price = []
free = []
OfferedBy = []

i = 0
for ele in AppInfo:

    if len(ele) == 21:
        ele['title'] = re.sub(',', ' ', ele['title'])
        title.append(ele['title'])

    
        NumberOfRate.append(ele['NumberOfRate'])
        Rate.append(ele['Rate'])
        grene.append(ele['grene'])
        AgeRating.append(ele['AgeRating'])
        price.append(ele['price'])
        free.append(ele['free'])
        OfferedBy.append(ele['Offered By'])
        
    i = i + 1

df = pd.DataFrame({
    'title': title,
    'NumberOfRate' : NumberOfRate,
    'Rate' : Rate,
    'grene': grene,
    'Rate': Rate,
    'AgeRating': AgeRating,
    'price': price,
    'free': free,
    'OfferedBy': OfferedBy
    })
    
df.to_csv('GameInfo_descriptive', index = False)
    

