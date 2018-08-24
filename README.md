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

### 
