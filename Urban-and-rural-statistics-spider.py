# 库函数导入
import requests
from lxml import etree
import csv
import time
import pandas as pd
from queue import Queue
from threading import Thread


# 网页爬取函数
# 下面加入了num_retries这个参数，经过测试网络正常一般最多retry一次就能获得结果
def getUrl(url,num_retries = 5):
    headers = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
    try:
        response = requests.get(url,headers = headers)
        response.encoding = 'GBK'
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

# 获取省级代码函数
def getProvince(url):
    province = []
    data = getUrl(url)
    selector = etree.HTML(data)
    provinceList = selector.xpath('//tr[@class="provincetr"]')
    for i in provinceList:
        provinceName = i.xpath('td/a/text()') #这里如果采用//a/text()路径会出现问题！！
        provinceLink = i.xpath('td/a/@href')
        for j in range(len(provinceLink)):
            provinceURL = url[:-10] + provinceLink[j] #根据获取到的每个省的链接进行补全，得到真实的URL。
            province.append({'name':provinceName[j],'link':provinceURL})
    return province

# 获取市级代码函数
def getCity(url_list):
    city_all = []
    for url in url_list:
        data = getUrl(url)
        selector = etree.HTML(data)
        cityList = selector.xpath('//tr[@class="citytr"]')
        #下面是抓取每一个城市的代码、URL
        city = []
        for i in cityList:
            cityCode = i.xpath('td[1]/a/text()')
            cityLink = i.xpath('td[1]/a/@href')
            cityName = i.xpath('td[2]/a/text()')
            for j in range(len(cityLink)):
                cityURL = url[:-7] + cityLink[j]
                city.append({'name':cityName[j],'code':cityCode[j],'link':cityURL})
        city_all.extend(city) #所有省的城市信息合并在一起
    return city_all

# 获取区级代码函数---多线程实现
def getCounty(url_list):
    queue_county = Queue() #队列
    thread_num = 10 #进程数
    county = [] #记录区级信息的字典（全局）
    
    def produce_url(url_list):
        for url in url_list:
            queue_county.put(url) # 生成URL存入队列，等待其他线程提取
    
    def getData():
        while not queue_county.empty(): # 保证url遍历结束后能退出线程
            url = queue_county.get() # 从队列中获取URL
            data = getUrl(url)
            selector = etree.HTML(data)
            countyList = selector.xpath('//tr[@class="countytr"]')
            #下面是爬取每个区的代码、URL
            for i in countyList:
                countyCode = i.xpath('td[1]/a/text()')
                countyLink = i.xpath('td[1]/a/@href')
                countyName = i.xpath('td[2]/a/text()')
                #上面得到的是列表形式的，下面将其每一个用字典存储
                for j in range(len(countyLink)):
                    countyURL = url[:-9] + countyLink[j]
                    county.append({'code':countyCode[j],'link':countyURL,'name':countyName[j]})
                
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
    return county

# 获取街道代码函数---多线程实现
def getTown(url_list):
    queue_town = Queue() #队列
    thread_num = 50 #进程数
    town = [] #记录街道信息的字典（全局）
    
    def produce_url(url_list):
        for url in url_list:
            queue_town.put(url) # 生成URL存入队列，等待其他线程提取
    
    def getData():
        while not queue_town.empty(): # 保证url遍历结束后能退出线程
            url = queue_town.get() # 从队列中获取URL
            data = getUrl(url)
            selector = etree.HTML(data)
            townList = selector.xpath('//tr[@class="towntr"]')
            #下面是爬取每个区的代码、URL
            for i in townList:
                townCode = i.xpath('td[1]/a/text()')
                townLink = i.xpath('td[1]/a/@href')
                townName = i.xpath('td[2]/a/text()')
                #上面得到的是列表形式的，下面将其每一个用字典存储
                for j in range(len(townLink)):
                    # 中山市、东莞市的处理
                    if url == 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/44/4419.html' or url == 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/44/4420.html':
                        townURL = url[:-9] + townLink[j]
                    else:
                        townURL = url[:-11] + townLink[j]
                    town.append({'code':townCode[j],'link':townURL,'name':townName[j]})
                
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
    return town

# 获取居委会代码函数---多线程实现
def getVillage(url_list):
    queue_village = Queue() #队列
    thread_num = 200 #进程数
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

###########################
###########################
#省级信息获取
pro = getProvince("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html")
df_province = pd.DataFrame(pro)
df_province.info()
# 信息写入csv文件
df_province.to_csv('province.csv', sep=',', header=True, index=False)

###########################
#市级信息获取
city = getCity(df_province['link'])
df_city = pd.DataFrame(city)
df_city.info()
# 信息写入csv文件
df_city.to_csv('city.csv', sep=',', header=True, index=False)

###########################
#区级信息获取
county = getCounty(df_city['link'])
df_county = pd.DataFrame(county)
# 排序:由于多线程的关系，数据的顺序已经被打乱，所以这里按照区代码进行“升序”排序。
df_county_sorted = df_county.sort_values(by = ['code']) #按1列进行升序排序
df_county_sorted.info()
# 信息写入csv文件
df_county_sorted.to_csv('county.csv', sep=',', header=True, index=False)

###########################
#街道信息获取
#中山市、东莞市的特殊处理（他们的链接在df_city中）
url_list = list()
for url in df_county['link']:
    url_list.append(url)
town_link_list = df_city[df_city['name'].isin(['中山市','东莞市'])]['link'].values
for town_link in town_link_list:
    url_list.append(town_link)
town = getTown(url_list)
df_town = pd.DataFrame(town)
# 排序:由于多线程的关系，数据的顺序已经被打乱，所以这里按照街道代码进行“升序”排序。
df_town_sorted = df_town.sort_values(by = ['code']) #按1列进行升序排序
df_town_sorted.info()
# 信息写入csv文件
df_town_sorted.to_csv('town.csv', sep=',', header=True, index=False)

###########################
#居委会信息获取
village = getVillage(df_town['link'])
df_village = pd.DataFrame(village)
# 排序:由于多线程的关系，数据的顺序已经被打乱，所以这里按照街道代码进行“升序”排序。
df_village_sorted = df_village.sort_values(by = ['code']) #按1列进行升序排序
df_village_sorted.info()
# 信息写入csv文件
df_village_sorted.to_csv('village.csv', sep=',', header=True, index=False)
