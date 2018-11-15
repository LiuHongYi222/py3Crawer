# -*- coding: UTF-8 -*-
import pymysql

def dbInsert(db,value):
   # 打开数据库连接
   #db = pymysql.connect("134.175.0.45", "root", "583821", "jobCrawer")

   # 使用cursor()方法获取操作游标
   cursor = db.cursor()

   # SQL 插入语句
   sql = "INSERT INTO liepin(positionName,city,companyName,salary,workYear,education," \
         "createTime,welfare,searchKey,jobType,area,getTime,detail,positionId)  " \
            "VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
   file = r'liePinLog.txt'
   f= open(file, 'a+')

   try:
      cursor.execute(sql,value)
      print('Insert one record ('+ value[13]+value[0] +') to liepin table at time:' + value[11])
      f.write('Insert one record ('+ value[13]+value[0] +') to liepin table at time:' + value[11] +'\n')

   except Exception as err:
      # 发生错误时回滚
      print(type(err),err)
      f.write(repr(err))
      f.write('at time:' + value[11])
      f.write('\n')
      db.rollback()

   f.close()
      # 关闭数据库连接
   # db.commit()
   # db.close()