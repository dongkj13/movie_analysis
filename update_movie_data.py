import urllib.request
import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
import re
from movie import movie
from conf import country_list

def getHTMLText(url,k = 0):
    try:
        if (k == 0):
            kw={}
        else: 
            kw={'start':k,'filter':''}
        r = requests.get(url, params=kw, headers={'User-Agent': 'Mozilla/4.0'})
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print("Failed!")

def getNumOfMoviesByHtml(html):
    soup = BeautifulSoup(html, "html.parser")
    num = soup.find('title').getText() # 我看过的电影(***)
    num = int(re.search('\d+',num).group())
    return num

def getNumOfMoviesByCSV(file_name):
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        return len(df)
    else:
        return 0

def splitTag(tag_str):
    try:
        release_year = re.search('\d+', tag_str).group()
        tag_list = tag_str.strip().split(' ')
        tag_list.remove(release_year)
        country = [c for c in country_list if c in tag_list][0]
        tag_list.remove(country)
        type = '电影'
        if '电视剧' in tag_list:
            type = '电视剧'
            tag_list.remove('电视剧')
    except:
        return 0, '', '', []
    
    return int(release_year), country, type, tag_list
    

def updateData(html, n):
    global df
    soup = BeautifulSoup(html, "html.parser")
    movieList = soup.find('div',attrs={'class':'grid-view'}).find_all('div',attrs={'class':'item'})
    for i in range(n):
        movie = {}
        movieLi = movieList[i]

        movieInfo = movieLi.find('div',attrs={'class':'info'}).find('ul')
        movie['href'] = movieInfo.find('a')['href'].strip()
        movie['mid'] = int(re.search('\d+', movie['href']).group())
        movieName = movieInfo.find('a').getText()
        if movieName.find('/') != -1:
            movieName = movieName[0:movieName.find('/')]
        movie['name'] = movieName.strip()


        movie['myRate'] = movieInfo.find_all('li')[2].find_all('span')[0]['class'][0][6]
        movie['release_year'], movie['country'], movie['type'], movie['myTag'] = splitTag(movieInfo.find_all('li')[2].find_all('span')[2].getText()[3:])

        movie = {k: [v] for k, v in movie.items()}

        df = df.append(pd.DataFrame(movie),ignore_index=True)




if __name__ == '__main__':
    userId = 155499404  # dkj
    url = 'https://movie.douban.com/people/%d/collect' % userId
    html = getHTMLText(url)
    num_of_movies = getNumOfMoviesByHtml(html)

    data_name = './data/%d.xls' % userId
    if os.path.exists(data_name):
        df = pd.read_excel(data_name)
    else:
        df = pd.DataFrame()

    for k in range(0, num_of_movies - len(df), 15):
    #for k in range(0, 15, 15):
        html = getHTMLText(url, k)
        if num_of_movies - len(df) > 15:
            n = 15
        else:
            n = num_of_movies - len(df)
        updateData(html, n)
        print(k)

    col_list = ['mid', 'name', 'release_year', 'country', 'type', 'myRate', 'myTag', 'href']
    df = df.loc[:, col_list]
    #print(df)

    df.to_excel(data_name, index=False)
