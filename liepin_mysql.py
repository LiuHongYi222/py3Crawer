# -*- coding: UTF-8 -*-

import pymysql

# 打开数据库连接
db = pymysql.connect("134.175.0.45", "root", "583821", "jobCrawer")

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# SQL 插入语句
sql = "INSERT INTO liepin( positionName,city,companyName,salary,workYear,education,createTime,welfare) \
       VALUES ('%s', '%s','%s','%s','%s','%s','%s','%s')" % \
      ('Mac', 'Mac','Mac','Mac','Mac','Mac','Mac','Mac')
try:
   # 执行sql语句
   cursor.execute(sql)
   # 执行sql语句
   db.commit()
except:
   # 发生错误时回滚
   db.rollback()

# 关闭数据库连接
db.close()