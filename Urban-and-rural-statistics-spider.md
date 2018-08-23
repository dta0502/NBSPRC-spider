
# 国家统计局的统计用区划代码和城乡划分代码爬取
[统计局网站提供的页面](http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html)按照：`省-市-县-镇-村`这样的层次关系来组织页面。我要把整个五个层级的`城乡代码`、`城乡名称`、`链接`全部进行爬取。

## 导入库


```python
import requests
from lxml import etree
import csv
```

## 网页爬取


```python
url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html"
headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
```

这里需要注意一下，国家统计局的统计用区划代码和城乡划分代码网页的编码为`gb2312`。一般我都采用下面的代码来获取页面：
```
data = requests.get(url,headers = headers).text
```
但是在碰到这个编码方式时会出现乱码，所以做出如下改变：


```python
response = requests.get(url,headers = headers)
response.apparent_encoding
```




    'GB2312'




```python
response.encoding = response.apparent_encoding
```


```python
data = response.text
```

## 网页解析

### 省级名称、URL获取


```python
selector = etree.HTML(data)
provinceList = selector.xpath('//*[@class="provincetr"]')
```


```python
provinceList
```




    [<Element tr at 0x54a4c88>,
     <Element tr at 0x54b4148>,
     <Element tr at 0x54b4188>,
     <Element tr at 0x54b41c8>]




```python
for i in provinceList:
    provinceName = i.xpath('//a/text()')
    provinceLink = i.xpath('//a/@href')
```


```python
provinceName = provinceName[:-1] #去掉最后的：京ICP备05034670号
provinceName[0:2]
```




    ['北京市', '天津市']




```python
provinceLink = provinceLink[:-1] #去掉最后的：京ICP备05034670号的链接
provinceLink[0:2]
```




    ['11.html', '12.html']



下面是根据获取到的每个省的链接进行补全，得到真实的URL。


```python
provinceURL = ['0']*len(provinceLink)
for j in range(len(provinceLink)):
    provinceURL[j] = url[:-10] + provinceLink[j]

provinceURL[0:2]
```




    ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/11.html',
     'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/12.html']



### 市级代码、URL获取


```python
cityCode = [] #第二维的数组
cityLink = []
cityName = []
for provURL in provinceURL:
    response = requests.get(provURL,headers = headers)
    response.encoding = response.apparent_encoding
    data = response.text
    selector = etree.HTML(data)
    cityList = selector.xpath('//tr[@class="citytr"]')
    #下面是抓取每一个城市的代码、URL
    Code = [] #第一维的数组：里面存储了一个省下辖的市的信息
    Link = []
    Name = []
    for i in cityList:
        Code.append(i.xpath('td[1]/a/text()'))
        Link.append(i.xpath('td[1]/a/@href'))
        Name.append(i.xpath('td[2]/a/text()'))
    cityCode.append(Code)
    cityLink.append(Link)
    cityName.append(Name)
```


```python
cityCode[3][0:2]
```




    [['140100000000'], ['140200000000']]




```python
cityLink[3][0:2]
```




    [['14/1401.html'], ['14/1402.html']]




```python
cityName[3][0:2]
```




    [['太原市'], ['大同市']]



下面是根据获取到的每个市的链接进行补全，得到真实的URL。


```python
cityLink[0][0][0]
```




    '11/1101.html'




```python
cityURL = cityLink
for i in range(len(cityLink)):
    for j in range(len(cityLink[i])):
        cityURL[i][j][0] = url[:-10] + cityLink[i][j][0]
```


```python
cityURL[3][0:2]
```




    [['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/14/1401.html'],
     ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/14/1402.html']]



### 区级代码、URL获取
由于之前获得的市级链接是多维列表的形式，为了后面能够很方便的获取页面，下面将这个链接转换成一维列表形式。


```python
cityURL_list = []
for i in range(len(cityURL)):
    for j in range(len(cityURL[i])):
        cityURL_list.append(cityURL[i][j][0])
```


```python
cityURL_list[0:2]
```




    ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/11/1101.html',
     'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/12/1201.html']



这里计算下市级区域的个数（为了得到区级信息，需要请求344个url）。


