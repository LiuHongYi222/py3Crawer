
#利用requests库的post请求访问拉勾网，返回j---son，直接在j不急不急son查找字段
#间隔必须在 20 秒以上

#每一个page有15条记录
#设置停顿至少20，爬虫限制较为严格

import  pymysql
import  lagou_mysql as DB
import requests
from time import sleep
import random
import  json

#两个关键词和猎聘网一样  保持一致性
# cityName='北京'
# searchKey='爬虫'

def argu(cityName):

    header = {
        'Host': 'www.lagou.com',
        #'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        #'Referer': 'https://www.lagou.com/jobs/list_Python?labelWords=&fromSearch=true&suginput=',
         'Referer': 'https://www.lagou.com/jobs/list_java?px=new&city=%E5%8C%97%E4%BA%AC',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Anit-Forge-Token': 'None',
        'X-Anit-Forge-Code': '0',
        'Content-Length': '24',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
        }
    url = 'https://www.lagou.com/jobs/positionAjax.json?px=new&city='+cityName+'&needAddtionalResult=false'
       #  https://www.lagou.com/jobs/positionAjax.json?px=default&city=        &needAddtionalResult=false
    return  url,header

# for num in range(1,2):
def crawerLaGou(cityName,searchKey,page =0 ):
    flag='true'
    if page!=1:
           flag='false'
    form = {'first':flag,
            'kd':searchKey,
            'pn':str(page)}

    url,header = argu(cityName)
    html=requests.post(url=url,data=form,headers=header)   #post请求
    result=html.json()
    # print(json.dumps(result,ensure_ascii=False,indent=4))      #缩进化输出json文件，便于查看需要查找的元素位置
    print('--------------------'+str(page)+'-------------------------')
    data=result['content']['positionResult']['result']
    # totalCount = result['content']['positionResult']['totalCount']

    db = pymysql.connect("134.175.0.45", "root", "583821", "jobCrawer")
    #data的type为list         len为15  每一个page有15条记录
    #data[0] 元素为dict
    for datas in data:

        workYear = datas['workYear']
        area = datas['district']
        positionName = datas['positionName']
        companyName = datas['companyFullName']
        salary = datas['salary']
        education = datas['education']
        createTime =  (datas['createTime'][:10] +' '+ datas['formatCreateTime'][0:-2])
        city  = cityName
        positionId = datas['positionId']
        welfare = ''
        for i in datas['companyLabelList']:
            welfare += i
            welfare += ','
        if(len(welfare) >=1 ):
           welfare = (welfare[0:-1])

        value = [workYear,area,positionName,companyName,salary,
                 education,createTime,welfare,city,searchKey,positionId]
        # print(value)
        DB.dbInsert(db,value)
    db.commit()
    db.close()
    print('..... sleeping .....')
    sleep(random.randint(22,25))



if __name__ == '__main__':

    positionName = ['java',
                    'python',
                    'c#',
                    'c++',
                    'php',
                    '数据库',
                    '数据挖掘'
                    ]
    positionNameLen = len(positionName)
    cityName =     ['北京',
                    '上海',
                    '厦门',
                    '广州',
                    '深圳',
                    '杭州',
                    '成都'
                    ]
    cityNameLen = len(cityName)

    for i in range(1,10):                  #不能从0开始，猎聘可以，拉勾不行
        #crawerLiePin('北京', '产品经理',i )
        crawerLaGou('北京', '前端', i )
        # sleep
        # crawerlagou('北京', '爬虫', i )


    # db.close()
