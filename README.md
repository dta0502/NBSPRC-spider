# 国家统计用区划代码和城乡划分代码---源码、详细分析、数据

---
2019.05.25更新：
- [x] 添加了爬虫代码使用说明
- [x] 添加了依赖`requirements.txt`

2018.12.02更新：
- [x] 修改[爬虫代码](https://github.com/dta0502/NBSPRC-spider/blob/master/Urban-and-rural-statistics-spider.py)，添加了中山市/东莞市下面没有区级单位的异常处理
- [x] 页面源码的编码为`GB2312`，实际为`GBK`，因此手工指定编码为`GBK`：[Issues #2](https://github.com/dta0502/NBSPRC-spider/issues/2)

2018.11.30更新：
- [x] 更新`village.csv`文件，按照`code`顺序从小到大排列，看起来更方便
- [x] 更新**数据总结**中的错误

2018.11.10更新：
- [x] 缺失数据补充:[Issues #1](https://github.com/dta0502/NBSPRC-spider/issues/1)

---


## 一、本仓库介绍
统计局网站提供的[2016年统计用区划代码和城乡划分代码(截止2016年07月31日)](http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html)按照：`省-市-县-镇-村`这样的层次关系来组织页面。统计局的网站对于爬虫的限制也不多，我只使用一个ip就爬取全部数据，爬取的过程中请求被拒绝的情况很少。

本仓库包含：

- 代码文件：
  - [爬虫完整代码](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Urban-and-rural-statistics-spider.py)
  - [居委会级爬虫代码](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/Village-Spider-Test.py)
  - [居委会数据合并代码](https://github.com/dta0502/NBSPRC-spider/blob/master/%E5%90%88%E5%B9%B6%E5%A4%9A%E4%B8%AAcsv%E6%96%87%E4%BB%B6.py)

- 2016年统计用区划代码和城乡划分代码数据文件：
  - [省级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/province.csv)
  - [市级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/city.csv)
  - [区级数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/county.csv)
  - [街道数据.csv](https://github.com/dta0502/China-zoning-code-for-statistics-spider/blob/master/data/town.csv)
  - [居委会数据.csv](https://github.com/dta0502/NBSPRC-spider/blob/master/data/village.csv)

- **页面分析、代码详细说明见个人博客**：
  - [国家统计局统计用区划代码和城乡划分代码爬虫-（一）页面分析](https://dta0502.github.io/archives/a4d70246.html)
  - [国家统计局统计用区划代码和城乡划分代码爬虫-（二）总体实现](https://dta0502.github.io/archives/796bd537.html)
  - [Python合并多个csv文件](https://dta0502.github.io/archives/616c581b.html)

## 二、如何使用
### 1、安装依赖
```bash
python3 -m pip install -r requirements.txt
```

### 2、一次性爬取全部数据
```bash
python3 ./Urban-and-rural-statistics-spider.py
```

### 3、居委会级数据分段爬取使用说明
居委会级数据量比较大，一次性爬取可能会出现内存不足，所以我提供了一种**居委会级数据分段爬取，最后合并各段数据的方法**，具体方法如下：
- 省、市、区、街道使用[爬虫完整代码](https://github.com/dta0502NBSPRC-spider/blob/master/Urban-and-rural-statistics-spider.py)，其中[居委级爬取部分](https://github.com/dta0502/NBSPRC-spider/blobcf26c7ade170eef874603969fd3858a4cdb747e6Urban-and-rural-statistics-spider.py#L231-L239)注释掉，然后执行：

```bash
python3 ./Urban-and-rural-statistics-spider.py
```

以上爬取完成后，可以看到此目录下已经含有了`town.csv`文件。

- 然后手动更改[居委会级爬代码](https://github.com/dta0502/NBSPRC-spider/blob/masterUrban-and-rural-statistics-spider.py)，具体要修改的部分如下：

```python
df_town = pd.read_csv("town.csv",encoding = 'utf-8')
village = getVillage(df_town['link'][0:10000])

df_village = pd.DataFrame(village)
# 信息写入csv文件
df_village.to_csv('village-0.csv', sep=',', header=True, index=False)
```

例如：第一次设置`village = getVillage(df_town['link'][0:10000])`中的爬取链接为`[0-10000]`，同时设置`df_village.to_csv('village-0.csv', sep=',', header=True, index=False)`中的保存文件名为`village-0.csv`。

- 执行[居委会级爬代码](https://github.com/dta0502/NBSPRC-spider/blob/masterUrban-and-rural-statistics-spider.py)：

```bash
python3 ./Village-Spider-Test.py
```

完成第一段爬取后，然后再手动更改爬取链接为`[10000,20000]`，同时保存文件名改为`village-1.csv`，执行以上命令，以此类推，直到全部爬取完成。

- 全部爬取完毕后，复制各段数据到一个空目录下，在此目录下执行如下代码：

```bash
python3 ./合并多个csv文件.py
```

至此，数据合并完毕，得到完整的居委会级数据。

## 三、数据总结
截止2016年07月31日，我国共有：
- 31个省
- 344个市
- 2852个区
- 42927个街道
- 665062个居委会