```python
len(cityURL_list)
```




    344



#### 多线程
由于这里的网页请求很多，我将采用多线程来加快速度。


```python
from queue import Queue
from threading import Thread
```


```python
qurl = Queue() #队列
thread_num = 10 #进程数
#下面三个全局变量是每个区的代码、URL、名称信息
countyCode = []
countyURL = []
countyName = []
```


```python
def produce_url(url_list):
    for url in url_list:
        qurl.put(url) # 生成URL存入队列，等待其他线程提取
```


```python
def getCounty():
    while not qurl.empty(): # 保证url遍历结束后能退出线程
        url = qurl.get() # 从队列中获取URL
        response = requests.get(url,headers = headers)
        response.encoding = response.apparent_encoding
        data = response.text
        selector = etree.HTML(data)
        countyList = selector.xpath('//tr[@class="countytr"]')
        #下面是爬取每个区的代码、URL
        for i in countyList:
            countyCode.append(i.xpath('td[1]/a/text()'))
            countyURL.append(i.xpath('td[1]/a/@href'))
            countyName.append(i.xpath('td[2]/a/text()'))
```


```python
def run(url_list):
    produce_url(url_list)
    
    ths = []
    for _ in range(thread_num):
        th = Thread(target = getCounty)
        th.start()
        ths.append(th)
    for th in ths:
        th.join()
```


```python
run(cityURL_list)
```

#### 写入csv文件


```python
with open('county_v1.csv','w',newline = '',encoding = 'utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["countyCode","countyName","countyURL"])
    for i in range(len(countyCode)):
        writer.writerow([countyCode[i],countyName[i],countyURL[i]])
```

#### 多线程碰到的问题1 
之前我采用的是三个列表countyCode、countyURL、countyName分别保存区代码、链接、名称数据，然后保存到csv文件（这步在后面实现），最后发现csv文件中存在`['130203000000'],[],['08/130802.html']`的情况，这不符合情理，因为如果网页爬取成功后，那么必定会获得全部三个数据。我认为这是因为不同进程写入时间先后的关系，导致了列表对应值的错乱。  

**解决办法：可以将三个数据包装成一个字典，每一个区级信息对应一个字典，最后得到的是一个字典的列表。**

#### 多线程碰到的问题2
没有处理好获取页面失败的情况，这种情况应该需要继续爬取，直到成功爬取。  

**解决办法：try except结构，如果爬取失败，就要递归爬取。**

