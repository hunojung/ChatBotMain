# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 16:49:28 2021

@author: Playdata


pip install plotly
pip install cython

# anaconta prompt 에서 실행
conda install Cython pystan pymc3 arviz
"""

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

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
warnings.filterwarnings(action='ignore')

# matplotlib inline
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.grid'] = False

pd.set_option('display.max_columns', 250)
pd.set_option('display.max_rows', 250)
pd.set_option('display.width', 100)

pd.options.display.float_format = '{:.2f}'.format



class NaverDataLabOpenAPI():
    """
    네이버 데이터랩 오픈 API 컨트롤러 클래스
    """

    """
    인증키 설정 및 검색어 그룹 초기화
    """
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.keywordGroups = []
        self.url = "https://openapi.naver.com/v1/datalab/search"
        
        
    """
    검색어 그룹 추가
    """
    def add_keyword_groups(self, group_dict):

        keyword_gorup = {
            'groupName': group_dict['groupName'],
            'keywords': group_dict['keywords']
        }
        
        self.keywordGroups.append(keyword_gorup)
        print(f">>> Num of keywordGroups: {len(self.keywordGroups)}")


    """
    요청 결과 반환
    """
    def get_data(self, startDate, endDate, timeUnit, device, ages, gender):
    
            # Request body
            body = json.dumps({
                "startDate": startDate,
                "endDate": endDate,
                "timeUnit": timeUnit,
                "keywordGroups": self.keywordGroups,
                "device": device,
                "ages": ages,
                "gender": gender
            }, ensure_ascii=False)
            
            # Results
            request = urllib.request.Request(self.url)
            request.add_header("X-Naver-Client-Id",self.client_id)
            request.add_header("X-Naver-Client-Secret",self.client_secret)
            request.add_header("Content-Type","application/json")
            response = urllib.request.urlopen(request, data=body.encode("utf-8"))
            rescode = response.getcode()
            if(rescode==200):
                # Json Result
                result = json.loads(response.read())
                
                df = pd.DataFrame(result['results'][0]['data'])[['period']]
                for i in range(len(self.keywordGroups)):
                    tmp = pd.DataFrame(result['results'][i]['data'])
                    tmp = tmp.rename(columns={'ratio': result['results'][i]['title']})
                    df = pd.merge(df, tmp, how='left', on=['period'])
                self.df = df.rename(columns={'period': '날짜'})
                self.df['날짜'] = pd.to_datetime(self.df['날짜'])
                
            else:
                print("Error Code:" + rescode)
                
            return self.df
        
    """
    일 별 검색어 트렌드 그래프 출력
    """
    def plot_daily_trend(self):
            colList = self.df.columns[1:]
            n_col = len(colList)
    
            fig = plt.figure(figsize=(6,3), facecolor='#FA7268')
            plt.title('일 별 검색어 트렌드', size=20, weight='bold')
            for i in range(n_col):
                sns.lineplot(x=self.df['날짜'], y=self.df[colList[i]], label=colList[i])
            plt.legend(loc='upper right')
            
            return fig
            

def search_test(keyword) :

    try:
        keywordSplit=keyword.split()
        if keywordSplit[2] != '분석해줘':
            return "분석 요청을 다시 해주세요"

        # 검색어 그룹 세트 정의
        keyword_group_set = {
            'keyword_group_1': {'groupName': keywordSplit[0], 'keywords': [keywordSplit[0]]},
            'keyword_group_2': {'groupName': keywordSplit[1], 'keywords': [keywordSplit[1]]}
            }
        #    'keyword_group_4': {'groupName': "테슬라", 'keywords': ["테슬라","Tesla","TSLA"]},
        #    'keyword_group_5': {'groupName': "페이스북", 'keywords': ["페이스북","Facebook","FB"]}
        # }

        # API 인증 정보 설정
        client_id = "bK6SRZLZNMahPGDdtfC0"
        client_secret = "dfR3AdiO5w"

        # 요청 파라미터 설정
        startDate = "2020-01-01"
        endDate = "2020-12-31"
        timeUnit = 'date'
        device = ''
        ages = []
        gender = ''

        # 데이터 프레임 정의
        naver = NaverDataLabOpenAPI(client_id=client_id, client_secret=client_secret)

        naver.add_keyword_groups(keyword_group_set['keyword_group_1'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_2'])
        # naver.add_keyword_groups(keyword_group_set['keyword_group_3'])
        # naver.add_keyword_groups(keyword_group_set['keyword_group_4'])
        # naver.add_keyword_groups(keyword_group_set['keyword_group_5'])

        df = naver.get_data(startDate, endDate, timeUnit, device, ages, gender)

        # 최대 값 5개 없애기
        for n in range(5):
            df[keywordSplit[0]][df[keywordSplit[0]].argmax()]=df[keywordSplit[0]][df[keywordSplit[0]].argmax()]/2

        max_value=df[keywordSplit[1]][df[keywordSplit[1]].argmax()]
        ## pairplot
        if '날씨' in keyword :
            weather_df = pd.read_excel("./data/weather_final_data.xlsx",usecols=[1,2,3,4])

            fig = plt.figure(figsize=(7,2.5), facecolor='#FA7268')
            plt.subplot(1,3,1)
            plt.title('기온과 '+keywordSplit[0], size=10, weight='bold')
            x = weather_df['기온']
            y = df[keywordSplit[0]]

            plt.scatter(x,y)
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x,p(x),"r--")
            plt.xlabel('기온')
            plt.ylabel(keywordSplit[0])


            plt.subplot(1,3,2)
            plt.title('강수량과 '+keywordSplit[0], size=10, weight='bold')
            x = weather_df['강수량']
            y = df[keywordSplit[0]]

            plt.scatter(x,y)
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x,p(x),"r--")
            plt.xlabel('강수량')

            plt.subplot(1,3,3)
            plt.title('미세먼지와 '+keywordSplit[0], size=10)
            x = weather_df['미세먼지']
            y = df[keywordSplit[0]]

            plt.scatter(x,y)
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x,p(x),"r--")
            plt.xlabel('미세먼지')
            plt.tight_layout()
            
            # 일 별 트렌드 시각화 하기
            #fig_1 = naver.plot_daily_trend()
            #print(mpld3.fig_to_html(fig_1)[15:100])
            
            return mpld3.fig_to_html(fig)
            # 월 별 트렌드 시각화 하기
            # fig_2 = naver.plot_monthly_trend()

            # 트렌드 예측하기
            # fig_3 = naver.plot_pred_trend(days = 90)
        else :
            # 데이터 프레임 정의
            naver = NaverDataLabOpenAPI(client_id=client_id, client_secret=client_secret)
            naver.add_keyword_groups(keyword_group_set['keyword_group_2'])
            df2 = naver.get_data(startDate, endDate, timeUnit, device, ages, gender)

            for n in range(5):
                df2[keywordSplit[1]][df[keywordSplit[1]].argmax()]=df[keywordSplit[1]][df[keywordSplit[1]].argmax()]/2
            max_value=df2[keywordSplit[1]][df[keywordSplit[1]].argmax()]
            fig = plt.figure(figsize=(5,4), facecolor='#FA7268')
            plt.title(keywordSplit[0]+"과(와) "+keywordSplit[1], size=20, weight='bold')
            x = df[keywordSplit[0]]
            y = df2[keywordSplit[1]]

            plt.scatter(x,y)
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x,p(x),"r--")
            plt.xlabel(keywordSplit[0])
            plt.ylabel(keywordSplit[1])

            return mpld3.fig_to_html(fig)
    except:
        return "분석 요청을 다시 해주세요"













