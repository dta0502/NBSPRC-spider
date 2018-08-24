# 国家统计用区划代码和城乡划分代码---源码、详细分析、数据

这里实现了`国家统计用区划代码和城乡划分代码`的爬取。本仓库包含：
- 爬虫完整代码---[Urban-and-rural-statistics-spider.py](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Urban-and-rural-statistics-spider.py)
- 居委会级爬虫代码（因为内存不足，所以这里分段爬取，最后合并csv文件）---[Village-Spider-Test.py](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Village-Spider-Test.py)
- 本次设计的详细说明\
    [页面分析](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E9%A1%B5%E9%9D%A2%E5%88%86%E6%9E%90.md)\
    [国家统计局的统计用区划代码和城乡划分代码爬取---第一版](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E7%AC%AC%E4%B8%80%E7%89%88.md)\
    [问题分析](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E9%97%AE%E9%A2%98%E5%88%86%E6%9E%90.md)\
    [国家统计局的统计用区划代码和城乡划分代码爬取---最终版](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E7%AC%AC%E4%BA%8C%E7%89%88%EF%BC%88%E6%9C%80%E7%BB%88%E7%89%88%EF%BC%89.md)
- 爬取的2016年统计用区划代码和城乡划分代码(截止2016年07月31日)数据\
    [省级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/province.csv)\
    [市级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/city.csv)\
    [区级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/county.csv)\
    [街道数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/town.csv)


## 总体说明
[统计局网站提供的页面](http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html)按照：`省-市-县-镇-村`这样的层次关系来组织页面。统计局的网站对于爬虫的限制也不多，我只使用一个ip爬取全部数据的过程中请求被拒绝的情况很少。

### 本设计主要调用的第三方库
- requests---我这里用来请求网站。
- lxml---HTML/XML的解析器，主要功能是解析和提取HTML/XML数据。
- fake_useragent---伪装请求头的库。
- threading---多线程库，加快爬取速度。

### 设计遇到的问题---[问题分析](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E9%97%AE%E9%A2%98%E5%88%86%E6%9E%90.md)
- 中文乱码问题
- 多线程碰到的问题1---csv文件中出现很多空值
- 多线程碰到的问题2---信息顺序混乱
- 数据量过大，内存不足

### 改进版本
在解决了上述问题以后，我通过:
- [完整代码](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Urban-and-rural-statistics-spider.py)爬取了省级、市级、区级、街道的信息。
- [居委会级爬虫代码](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Village-Spider-Test.py)分段爬取了居委会的信息。





