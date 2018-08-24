# coding: utf-8

# # 居委会信息获取爬虫测试
# 由于居委会的数据量过大，我这里用很小的数据测试其代码是否正确。

import requests
from lxml import etree
import csv
import time
import pandas as pd
from queue import Queue
from threading import Thread
from fake_useragent import UserAgent

# 下面加入了num_retries这个参数，经过测试网络正常一般最多retry一次就能获得结果
def getUrl(url,num_retries = 5):
    ua = UserAgent()
    headers = {'User-Agent':ua.random}
    try:
        response = requests.get(url,headers = headers)
        response.encoding = response.apparent_encoding
        data = response.text
        return data
    except Exception as e:
        if num_retries > 0:
            time.sleep(10)
            print(url)
            print("requests fail, retry!")
            return getUrl(url,num_retries-1) #递归调用
        else:
            print("retry fail!")
            print("error: %s" % e + " " + url)
            return #返回空值，程序运行报错

def getVillage(url_list):
    queue_village = Queue() #队列
    thread_num = 20 #进程数
    village = [] #记录街道信息的字典（全局）
    
    def produce_url(url_list):
        for url in url_list:
            queue_village.put(url) # 生成URL存入队列，等待其他线程提取
    
    def getData():
        while not queue_village.empty(): # 保证url遍历结束后能退出线程
            url = queue_village.get() # 从队列中获取URL
            data = getUrl(url)
            selector = etree.HTML(data)
            villageList = selector.xpath('//tr[@class="villagetr"]')
            #下面是爬取每个区的代码、URL
            for i in villageList:
                villageCode = i.xpath('td[1]/text()')
                UrbanRuralCode = i.xpath('td[2]/text()')
                villageName = i.xpath('td[3]/text()')
                #上面得到的是列表形式的，下面将其每一个用字典存储
                for j in range(len(villageCode)):
                    village.append({'code':villageCode[j],'UrbanRuralCode':UrbanRuralCode[j],'name':villageName[j]})
                
    def run(url_list):
        produce_url(url_list)
    
        ths = []
        for _ in range(thread_num):
            th = Thread(target = getData)
            th.start()
            ths.append(th)
        for th in ths:
            th.join()
            
    run(url_list)
    return village


df_town = pd.read_csv("town.csv",encoding = 'utf-8')
village = getVillage(df_town['link'][0:10000])

df_village = pd.DataFrame(village)
# 信息写入csv文件
df_village.to_csv('village-0.csv', sep=',', header=True, index=False)

