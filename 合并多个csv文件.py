# coding: utf-8

# 导入所需的包
import os
import pandas as pd
import glob

# 合并多个csv文件
csv_list = glob.glob('*.csv') #查看同文件夹下的csv文件数
print(u'共发现%s个CSV文件'% len(csv_list))
print(u'正在处理............')
for i in csv_list: #循环读取同文件夹下的csv文件
    fr = open(i,'rb').read()
    with open('result.csv','ab') as f: #将结果保存为result.csv
        f.write(fr)
print(u'合并完毕！')

# 去重函数
# 这个函数将重复的内容去掉，主要是去表头。
df = pd.read_csv("result.csv",header=0)
datalist = df.drop_duplicates(keep = False)

# 排序函数
datalist_sorted = datalist.sort_values(by = ['code']) #按1列进行升序排序

# 结果写入csv文件
datalist_sorted.to_csv("village_all.csv", sep = ',', header = True,index = False)

