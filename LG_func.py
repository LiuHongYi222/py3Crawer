#拉勾网的爬虫源码， 18-10-17可用
#利用requests库的post请求访问拉勾网，返回json，直接在json查找字段
#间隔必须在20秒以上

#每一个page有15条记录
#设置停顿至少20，爬虫限制较为严格

import requests
from time import sleep
import random
import  json

#两个关键词和猎聘网一样  保持一致性
cityName='北京'
searchKey='java'


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

for num in range(300,302):

    print('-----------')
    #取随机延迟,防止IP被封


    flag='true'
    if num!=1:
           flag='false'
    form = {'first':flag,
            'kd':searchKey,
            'pn':str(num)}
    html=requests.post(url=url,data=form,headers=header)   #post请求
    result=html.json()
    #print(json.dumps(result,ensure_ascii=False,indent=4))      #缩进化输出json文件，便于查看需要查找的元素位置
    print('--------------------'+str(num)+'-------------------------')
    data=result['content']['positionResult']['result']
    totalCount = result['content']['positionResult']['totalCount']
    print(totalCount)

    #data的type为list         len为15  每一个page有15条记录
    #data[0] 元素为dict
    for datas in data:

        # print(datas['workYear'])
        print(datas['companyFullName'])
        print(datas['district'])
        print(datas['createTime'][:10])
        print(str((datas['positionAdvantage'])))
        print(datas['positionId'])
        print(datas['positionName'])

        print('*****************************************************************************')



    # workYear = workYear
    # area = district
    # positionName = positionName
    # companyName = companyFullName
    # salary = salary
    # education = education
    # createTime = createTime[:10]
    # welfare   = companyLabelList
    # cityName =
    # serachKey =

    # positionId = positionId




    #sleep(random.randint(22,25))
