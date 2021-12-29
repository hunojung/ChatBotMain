import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from bs4 import BeautifulSoup as bs
import requests

import urllib.request
import datetime
import json
import glob
import sys
import os
import mpld3
import matplotlib.ticker as ticker
# from fbprophet import Prophet

import warnings

def search_movie(keyword):
 
    html = requests.get('https://search.naver.com/search.naver?query=영화+순위').text
    soup=bs(html,'lxml')
    
    try :

        movie_all1=soup.find('ul',class_='_panel').findAll('span',class_='this_text')
        movie_all2=soup.find('ul',class_='_panel').findAll('strong',class_='name')
        movie_all3=soup.find('ul',class_='_panel').findAll('span',class_='sub_text')


        movie_rank=[title.get_text() for title in movie_all1]
        movie_name=[title.get_text() for title in movie_all2]
        movie_pop=[title.get_text() for title in movie_all3]

        movie_rank_df=pd.DataFrame(movie_rank)
        movie_name_df=pd.DataFrame(movie_name)
        movie_pop_df=pd.DataFrame(movie_pop)

        movie_data=pd.concat([movie_rank_df,movie_name_df,movie_pop_df],axis=1)


        movie_data.columns=['순위','이름','관객']
        movie_data.set_index('순위',inplace=True)
        res='영화 추천 목록 입니다~'
        j=0
        for i in movie_data.index:
            res= res+'<br>&nbsp'+i+'위'+'&nbsp'+movie_data['이름'][i]+'&nbsp'+'&nbsp'+'관객수 : '+movie_data['관객'][i]
            if j == 3:
                res=res+"|"
            j=j+3
        return res
    except :
        return '다시 입력 하세요' 
    

