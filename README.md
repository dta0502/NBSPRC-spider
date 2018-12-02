# 国家统计用区划代码和城乡划分代码---源码、详细分析、数据

---

2018.12.02更新：
- 修改[爬虫代码](https://github.com/dta0502/NBSPRC-spider/blob/master/Urban-and-rural-statistics-spider.py)，添加了中山市/东莞市下面没有区级单位的异常处理
- 页面源码的编码为`GB2312`，实际为`GBK`，因此手工指定编码为`GBK`：[Issues #2](https://github.com/dta0502/NBSPRC-spider/issues/2)

2018.11.30更新：
- 更新`village.csv`文件，按照`code`顺序从小到大排列，看起来更方便
- 更新**数据总结**中的错误

2018.11.10更新：
- 缺失数据补充:[Issues #1](https://github.com/dta0502/NBSPRC-spider/issues/1)

---



**详细分析见个人博客：[国家统计局统计用区划代码和城乡划分代码---爬虫、详细分析](https://blog.csdn.net/dta0502/article/details/82024462)。**

这里实现了`国家统计用区划代码和城乡划分代码`的爬取。本仓库包含：
- 爬虫完整代码---[Urban-and-rural-statistics-spider.py](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Urban-and-rural-statistics-spider.py)
- 居委会级爬虫代码（因为内存不足，所以这里分段爬取，最后合并csv文件）---[Village-Spider-Test.py](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Village-Spider-Test.py)
- 居委会数据合并代码---[合并多个csv文件.py](https://github.com/dta0502/NBSPRC-spider/blob/master/%E5%90%88%E5%B9%B6%E5%A4%9A%E4%B8%AAcsv%E6%96%87%E4%BB%B6.py)
- 本次设计的详细说明\
    [页面分析](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E9%A1%B5%E9%9D%A2%E5%88%86%E6%9E%90.md)\
    [国家统计局的统计用区划代码和城乡划分代码爬取---第一版](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E7%AC%AC%E4%B8%80%E7%89%88.md)\
    [问题分析](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E9%97%AE%E9%A2%98%E5%88%86%E6%9E%90.md)\
    [国家统计局的统计用区划代码和城乡划分代码爬取---最终版](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E7%AC%AC%E4%BA%8C%E7%89%88%EF%BC%88%E6%9C%80%E7%BB%88%E7%89%88%EF%BC%89.md)\
    [合并多个csv文件代码说明](https://github.com/dta0502/NBSPRC-spider/blob/master/docs/%E5%90%88%E5%B9%B6%E5%A4%9A%E4%B8%AAcsv%E6%96%87%E4%BB%B6.md)
- 爬取的2016年统计用区划代码和城乡划分代码(截止2016年07月31日)数据\
    [省级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/province.csv)\
    [市级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/city.csv)\
    [区级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/county.csv)\
    [街道数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/town.csv)\
    [居委会数据.csv](https://github.com/dta0502/NBSPRC-spider/blob/master/data/village.csv)

## 总体说明
统计局网站提供的[2016年统计用区划代码和城乡划分代码(截止2016年07月31日)](http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html)按照：`省-市-县-镇-村`这样的层次关系来组织页面。统计局的网站对于爬虫的限制也不多，我只使用一个ip就爬取全部数据，爬取的过程中请求被拒绝的情况很少。

### [设计遇到的问题](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E9%97%AE%E9%A2%98%E5%88%86%E6%9E%90.md)
- 中文乱码问题
- 多线程碰到的问题1---csv文件中出现很多空值
- 多线程碰到的问题2---信息顺序混乱
- 数据量过大，内存不足

### [改进版本](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/docs/%E7%AC%AC%E4%BA%8C%E7%89%88%EF%BC%88%E6%9C%80%E7%BB%88%E7%89%88%EF%BC%89.md)
在解决了上述问题以后，我通过:
- [完整代码](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Urban-and-rural-statistics-spider.py)爬取了省级、市级、区级、街道的信息。
- [居委会级爬虫代码](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Village-Spider-Test.py)分段爬取了居委会的信息。
- [居委会数据合并代码](https://github.com/dta0502/NBSPRC-spider/blob/master/%E5%90%88%E5%B9%B6%E5%A4%9A%E4%B8%AAcsv%E6%96%87%E4%BB%B6.py)得到了合并、排序后居委会信息。

### 数据总结
截止2016年07月31日，我国共有：
- 31个省
- 344个市
- 2852个区
- 42927个街道
- 665062个居委会


