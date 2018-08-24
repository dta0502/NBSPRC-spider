# 国家统计用区划代码和城乡划分代码---源码、详细分析、数据

这里实现了`国家统计用区划代码和城乡划分代码`的爬取。本仓库包含：
- 爬虫完整代码---[Urban-and-rural-statistics-spider.py](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Urban-and-rural-statistics-spider.py)
- 本次设计的详细说明---[Urban-and-rural-statistics-spider.md](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Urban-and-rural-statistics-spider.md)
- 爬取的2016年统计用区划代码和城乡划分代码(截止2016年07月31日)数据\
    [省级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/province.csv)\
    [市级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/city.csv)\
    [区级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/county.csv)\
    [街道数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/town.csv)
- 居委会级爬虫代码（因为内存不足，所以这里分段爬取，最后合并csv文件）---[Village-Spider-Test.py](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Village-Spider-Test.py)

## 总体说明
[统计局网站提供的页面](http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html)按照：`省-市-县-镇-村`这样的层次关系来组织页面。统计局的网站对于爬虫的限制也不多，我只使用一个ip爬取全部数据的过程中请求被拒绝的情况很少。

### 本设计主要调用的第三方库
- requests---我这里用来请求网站。
- lxml---HTML/XML的解析器，主要功能是解析和提取HTML/XML数据。
- fake_useragent---伪装请求头的库。
- threading---多线程库，加快爬取速度。

### 设计遇到的问题
#### 1）中文乱码问题
分析requests的源代码发现，text返回的是处理过的Unicode型的数据，而使用content返回的是bytes型的原始数据。也就是说，r.content相对于r.text来说节省了计算资源，content是把内容bytes返回. 而text是decode成Unicode。

如果直接采用下面的代码获取数据，会出现中文乱码的问题。
```python
data = requests.get(url,headers = headers).text
```
**原因在于：《HTTP权威指南》里第16章国际化里提到，如果HTTP响应中Content-Type字段没有指定charset，则默认页面是'ISO-8859-1'编码。这处理英文页面当然没有问题，但是中文页面，就会有乱码了！**

**解决办法：如果在确定使用text，并已经得知该站的字符集编码（使用apparent_encoding可以获得真实编码）时，可以使用 r.encoding = ‘xxx’ 模式， 当你指定编码后，requests在text时会根据你设定的字符集编码进行转换。**
```python
>>> response = requests.get(url,headers = headers)
>>> response.apparent_encoding
'GB2312'
>>> response.encoding = response.apparent_encoding
>>> data = response.text
```
这样就不会有中文乱码的问题了。

#### 2）多线程碰到的问题1---csv文件中出现很多空值
下面是出现这个问题的区级信息获取的部分代码：
```python
qurl = Queue() #队列
thread_num = 10 #进程数
#下面三个全局变量是每个区的代码、URL、名称信息
countyCode = []
countyURL = []
countyName = []

def produce_url(url_list):
    for url in url_list:
        qurl.put(url) # 生成URL存入队列，等待其他线程提取

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

def run(url_list):
    produce_url(url_list)
    
    ths = []
    for _ in range(thread_num):
        th = Thread(target = getCounty)
        th.start()
        ths.append(th)
    for th in ths:
        th.join()

run(cityURL_list)
```
这里有几个问题：\
首先，下面这个解析代码获取的是一个列表：
```python
i.xpath('td[1]/a/text()
```
而外面套着的append操作则使得列表嵌套列表（生成一个二维列表）：
```python
countyCode.append(i.xpath('td[1]/a/text()'))
```
同时又有三个全部变量来存储数据：
```python
#下面三个全局变量是每个区的代码、URL、名称信息
countyCode = []
countyURL = []
countyName = []
```

在单线程下，这个操作是没有问题的，但是由于这里是多线程实现，多个线程同时运行，例如：线程1写入countyCode这个全局变量，然后在写入countyURL这个变量之前，线程2写入了它对应的countyURL，导致了线程1的countyCode对应了线程2的countyURL，这样整个列表对应顺序出现了错乱。

**解决办法：使用字典封装每个区的三个信息，这部分实现如下代码所示。**
```python
county = [] #记录区级信息的字典（全局）
        #下面是爬取每个区的代码、URL
        for i in countyList:
            countyCode = i.xpath('td[1]/a/text()')
            countyLink = i.xpath('td[1]/a/@href')
            countyName = i.xpath('td[2]/a/text()')
            #上面得到的是列表形式的，下面将其每一个用字典存储
            for j in range(len(countyLink)):
                countyURL = url[:-9] + countyLink[j]
                county.append({'code':countyCode[j],'link':countyURL,'name':countyName[j]})
```
这样在多线程操作时，每个线程写入的都是完整的一个区的信息，不会出现对应错误。

#### 3）多线程碰到的问题2---信息顺序混乱
这是多线程无法避免的问题，不同线程写入时间存在先后关系。我这里先完成多线程信息采集，然后对这个“字典”列表进行排序，最后再写入csv文件。代码如下所示：
```python
county = getCounty(df_city['link'])
df_county = pd.DataFrame(county)
df_county_sorted = df_county.sort_values(by = ['code']) #按1列进行升序排序
df_county_sorted.to_csv('county.csv', sep=',', header=True, index=False)
```

#### 4）数据量过大，内存不足
我把整个爬虫放到1G内存的VPS上进行爬取，运行一段时间后就会被killed。我查看日志发现，这是内存不足导致的，OOM killer杀死了这个占用很大内存的非内核进程以防止内存耗尽影响系统运行。具体分析见：[Linux下Python程序Killed，分析其原因](https://blog.csdn.net/dta0502/article/details/82016616)。\
最后我采取分段爬取居委会一级的数据，每次爬取5000个街道的URL，具体代码：
```python
village = getVillage(df_town['link'][0:5000])
df_village = pd.DataFrame(village)
# 信息写入csv文件
df_village.to_csv('village-0.csv', sep=',', header=True, index=False)
```
最后将所有爬取得到的csv文件进行合并得到全部居委会信息。

