
# Python合并多个csv文件

## 导入所需的包


```python
import os
import pandas as pd
import glob
```

## 合并多个csv文件


```python
csv_list = glob.glob('*.csv') #查看同文件夹下的csv文件数
print(u'共发现%s个CSV文件'% len(csv_list))
print(u'正在处理............')
for i in csv_list: #循环读取同文件夹下的csv文件
    fr = open(i,'rb').read()
    with open('result.csv','ab') as f: #将结果保存为result.csv
        f.write(fr)
print(u'合并完毕！')
```

    共发现9个CSV文件
    正在处理............
    合并完毕！
    

## 去重函数
这个函数将重复的内容去掉，主要是去表头。


```python
df = pd.read_csv("result.csv",header=0)
```


```python
df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 659867 entries, 0 to 659866
    Data columns (total 3 columns):
    UrbanRuralCode    659867 non-null object
    code              659867 non-null object
    name              659867 non-null object
    dtypes: object(3)
    memory usage: 15.1+ MB
    


```python
IsDuplicated = df.duplicated()
```


```python
True in IsDuplicated
```




    True



这说明了这个DataFrame格式的数据含有重复项。

**DataFrame.drop_duplicates函数的使用**
```python
DataFrame.drop_duplicates(subset=None, keep='first', inplace=False)
```
- subset : column label or sequence of labels, optional  
用来指定特定的列，默认所有列
- keep : {‘first’, ‘last’, False}, default ‘first’  
删除重复项并保留第一次出现的项
- inplace : boolean, default False   
是直接在原来数据上修改还是保留一个副本


```python
datalist = df.drop_duplicates(keep = False)
```


```python
datalist.info()
```

    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 659859 entries, 0 to 659866
    Data columns (total 3 columns):
    UrbanRuralCode    659859 non-null object
    code              659859 non-null object
    name              659859 non-null object
    dtypes: object(3)
    memory usage: 20.1+ MB
    

## 排序函数


```python
datalist_sorted = datalist.sort_values(by = ['code']) #按1列进行升序排序
```

## 结果写入csv文件


```python
datalist_sorted.to_csv("village_all.csv", sep = ',', header = True,index = False)
```

## 问题

### Python读取文件问题
#### 错误信息
```
"UnicodeDecodeError: 'gbk' codec can't decode byte 0x80 in position 205: illegal multibyte sequence"  
```
#### 解决方案
```python
fr = open(i,'r').read() 改为 fr = open(i,'rb').read()
with open('result.csv','a') as f: 改为 with open('result.csv','ab') as f:
```

### 重复值问题
这里我合并了9个csv文件，检查最后合并结果发现，里面还有**一个列名**。这是因为9个为文件，其中8个的列名被认为是DataFrame的值，第1个的列名依旧为列名，然后再去重的过程中，8个相同值被保留了1个，所以这会导致最后的csv文件多了**一个列名**。
#### 解决方案
```python
IsDuplicated = df.duplicated() 改为 IsDuplicated = df.duplicated(keep = False) #重复数据全部去除
```

