# -*- coding: UTF-8 -*-
# 拉勾网的sql
import pymysql

table = 'lagou'
def dbInsert(db,value):
   # 打开数据库连接
   #db = pymysql.connect("134.175.0.45", "root", "583821", "jobCrawer")

   # 使用cursor()方法获取操作游标
   cursor = db.cursor()

   # SQL 插入语句
   sql = "INSERT INTO lagou(workYear,area,positionName,companyName,salary,education,createTime,welfare,city,searchKey,positionId) " \
            "VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

   try:
      cursor.execute(sql,value)
      print('successfully inset one record to ' + table  +'!' )
      # db.commit()
   except Exception as err:
      # 发生错误时回滚
      print(err)
      db.rollback()

   # 关闭数据库连接
   # db.commit()
   # db.close()