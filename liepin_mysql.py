# -*- coding: UTF-8 -*-
import pymysql

def dbInsert(value):
   # 打开数据库连接
   db = pymysql.connect("134.175.0.45", "root", "583821", "jobCrawer")

   # 使用cursor()方法获取操作游标
   cursor = db.cursor()

   # SQL 插入语句
   sql = "INSERT INTO liepin(positionName,city,companyName,salary,workYear,education,createTime,welfare,searchKey)  VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s)"

         #(positionName,city,companyName,salary,workYear,education,createTime,welfare,searchKey)
   try:
      cursor.execute(sql,value)
      db.commit()
   except Exception as err:
      # 发生错误时回滚
      print(err)
      db.rollback()

   # 关闭数据库连接
   db.close()