#!/usr/bin/env python
# coding: utf-8
import requests
import csv
import os
import sys
from bs4 import BeautifulSoup
from datetime import time, datetime, date, timedelta
import urllib

# 讀取每頁日期符合昨日的文章
def all_page_articles(url, date):
    html_P = requests.get(url).text
    soup_P = BeautifulSoup(html_P, 'html.parser')
    all_inf = soup_P.select('div > .r-ent')
    # 每個文章區塊
    for inf in all_inf:
        a_date = inf.find('div', 'date')
        # 如果日期為昨日
        if a_date.string.lstrip(' ') == date :            
            # 取得文章標題與連結
            if inf.find('a'):
                title = inf.find('a').string
                pageLink = ptt + inf.find('a')['href']
                titleList.append(title)
                pageLinkList.append(pageLink)

#讀取文章內容       
def readArticle(url):
    html_R = requests.get(url).text
    soup_R = BeautifulSoup(html_R, 'html.parser')
    # 找出圖片網址
    # 找出所有連結
    image = soup_R.select('div#main-content > a')
    # 如果有連結
    if image :
        countImg = 0
        for img in image :
            imgUrl = img.string
            if countImg == 0 :
                # 如果連結開頭為圖片網站則存起來:兩種網站用or
                if(imgUrl.startswith('https://i.imgur.com/')|imgUrl.startswith('https://imgur.com/')):
                    if not imgUrl.endswith('.jpg') :
                        imgUrl += '.jpg'
                    imgList.append(imgUrl)
                    countImg += 1
        # 網址循環完都沒存到圖片的話
        if countImg == 0 :
            imgList.append('無圖片網址')
    else:
        imgList.append('無網址')

    # 找出文章資訊:作者時間IP跟推噓
    articleInf = soup_R.find_all('div', 'article-metaline')
    for a in articleInf :
        titleInf = a.find('span', 'article-meta-tag').string.strip(' ')
        inf = a.find('span', 'article-meta-value').string.strip(' ')
        if titleInf == '作者' :
            authorList.append(inf)
        if titleInf == '時間' :
            articleTimeList.append(inf)


    # IP
    articleIP = soup_R.find_all('span', 'f2')
    for ip in articleIP:
        if ip.string is not None:
            ipStr = ip.string
            if ipStr.startswith('※ 發信站:'):
                ipSplit = ipStr.split("來自:", 1)
                IPList.append(ipSplit[1].strip(' ').strip('\n'))
    
    # push&diss
    articleMes = soup_R.find_all('div', 'push')
    countPush = 0
    countDiss = 0
    for mes in articleMes:
        pushStr = mes.find('span', 'hl push-tag')
        dissStr = mes.find('span' , 'f1 hl push-tag')
        if pushStr :
            if pushStr.string.strip(' ') == '推':
                countPush += 1
            if pushStr.string.strip(' ') == '噓':
                countDiss += 1
        if dissStr :
            if dissStr.string.strip(' ') == '推':
                countPush += 1
            if dissStr.string.strip(' ') == '噓':
                countDiss += 1
    pushList.append(countPush)
    dissList.append(countDiss)


# 儲存圖片
def save_img (imgUrl, imgTitle) :
    if imgUrl :
        for img in range(len(imgUrl)) :
            # 如果內容是網址開頭
            if imgUrl[img].startswith('http') :
                filename = imgTitle[img].split(']')[-1] + '.jpg'
                imgInf = str(imgUrl[img])
                try:
                    if os.path.isdir('img') :
                        urllib.request.urlretrieve(imgInf, os.path.join('img', filename.strip(' ')))
                    else :
                        os.mkdir('img')
                        urllib.request.urlretrieve(imgInf, os.path.join('img', filename.strip(' ')))
                except PermissionError :
                    print("權限不足")
                except Exception as e :
                    print(e)
                    


if __name__ == '__main__':

    # 昨日日期字串
    yesterday = datetime.now() - timedelta(days=1)
    f_date = yesterday.strftime("%m/%d").lstrip('0')

    # 定義各值列表
    titleList=[]
    pageLinkList=[]
    authorList=[]
    articleTimeList=[]
    IPList=[]
    imgList=[]
    pushList=[]
    dissList=[]
    crawlerTimeList=[]

    Pageurl = 'https://www.ptt.cc/bbs/StupidClown/index.html'
    ptt = 'https://www.ptt.cc'

    # 取前五頁中昨日的文章總列表
    count = 0
    while count < 5 :
        html = requests.get(Pageurl).text
        soup = BeautifulSoup(html, 'html.parser')
        # 先找出上一頁的連結
        prePage = soup.find_all('a', class_='btn wide')[1].get('href')
        all_page_articles(Pageurl, f_date)
        # 替換新的讀取網址成上頁網址
        Pageurl = ptt + prePage
        count += 1

    # 取得昨日列表後來讀取文章內容
    for read in pageLinkList :
        if read :
            readArticle(read)
            crawlerTimeList.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # print(crawlerTimeList)
    # print(titleList)
    # print(pageLinkList)
    # print(imgList)
    # print(IPList)
    # print(authorList)
    # print(articleTimeList)
    # print('countPush: ' + str(pushList))
    # print('countDiss: '+ str(dissList))

    save_img(imgList, titleList)

    # 輸入至CSV檔案
    totalLength = len(imgList) #各列表長度
    with open('crawler_ptt.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['爬取時間', '作者', '標題', '文章時間','第一章圖片網址', 'Po文IP', '推文數', '噓文數', '文章網址'])
        for w in range(totalLength):
            csvwriter.writerow([crawlerTimeList[w], authorList[w], titleList[w], articleTimeList[w], imgList[w], IPList[w], pushList[w], dissList[w], pageLinkList[w]])




