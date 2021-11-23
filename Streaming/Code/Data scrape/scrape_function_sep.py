import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import json
import os 
from google.cloud import storage 


def google_web_scrape_basic(url, appInfo):
    '''
    This function is used to collection basic information of the game from the url given
    
   
    Parameters
    ----------
    url : string
        The full url of a website from Google Play Game. 
        For example: https://play.google.com/store/apps/details?id=jp.pokemon.pokemonunite
        
    appInfo : dictionary
        An empty dictionary that to put information in 

    Returns
    -------
    appInfo : dictionary
        A dictionary with information

    '''
    
    result = requests.get(url)

    # web source of the page
    src = result.content
    soup = BeautifulSoup(src, 'lxml', from_encoding='utf-8')

    # for header part

    title = soup.find_all('h1', {'class': 'AHFaub'}) 
    appInfo['title'] = title[0].text

    description = soup.find_all('div', {'jsname': 'sngebd' })
    appInfo['description'] = description[0].text

    grene = soup.find_all('span', {'T32cc UAO9ie'})
    appInfo['grene'] = grene[1].text

    AgeRating = soup.find_all('div', {'KmO8jd'})
    appInfo['AgeRating'] = AgeRating[0].text

    AdPurchase = soup.find_all('div', {'class': 'bSIuKf'})
    if AdPurchase == []:
        appInfo['ContainAds'] = 'False'
        appInfo['offerIAP'] = 'False'
    else: 
        if 'Contains Ads' in AdPurchase[0].text: 
            appInfo['ContainAds'] = 'True'
        else: appInfo['ContainAds'] = 'False'

        if 'Offers in-app purchases' in AdPurchase[0].text: 
            appInfo['offerIAP'] = 'True'
        else: appInfo['offerIAP'] = 'False'

    price= soup.find_all('span', {'class': 'oocvOe'})
    if price[0].text == 'Install':
        appInfo['price'] = float(0.00)
    else: appInfo['price'] = float(re.sub(r"[ ,+$a-zA-Z]", "", price[0].text))

    if appInfo['price'] > 0:
        appInfo['free'] = 'False'
    else: appInfo['free'] ='True'

    try:
        people_rate = soup.find_all('span', {'class': 'AYi5wd TBRnV'})
        appInfo['NumberOfRate'] = int(re.sub(r"[ ,.+]", "", people_rate[0].text))
    except: IndexError
    pass
    
    # Total rate (x out of 5)
    try:
        Rate = soup.find('div', {'class':'BHMmbe'})
        appInfo['Rate'] = Rate.text
    except: AttributeError
    pass
    
    # Calculate the rate distribution

    RateDistribute = soup.find_all('div', {'class': 'mMF0fd'})
    percent = []
    for rate in RateDistribute: # extract the percentage of the bar chart
        result = str(rate.find_all('span')[1])
        number = float(re.findall(r'width:(.*)%',result)[0])
        percent.append(number/100)

    stars = []
    for element in percent: # calculate based on the percentage
        result = (appInfo['NumberOfRate']/sum(percent)) * element
        stars.append(round(result))
   
    try: 
        appInfo['histogram'] = stars
        appInfo['fiveStar'] = stars[0]
        appInfo['fourStar'] = stars[1]
        appInfo['threeStar'] = stars[2]
        appInfo['twoStar'] = stars[3]
        appInfo['oneStar'] = stars[4]
        
    except: IndexError
    pass
    
    return appInfo



def google_web_scrape_additional(url, appInfo):
    '''
    This function is used to collection additional information of the game, 
    such as the producer, Update time...
    '''
    
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, 'lxml', from_encoding='utf-8')
    
    add_title = soup.find_all('div', {'class': 'hAyfc'})
    useless_key = ['Permissions', 'Report', 'Content Rating', 'In-app Products']

    for element in add_title:
        key = element.find('div', {'class': 'BgcNfc'})
        value = element.find('span', {'class': 'htlgb'})
        appInfo[key.text] = value.text


    for title in useless_key:
        try: del appInfo[title]
        except: KeyError
        pass

    try:
        appInfo['miniInstalls'] = int(re.sub(r"[a-zA-Z+,]", "", appInfo['Installs']))
        appInfo['Android'] = float(re.sub(r"[a-zA-Z+,]","", appInfo['Requires Android']))
    except: ValueError
    pass

    return(appInfo)  


def google_web_scrape(url, appInfo):
    '''
    A combination of scraping both basic and additional information of the game

    '''
    
    google_web_scrape_basic(url, appInfo)
    google_web_scrape_additional(url, appInfo)
    return appInfo