## 模块化代码
本部分实现参考了[Python爬虫练习五：爬取 2017年统计用区划代码和城乡划分代码（附代码与全部数据）](https://blog.csdn.net/weixin_41710905/article/details/81348427)

上面的实现还存在一些问题：  
- 多线程碰到的问题
- 因为没有模块化，代码结构比较混乱

### 总体思路说明
首先我定义了一个网页爬取函数，然后依次定义省级代码获取函数、市级代码获取函数、区级代码获取函数、街道代码获取函数、居委会代码获取函数，这些函数都会调用网页爬取函数。其中区级代码获取函数、街道代码获取函数、居委会代码获取函数这三个函数都是多线程实现爬取的。最后我将爬取得到的数据输出为csv格式文件。

### 库函数导入


```python
import requests
from lxml import etree
import csv
import time
import pandas as pd
from queue import Queue
from threading import Thread
from fake_useragent import UserAgent
```

### 网页爬取函数


```python
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
```

### 获取省级代码函数


```python
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
```


```python
pro = getProvince("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html")
```


```python
df_province = pd.DataFrame(pro)
df_province['link']
```




    0     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    1     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    2     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    3     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    4     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    5     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    6     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    7     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    8     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    9     http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    10    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    11    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    12    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    13    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    14    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    15    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    16    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    17    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    18    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    19    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    20    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    21    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    22    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    23    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    24    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    25    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    26    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    27    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    28    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    29    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    30    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...
    Name: link, dtype: object



#### 信息写入csv文件


```python
df_province.to_csv('province.csv', sep=',', header=True, index=False)
```

### 获取市级代码函数


```python
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
```


```python
city = getCity(df_province['link'])
```


```python
df_city = pd.DataFrame(city)
df_city
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>code</th>
      <th>link</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>110100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>市辖区</td>
    </tr>
    <tr>
      <th>1</th>
      <td>120100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>市辖区</td>
    </tr>
    <tr>
      <th>2</th>
      <td>130100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>石家庄市</td>
    </tr>
    <tr>
      <th>3</th>
      <td>130200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>唐山市</td>
    </tr>
    <tr>
      <th>4</th>
      <td>130300000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>秦皇岛市</td>
    </tr>
    <tr>
      <th>5</th>
      <td>130400000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>邯郸市</td>
    </tr>
    <tr>
      <th>6</th>
      <td>130500000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>邢台市</td>
    </tr>
    <tr>
      <th>7</th>
      <td>130600000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>保定市</td>
    </tr>
    <tr>
      <th>8</th>
      <td>130700000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>张家口市</td>
    </tr>
    <tr>
      <th>9</th>
      <td>130800000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>承德市</td>
    </tr>
    <tr>
      <th>10</th>
      <td>130900000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>沧州市</td>
    </tr>
    <tr>
      <th>11</th>
      <td>131000000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>廊坊市</td>
    </tr>
    <tr>
      <th>12</th>
      <td>131100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>衡水市</td>
    </tr>
    <tr>
      <th>13</th>
      <td>139000000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>省直辖县级行政区划</td>
    </tr>
    <tr>
      <th>14</th>
      <td>140100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>太原市</td>
    </tr>
    <tr>
      <th>15</th>
      <td>140200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>大同市</td>
    </tr>
    <tr>
      <th>16</th>
      <td>140300000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阳泉市</td>
    </tr>
    <tr>
      <th>17</th>
      <td>140400000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>长治市</td>
    </tr>
    <tr>
      <th>18</th>
      <td>140500000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>晋城市</td>
    </tr>
    <tr>
      <th>19</th>
      <td>140600000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>朔州市</td>
    </tr>
    <tr>
      <th>20</th>
      <td>140700000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>晋中市</td>
    </tr>
    <tr>
      <th>21</th>
      <td>140800000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>运城市</td>
    </tr>
    <tr>
      <th>22</th>
      <td>140900000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>忻州市</td>
    </tr>
    <tr>
      <th>23</th>
      <td>141000000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>临汾市</td>
    </tr>
    <tr>
      <th>24</th>
      <td>141100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>吕梁市</td>
    </tr>
    <tr>
      <th>25</th>
      <td>150100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>呼和浩特市</td>
    </tr>
    <tr>
      <th>26</th>
      <td>150200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>包头市</td>
    </tr>
    <tr>
      <th>27</th>
      <td>150300000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>乌海市</td>
    </tr>
    <tr>
      <th>28</th>
      <td>150400000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>赤峰市</td>
    </tr>
    <tr>
      <th>29</th>
      <td>150500000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>通辽市</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>314</th>
      <td>622900000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>临夏回族自治州</td>
    </tr>
    <tr>
      <th>315</th>
      <td>623000000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>甘南藏族自治州</td>
    </tr>
    <tr>
      <th>316</th>
      <td>630100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>西宁市</td>
    </tr>
    <tr>
      <th>317</th>
      <td>630200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>海东市</td>
    </tr>
    <tr>
      <th>318</th>
      <td>632200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>海北藏族自治州</td>
    </tr>
    <tr>
      <th>319</th>
      <td>632300000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>黄南藏族自治州</td>
    </tr>
    <tr>
      <th>320</th>
      <td>632500000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>海南藏族自治州</td>
    </tr>
    <tr>
      <th>321</th>
      <td>632600000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>果洛藏族自治州</td>
    </tr>
    <tr>
      <th>322</th>
      <td>632700000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>玉树藏族自治州</td>
    </tr>
    <tr>
      <th>323</th>
      <td>632800000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>海西蒙古族藏族自治州</td>
    </tr>
    <tr>
      <th>324</th>
      <td>640100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>银川市</td>
    </tr>
    <tr>
      <th>325</th>
      <td>640200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>石嘴山市</td>
    </tr>
    <tr>
      <th>326</th>
      <td>640300000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>吴忠市</td>
    </tr>
    <tr>
      <th>327</th>
      <td>640400000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>固原市</td>
    </tr>
    <tr>
      <th>328</th>
      <td>640500000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>中卫市</td>
    </tr>
    <tr>
      <th>329</th>
      <td>650100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>乌鲁木齐市</td>
    </tr>
    <tr>
      <th>330</th>
      <td>650200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>克拉玛依市</td>
    </tr>
    <tr>
      <th>331</th>
      <td>650400000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>吐鲁番市</td>
    </tr>
    <tr>
      <th>332</th>
      <td>650500000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>哈密市</td>
    </tr>
    <tr>
      <th>333</th>
      <td>652300000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>昌吉回族自治州</td>
    </tr>
    <tr>
      <th>334</th>
      <td>652700000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>博尔塔拉蒙古自治州</td>
    </tr>
    <tr>
      <th>335</th>
      <td>652800000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>巴音郭楞蒙古自治州</td>
    </tr>
    <tr>
      <th>336</th>
      <td>652900000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿克苏地区</td>
    </tr>
    <tr>
      <th>337</th>
      <td>653000000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>克孜勒苏柯尔克孜自治州</td>
    </tr>
    <tr>
      <th>338</th>
      <td>653100000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>喀什地区</td>
    </tr>
    <tr>
      <th>339</th>
      <td>653200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>和田地区</td>
    </tr>
    <tr>
      <th>340</th>
      <td>654000000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>伊犁哈萨克自治州</td>
    </tr>
    <tr>
      <th>341</th>
      <td>654200000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>塔城地区</td>
    </tr>
    <tr>
      <th>342</th>
      <td>654300000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿勒泰地区</td>
    </tr>
    <tr>
      <th>343</th>
      <td>659000000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>自治区直辖县级行政区划</td>
    </tr>
  </tbody>
</table>
<p>344 rows × 3 columns</p>
</div>



#### 信息写入csv文件


```python
df_city.to_csv('city.csv', sep=',', header=True, index=False)
```

### 获取区级代码函数---多线程实现


```python
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
```


```python
county = getCounty(df_city['link'])
```


```python
df_county = pd.DataFrame(county)
df_county
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>code</th>
      <th>link</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>130702000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>桥东区</td>
    </tr>
    <tr>
      <th>1</th>
      <td>130703000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>桥西区</td>
    </tr>
    <tr>
      <th>2</th>
      <td>130705000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>宣化区</td>
    </tr>
    <tr>
      <th>3</th>
      <td>130706000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>下花园区</td>
    </tr>
    <tr>
      <th>4</th>
      <td>130708000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>万全区</td>
    </tr>
    <tr>
      <th>5</th>
      <td>130709000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>崇礼区</td>
    </tr>
    <tr>
      <th>6</th>
      <td>130722000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>张北县</td>
    </tr>
    <tr>
      <th>7</th>
      <td>130723000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>康保县</td>
    </tr>
    <tr>
      <th>8</th>
      <td>130724000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>沽源县</td>
    </tr>
    <tr>
      <th>9</th>
      <td>130725000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>尚义县</td>
    </tr>
    <tr>
      <th>10</th>
      <td>130726000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>蔚县</td>
    </tr>
    <tr>
      <th>11</th>
      <td>130727000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阳原县</td>
    </tr>
    <tr>
      <th>12</th>
      <td>130602000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>竞秀区</td>
    </tr>
    <tr>
      <th>13</th>
      <td>130606000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>莲池区</td>
    </tr>
    <tr>
      <th>14</th>
      <td>130607000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>满城区</td>
    </tr>
    <tr>
      <th>15</th>
      <td>130608000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>清苑区</td>
    </tr>
    <tr>
      <th>16</th>
      <td>130609000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>徐水区</td>
    </tr>
    <tr>
      <th>17</th>
      <td>130623000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>涞水县</td>
    </tr>
    <tr>
      <th>18</th>
      <td>130624000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阜平县</td>
    </tr>
    <tr>
      <th>19</th>
      <td>130626000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>定兴县</td>
    </tr>
    <tr>
      <th>20</th>
      <td>130627000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>唐县</td>
    </tr>
    <tr>
      <th>21</th>
      <td>130628000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>高阳县</td>
    </tr>
    <tr>
      <th>22</th>
      <td>130629000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>容城县</td>
    </tr>
    <tr>
      <th>23</th>
      <td>130630000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>涞源县</td>
    </tr>
    <tr>
      <th>24</th>
      <td>130631000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>望都县</td>
    </tr>
    <tr>
      <th>25</th>
      <td>130632000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>安新县</td>
    </tr>
    <tr>
      <th>26</th>
      <td>130633000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>易县</td>
    </tr>
    <tr>
      <th>27</th>
      <td>130634000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>曲阳县</td>
    </tr>
    <tr>
      <th>28</th>
      <td>130635000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>蠡县</td>
    </tr>
    <tr>
      <th>29</th>
      <td>130636000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>顺平县</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2822</th>
      <td>653128000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>岳普湖县</td>
    </tr>
    <tr>
      <th>2823</th>
      <td>653129000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>伽师县</td>
    </tr>
    <tr>
      <th>2824</th>
      <td>654221000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>额敏县</td>
    </tr>
    <tr>
      <th>2825</th>
      <td>652901000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿克苏市</td>
    </tr>
    <tr>
      <th>2826</th>
      <td>654223000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>沙湾县</td>
    </tr>
    <tr>
      <th>2827</th>
      <td>652922000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>温宿县</td>
    </tr>
    <tr>
      <th>2828</th>
      <td>653130000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>巴楚县</td>
    </tr>
    <tr>
      <th>2829</th>
      <td>654224000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>托里县</td>
    </tr>
    <tr>
      <th>2830</th>
      <td>652923000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>库车县</td>
    </tr>
    <tr>
      <th>2831</th>
      <td>654225000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>裕民县</td>
    </tr>
    <tr>
      <th>2832</th>
      <td>653131000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>塔什库尔干塔吉克自治县</td>
    </tr>
    <tr>
      <th>2833</th>
      <td>654226000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>和布克赛尔蒙古自治县</td>
    </tr>
    <tr>
      <th>2834</th>
      <td>652924000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>沙雅县</td>
    </tr>
    <tr>
      <th>2835</th>
      <td>652925000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>新和县</td>
    </tr>
    <tr>
      <th>2836</th>
      <td>652926000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>拜城县</td>
    </tr>
    <tr>
      <th>2837</th>
      <td>652927000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>乌什县</td>
    </tr>
    <tr>
      <th>2838</th>
      <td>652928000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿瓦提县</td>
    </tr>
    <tr>
      <th>2839</th>
      <td>652929000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>柯坪县</td>
    </tr>
    <tr>
      <th>2840</th>
      <td>659001000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>石河子市</td>
    </tr>
    <tr>
      <th>2841</th>
      <td>659002000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿拉尔市</td>
    </tr>
    <tr>
      <th>2842</th>
      <td>659003000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>图木舒克市</td>
    </tr>
    <tr>
      <th>2843</th>
      <td>659004000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>五家渠市</td>
    </tr>
    <tr>
      <th>2844</th>
      <td>659006000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>铁门关市</td>
    </tr>
    <tr>
      <th>2845</th>
      <td>654301000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿勒泰市</td>
    </tr>
    <tr>
      <th>2846</th>
      <td>654321000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>布尔津县</td>
    </tr>
    <tr>
      <th>2847</th>
      <td>654322000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>富蕴县</td>
    </tr>
    <tr>
      <th>2848</th>
      <td>654323000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>福海县</td>
    </tr>
    <tr>
      <th>2849</th>
      <td>654324000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>哈巴河县</td>
    </tr>
    <tr>
      <th>2850</th>
      <td>654325000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>青河县</td>
    </tr>
    <tr>
      <th>2851</th>
      <td>654326000000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>吉木乃县</td>
    </tr>
  </tbody>
</table>
<p>2852 rows × 3 columns</p>
</div>



#### 排序
由于多线程的关系，数据的顺序已经被打乱，所以这里按照区代码进行“升序”排序。


```python
df_county_sorted = df_county.sort_values(by = ['code']) #按1列进行升序排序
```

#### 信息写入csv文件


```python
df_county_sorted.to_csv('county.csv', sep=',', header=True, index=False)
```

### 获取街道代码函数---多线程实现


```python
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
```


```python
town = getTown(df_county['link'])
```


```python
df_town = pd.DataFrame(town)
df_town
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>code</th>
      <th>link</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>130706001000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>城镇街道办事处</td>
    </tr>
    <tr>
      <th>1</th>
      <td>130706002000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>煤矿街道办事处</td>
    </tr>
    <tr>
      <th>2</th>
      <td>130706200000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>花园乡</td>
    </tr>
    <tr>
      <th>3</th>
      <td>130706201000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>辛庄子乡</td>
    </tr>
    <tr>
      <th>4</th>
      <td>130706202000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>定方水乡</td>
    </tr>
    <tr>
      <th>5</th>
      <td>130706203000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>段家堡乡</td>
    </tr>
    <tr>
      <th>6</th>
      <td>130702001000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>红旗楼街道办事处</td>
    </tr>
    <tr>
      <th>7</th>
      <td>130702002000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>胜利北路街道办事处</td>
    </tr>
    <tr>
      <th>8</th>
      <td>130702003000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>五一路街道办事处</td>
    </tr>
    <tr>
      <th>9</th>
      <td>130702004000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>花园街街道办事处</td>
    </tr>
    <tr>
      <th>10</th>
      <td>130702005000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>工业路街道办事处</td>
    </tr>
    <tr>
      <th>11</th>
      <td>130702101000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>姚家庄镇</td>
    </tr>
    <tr>
      <th>12</th>
      <td>130623001000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>城区社区管理办公室街道办事处</td>
    </tr>
    <tr>
      <th>13</th>
      <td>130624100000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阜平镇</td>
    </tr>
    <tr>
      <th>14</th>
      <td>130624101000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>龙泉关镇</td>
    </tr>
    <tr>
      <th>15</th>
      <td>130626100000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>定兴镇</td>
    </tr>
    <tr>
      <th>16</th>
      <td>130623100000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>涞水镇</td>
    </tr>
    <tr>
      <th>17</th>
      <td>130624102000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>平阳镇</td>
    </tr>
    <tr>
      <th>18</th>
      <td>130624103000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>城南庄镇</td>
    </tr>
    <tr>
      <th>19</th>
      <td>130624104000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>天生桥镇</td>
    </tr>
    <tr>
      <th>20</th>
      <td>130624105000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>王林口镇</td>
    </tr>
    <tr>
      <th>21</th>
      <td>130624202000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>台峪乡</td>
    </tr>
    <tr>
      <th>22</th>
      <td>130624203000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>大台乡</td>
    </tr>
    <tr>
      <th>23</th>
      <td>130624204000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>史家寨乡</td>
    </tr>
    <tr>
      <th>24</th>
      <td>130624205000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>砂窝乡</td>
    </tr>
    <tr>
      <th>25</th>
      <td>130724100000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>平定堡镇</td>
    </tr>
    <tr>
      <th>26</th>
      <td>130724101000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>小厂镇</td>
    </tr>
    <tr>
      <th>27</th>
      <td>130724102000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>黄盖淖镇</td>
    </tr>
    <tr>
      <th>28</th>
      <td>130724103000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>九连城镇</td>
    </tr>
    <tr>
      <th>29</th>
      <td>130724200000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>高山堡乡</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>42532</th>
      <td>659002509000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团十六团</td>
    </tr>
    <tr>
      <th>42533</th>
      <td>659002511000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团第一师水利水电工程处</td>
    </tr>
    <tr>
      <th>42534</th>
      <td>659002512000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团第一师塔里木灌区水利管理处</td>
    </tr>
    <tr>
      <th>42535</th>
      <td>659002513000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿拉尔农场</td>
    </tr>
    <tr>
      <th>42536</th>
      <td>659002514000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团第一师幸福农场</td>
    </tr>
    <tr>
      <th>42537</th>
      <td>659002515000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>中心监狱</td>
    </tr>
    <tr>
      <th>42538</th>
      <td>659002516000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团一团</td>
    </tr>
    <tr>
      <th>42539</th>
      <td>659002517000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团农一师沙井子水利管理处</td>
    </tr>
    <tr>
      <th>42540</th>
      <td>659002518000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>西工业园区管理委员会</td>
    </tr>
    <tr>
      <th>42541</th>
      <td>659002519000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团二团</td>
    </tr>
    <tr>
      <th>42542</th>
      <td>659002520000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>兵团三团</td>
    </tr>
    <tr>
      <th>42543</th>
      <td>522701001000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>广惠街道办事处</td>
    </tr>
    <tr>
      <th>42544</th>
      <td>522701002000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>文峰街道办事处</td>
    </tr>
    <tr>
      <th>42545</th>
      <td>522701004000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>小围寨街道办事处</td>
    </tr>
    <tr>
      <th>42546</th>
      <td>522701005000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>沙包堡街道办事处</td>
    </tr>
    <tr>
      <th>42547</th>
      <td>522701006000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>绿茵湖街道办事处</td>
    </tr>
    <tr>
      <th>42548</th>
      <td>522701106000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>墨冲镇</td>
    </tr>
    <tr>
      <th>42549</th>
      <td>522701107000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>平浪镇</td>
    </tr>
    <tr>
      <th>42550</th>
      <td>522701110000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>毛尖镇</td>
    </tr>
    <tr>
      <th>42551</th>
      <td>522701111000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>匀东镇</td>
    </tr>
    <tr>
      <th>42552</th>
      <td>522701208000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>归兰水族乡</td>
    </tr>
    <tr>
      <th>42553</th>
      <td>652928100000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿瓦提镇</td>
    </tr>
    <tr>
      <th>42554</th>
      <td>652928101000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>乌鲁却勒镇</td>
    </tr>
    <tr>
      <th>42555</th>
      <td>652928102000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>拜什艾日克镇</td>
    </tr>
    <tr>
      <th>42556</th>
      <td>652928200000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿依巴格乡</td>
    </tr>
    <tr>
      <th>42557</th>
      <td>652928201000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>塔木托格拉克乡</td>
    </tr>
    <tr>
      <th>42558</th>
      <td>652928202000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>英艾日克乡</td>
    </tr>
    <tr>
      <th>42559</th>
      <td>652928203000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>多浪乡</td>
    </tr>
    <tr>
      <th>42560</th>
      <td>652928204000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>巴格托格拉克乡</td>
    </tr>
    <tr>
      <th>42561</th>
      <td>652928405000</td>
      <td>http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhf...</td>
      <td>阿克苏监狱</td>
    </tr>
  </tbody>
</table>
<p>42562 rows × 3 columns</p>
</div>



#### 排序
由于多线程的关系，数据的顺序已经被打乱，所以这里按照街道代码进行“升序”排序。


```python
df_town_sorted = df_town.sort_values(by = ['code']) #按1列进行升序排序
```

#### 信息写入csv文件


```python
df_town_sorted.to_csv('town.csv', sep=',', header=True, index=False)
```

### 获取居委会代码函数---多线程实现


```python
def getVillage(url_list):
    queue_village = Queue() #队列
    thread_num = 200 #进程数
    town = [] #记录街道信息的字典（全局）
    
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
                    town.append({'code':villageCode[j],'UrbanRuralCode':UrbanRuralCode[j],'name':villageName[j]})
                
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
```


```python
village = getVillage(df_town['link'])
```

    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/14/07/24/140724204.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/14/07/27/140727400.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/14/10/29/141029204.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/01/04/150104008.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/14/09/81/140981102.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/01/02/150102001.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/14/09/81/140981210.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/04/21/150421202.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/04/25/150425100.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/04/22/150422401.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/04/02/150402402.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/04/30/150430207.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/01/21/150121105.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/07/22/150722105.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/15/25/26/152526103.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/21/04/21/210421209.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/21/04/22/210422108.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/21/05/02/210502002.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/21/06/03/210603007.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/21/05/02/210502010.html
    requests fail, retry!
    http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/21/05/03/210503005.html
    requests fail, retry!
    

由于数据量很大，所以这里我没有爬取完毕。
