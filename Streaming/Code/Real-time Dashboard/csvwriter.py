import pandas as pd
from datetime import datetime
import re


def stream_to_csv(file):
    # now = datetime.now().isoformat()
    now = datetime.now()
    dt_string = str(now.strftime("%Y-%m-%d %H:%M:%S"))

    title = []
    NumberOfRate = [] 
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
        fiveStar.append(ele['histogram'][0])
        fourStar.append(ele['histogram'][1])
        threeStar.append(ele['histogram'][2])
        twoStar.append(ele['histogram'][3])
        oneStar.append(ele['histogram'][4])

    df = pd.DataFrame({
        'title': title,
        'NumberOfRate' : NumberOfRate,
        'Rate' : Rate,
        'oneStar': oneStar,
        'twoStar': twoStar,
        'threeStar': threeStar,
        'fourStar': fourStar,
        'fiveStar': fiveStar,
        'last_update': dt_string
        })
    
    df.to_csv('Rating_Info - 1.csv', index = False)
    
    return df


