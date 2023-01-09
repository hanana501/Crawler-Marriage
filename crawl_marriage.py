# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 14:01:52 2022

@author: user
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import jieba
from jieba.analyse import extract_tags
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# headers
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
# 容器(裝取標題、網址)
d =[]
# 網址(ptt婚姻版)
url = "https://www.ptt.cc/bbs/marriage/index2839.html"
# 發送請求
web = requests.get(url,headers=headers)
# 解析
soup = BeautifulSoup(web.text,"lxml")
# 找出欲搜尋的區塊
block = soup.find_all("div",class_="r-ent")
# 利用迴圈在區塊中找出標題、網址
for row in block:
    d.append({"title":row.find("div",class_="title").text,
              "url":"https://www.ptt.cc/"+row.find("a")["href"]})

# 利用迴圈再剛爬出的網址裡爬取留言內容
for c in d:
    # 發送請求
    w = requests.get(c["url"],headers=headers)
    # 跳過掛掉的網頁
    if w.status_code == 404:
        d.remove(c)
    else:
        # 解析
        s = BeautifulSoup(w.text,"lxml")
        # 新增容器放留言內容
        content=[]
        # 利用迴圈搜尋每則留言區塊並找出內容
        for i in s.find_all('div', class_='push'):
            # 沒有留言就跳過
            if not i.find("span",class_="f1 hl push-tag"):
                continue
            # 存入留言內容並去除標點符號
            content.append(i.find("span",class_="f3 push-content").text.replace(": ",""))
        # 將content加入最初的容器裡
        c["content"] = content
        
# 轉dataframe
df = pd.DataFrame(d)
# 另存csv檔
df.to_csv("crawl_mg.csv",encoding="utf-8",index=False)

# 製作文字雲
# 設定分析所需的斷字字典
jieba.set_dictionary('dict.txt.big.txt')

for i in d[1:6:2]:
    # 找出留言內容，並添加空格(jieba才可以進行分析)    
    content_list = " ".join(i['content'])
    # 提取關鍵字(設定100個關鍵字)
    kw = extract_tags(content_list, topK=100, withWeight=True, allowPOS=(),withFlag=True)
    # 新增容器裝取分析完的詞
    kw_d={}
    # 利用迴圈把分析完的詞裝進容器
    for j in range(len(kw)):
        kw_d[kw[j][0]]=kw[j][1]
  
    # 做成文字雲
    wd = WordCloud(width=1280, # 圖的寬度
                height=720, # 圖的長度
                background_color="#5E4B3E",  # 背景顏色
                colormap="Dark2",
                font_path=r'C:\Users\user\AppData\Local\Microsoft\Windows\Fonts\NotoSansTC-Regular.otf' # 字型
                 ).fit_words(kw_d)
    # 用plt顯示
    plt.rcParams["font.family"] = "Microsoft JhengHei"
    plt.figure(figsize=(8, 6),dpi = 100)
    plt.imshow(wd, interpolation="bilinear")
    plt.title(i["title"]+i["url"])
    plt.axis("off")
    plt.show()