def file_to_csv(file, file_name):
    '''
    This function is used to convert the json files (with information require updates) that are the output of funciton google_web_scrape_basic
    and google_web_scrape_additional into csv files. 

    Parameters
    ----------
    file : dictionary (JSON)
        the specific json file gained from the web scrapper functions 

    Returns
    -------
    df : pandas DataFrame
        A pandas DataFrame with the information from the JOSN file, and will be writen into a csv. 

    '''
    
    now = datetime.now()
    dt_string = str(now.strftime("%Y-%m-%d %H:%M:%S"))

    title = []
    NumberOfRate = [] 
    histogram = []
    grene = []
    Rate = []
    oneStar = [] 
    twoStar = [] 
    threeStar = [] 
    fourStar = [] 
    fiveStar = []

    for ele in file:
        ele['title'] = re.sub(',', ' ', ele['title'])
        title.append(ele['title'])
        
        NumberOfRate.append(ele['NumberOfRate'])
        Rate.append(ele['Rate'])
        grene.append(ele['grene'])
        histogram.append(ele['histogram'])
        fiveStar.append(ele['histogram'][0])
        fourStar.append(ele['histogram'][1])
        threeStar.append(ele['histogram'][2])
        twoStar.append(ele['histogram'][3])
        oneStar.append(ele['histogram'][4])

    df = pd.DataFrame({
        'title': title,
        'NumberOfRate' : NumberOfRate,
        'Rate' : Rate,
        'grene': grene,
        'histogram': histogram,
        'oneStar': oneStar,
        'twoStar': twoStar,
        'threeStar': threeStar,
        'fourStar': fourStar,
        'fiveStar': fiveStar,
        'last_update': dt_string
        })
    
    df.to_csv(file_name, index = False)
    
    return df

# def batch_to_csv(file):
    

def get_data(LinksCollection):
    '''
    

    Parameters
    ----------
    LinksCollection : list
        A list with ALL website urls that you want to scrape data from

    Returns
    -------
    gameInfo_all : dictionary (JSON)
        A dictionary with all basic information of the games in LinksCollection
        
    streamInfo_all : dictionary (JSON)
        A dictionary with all stream information of the games in LinksCollection

    '''
    # data scrape from these web links
    stream = ['title', 'NumberOfRate', 'grene','histogram', 'Rate', 'histogram', 'oneStar', 'twoStar', 'threeStar', 'fourStar', 'fiveStar'] # These are the data that require real-time updartes
    gameInfo_all = [] # put the information that do not reuqire real-time updates
    streamInfo_all = [] # put the information that require real-time updates


    for path in LinksCollection:
        gameInfo = {}
        streamInfo = {}
        url = 'https://play.google.com' + path
        info = google_web_scrape_basic(url, gameInfo)
    
        for ele in stream:
            # seperate the data into two parts, non-real time and real-time data
            try:
                streamInfo[ele] = info[ele]
            except: KeyError
            pass
        streamInfo_all.append(streamInfo)
            
        gameInfo_all.append(info)
    
    return gameInfo_all, streamInfo_all
    
    
def upload_to_bucket(blob_name, file_path, bucket_name):

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceKey.json'

    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket('data5006')
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return True

    except Exception as e:
        print(e)
        return False

def write_upload_file(gameInfo_all, streamInfo_all):
    '''
    Ths function is used to connect and upload our JSON file to GCP cloud storage,
    and name the files based on the updating time

    Parameters
    ----------
    gameInfo_all : dictionary (JSON)
    streamInfo_all : dictionary (JSON)
    file_path: the location you want to store the files
    '''
    
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    file_name_rate = 'streamInfo ' + dt_string +'.txt'
    file_name_game = 'GameInfo.txt' + dt_string +'.txt'


    # wirte the JSON files
    with open(file_name_rate, 'w') as json_file:
        json.dump(streamInfo_all, json_file)

    with open(file_name_game, 'w') as json_file:
        json.dump(gameInfo_all, json_file)
    
    # write the csv file
    file_to_csv(streamInfo_all, 'Rating_Info - 1.csv')
    
    
    # Upload to CGP
    upload_to_bucket(file_name_rate, os.path.join(os.getcwd(), file_name_rate), 'data5006')
    upload_to_bucket(file_name_game, os.path.join(os.getcwd(), file_name_game), 'data5006')
    upload_to_bucket('Rating_Info - 1.csv', os.path.join(os.getcwd(), 'Rating_Info - 1.csv'), 'data5006')

    
    




# https://www.youtube.com/watch?v=Gs5jGDROx1M

