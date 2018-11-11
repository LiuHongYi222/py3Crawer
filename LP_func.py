#每一个page有40条记录
#无需设置停顿，爬虫不限制
import requests
from bs4 import BeautifulSoup
import  pymysql
import  liepin_mysql as DB

def cityToNumber(cityName):

    if (cityName == '北京'):
        return '010'
    if (cityName == '上海'):
        return '020'
    if (cityName == '广州'):
        return '050020'
    if (cityName == '深圳'):
        return '050090'

    if (cityName == '杭州'):
        return '070020'
    if (cityName == '成都'):
        return '280020'

    if (cityName == '南京'):
        return '060020'
    if (cityName == '重庆'):
        return '040'
    if (cityName == '苏州'):
        return '060080'
    if (cityName == '武汉'):
        return '170020'
    if (cityName == '厦门'):
        return '090040'

def argu(cityName,searchKey):

    my_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    base_url1 = 'https://www.liepin.com/zhaopin/?pubTime=&ckid=47859fa68f1086ee&fromSearchBtn=2&compkind' \
                '=&isAnalysis=&init=-1&searchType=1&dqs='

    base_url2 = '&industryType=&jobKind=&sortFlag=15&degradeFlag=0&industries=&salary=&compscale=' \
                '&clean_condition=&key= '

    base_url3 = '&headckid=1044990bb2f3db5a&d_pageSize=40&siTag=k_cloHQj' \
                '_hyIn0SLM9IfRg~-nQsjvAMdjst7vnBI-6VZQ&d_headId=5e971b35915f191cc89e5701fbbf4993&d_ckId' \
                '=4d04b8eb57216c472f52e366d9a3d8ad&d_sfrom=search_prime&d_curPage=0&curPage='

    base_url = base_url1 + cityToNumber(cityName) \
               +base_url2 + searchKey  \
                +base_url3     #猎头招聘网的传参是城市电话代码
                                              #页码
    return  my_headers,base_url

#输入一个page   出来40个size记录
def crawerLiePin(cityName,searchKey,page = 0):

    my_headers,base_url = argu(cityName,searchKey)
    r=requests.get(base_url+str(page), headers = my_headers)
    bs = BeautifulSoup(r.text,'lxml')

    positionNameBs = bs.select("div.job-info > h3 > a")    #岗位名称的HTML节点
    areaBs = bs.select(".area")                            #工作地区的HTML节点（一般是城市+区域）
    companyNameBs  = bs.select(".company-name > a")        #公司名称的HTML节点
    salaryBs  = bs.select(".text-warning")                 #薪水的HTML节点
    educationBs = bs.select(".edu")                        #学历要求的HTML节点
    welfareBs = bs.select(".temptation")                   #工作福利的HTML节点（企业招聘才有，猎头没有）
    workYearBs = bs.select(".condition ")                  #工作年限要求的HTML节点
    createTimeBs = bs.select(".time-info > time")          #招聘的发布时间HTML节点
    jobTypeBs = (bs.select('.icon'))                       #招聘类型的HTML节点（企业直招，急招，猎头招聘等等）

    welfareCount = 0                       #其他的属性都是必有，count=40 ,但福利字段可能为空
    # print(len(welfareBs),'-------------------------------')
    count = len(positionNameBs)
    # print(count)
    db = pymysql.connect("134.175.0.45", "root", "583821", "jobCrawer")
    for i in range(0,count):                  #pageSize = 40,该for表示一个页码


        workYear        =    workYearBs[i].text.split('\n')[4]
        area            =    areaBs[i].text
        positionName    =    positionNameBs[i].text.replace('	','').replace('\n','')
        companyName     =    companyNameBs[i].text
        salary          =    salaryBs[i].text
        education       =    educationBs[i].text
        createTime      =    createTimeBs[i].get('title')
        jobType         =    jobTypeBs[i].get('title')
        welfare = ''                                    #猎聘网站中，目前只发现企业招聘具有福利
        if ('企业') in jobTypeBs[i].get('title')  :

            welfare = (welfareBs[welfareCount].text.replace('\n', ',')[1:-1])
            # print(welfareCount,welfare)
            if(welfareCount < len(welfareBs)-1):
                welfareCount += 1

        value = [positionName, cityName, companyName, salary, workYear, education, createTime, welfare, searchKey,jobType,area]
        # print(value)
        #插入数据库
        DB.dbInsert(db,value)


    #提交insert，之后关闭数据库
    db.commit()
    db.close()


if __name__ == '__main__':

    #  c%23是c#的关键词，   c%2B%2B是C++的关键词
    positionName = ['java',
                    'python',
                    'c%23',
                    'c%2B%2B',
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
    positionNameLen = len(positionName)
    for i in range(0,30):                  #该range语句表示page范围,  每page有40条工作职位
        #crawerLiePin('北京', '产品经理',i )
        crawerLiePin('上海', '前端', i )
        crawerLiePin('杭州', '爬虫', i )

    # db.close()






        #insert   前面几个 +  cityname  +searchkey （例如，北京，java）
        # print('')
        # print('**********************************************************************************')
        # print('----工作年限---')
        # print(workYear)
        # print('----地区---')
        # print(area)
        # print('-----岗位名称--')
        # print(positionName)
        # print('----公司名称---')
        # print(companyName)
        # print('-----薪水--')
        # print(salary)
        # print('----学历要求---')
        # print(education)
        # print('-----发布时间--')
        # print(createTime)
        # print('-----岗位招聘类型--')
        # print(jobType)
        # print('-----福利（可能为空）--')
        # print(welfaret)
