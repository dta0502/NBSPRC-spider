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
- requests:我这里用来请求网站。
- lxml:Html/XML的解析器，主要功能是解析和提取HTML/XML数据。
- fake_useragent:伪装请求头的库。
- threading:多线程库，加快爬取速度

### 设计遇到的问题
#### 1）中文乱码问题
分析requests的源代码发现，text返回的是处理过的Unicode型的数据，而使用content返回的是bytes型的原始数据。也就是说，r.content相对于r.text来说节省了计算资源，content是把内容bytes返回. 而text是decode成Unicode。\
如果直接采用下面的代码获取数据，会出现中文乱码的问题。
```python
data = requests.get(url,headers = headers).text
```
**原因在于：《HTTP权威指南》里第16章国际化里提到，如果HTTP响应中Content-Type字段没有指定charset，则默认页面是'ISO-8859-1'编码。这处理英文页面当然没有问题，但是中文页面，就会有乱码了！**\
**解决办法：如果在确定使用text，并已经得知该站的字符集编码（使用apparent_encoding可以获得真实编码）时，可以使用 r.encoding = ‘xxx’ 模式， 当你指定编码后，requests在text时会根据你设定的字符集编码进行转换。**
```python
>>> response = requests.get(url,headers = headers)
>>> response.apparent_encoding
'GB2312'
>>> response.encoding = response.apparent_encoding
>>> data = response.text
```
这样就不会有中文乱码的问题了。

