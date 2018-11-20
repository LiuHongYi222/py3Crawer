#猎聘网，每一个page有40条记录，page最大值100
#第一级简介信息爬虫无需设置反爬虫，
# 但是第二级链接详细信息有反爬机制，目前采取睡眠1-2秒的方式，如果爬虫过快偶尔会出现timeout的异常，日志记录异常
import requests
from bs4 import BeautifulSoup
import  pymysql
import  liepin_mysql as DB
import  time
import  threading
import  printStandard as pr

from datetime import datetime


lock = threading.Lock()
def cityToNumber(cityName):

    # 一线城市
    if (cityName == '北京'):
        return '010'
    if (cityName == '上海'):
        return '020'
    if (cityName == '广州'):
        return '050020'
    if (cityName == '深圳'):
        return '050090'

    # 非一线城市
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

def requestsArgu(cityName,searchKey):

    my_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    baseUrl1 = 'https://www.liepin.com/zhaopin/?pubTime=&ckid=47859fa68f1086ee&fromSearchBtn=2&compkind' \
                '=&isAnalysis=&init=-1&searchType=1&dqs='

    baseUrl2 = '&industryType=&jobKind=&sortFlag=15&degradeFlag=0&industries=&salary=&compscale=' \
                '&clean_condition=&key= '

    baseUrl3 = '&headckid=1044990bb2f3db5a&d_pageSize=40&siTag=k_cloHQj' \
                '_hyIn0SLM9IfRg~-nQsjvAMdjst7vnBI-6VZQ&d_headId=5e971b35915f191cc89e5701fbbf4993&d_ckId' \
                '=4d04b8eb57216c472f52e366d9a3d8ad&d_sfrom=search_prime&d_curPage=0&curPage='

    baseUrl = baseUrl1 + cityToNumber(cityName) \
               +baseUrl2 + searchKey  \
                +baseUrl3     #猎头招聘网的传参是城市电话代码
                                              #页码
    return  my_headers,baseUrl

def crawerLiePin(cityName,searchKey,page,db):

    my_headers,baseUrl = requestsArgu(cityName,searchKey)

    # 打开baseUrl页面，一般不会出错
    try:
        r = requests.get(baseUrl + str(page), headers=my_headers)
    except Exception as err:
        file = r'liePinLog.txt'
        f = open(file, 'a+')
        f.write('A baseUrl error :')
        f.write(repr(err))
        f.write('at time:' +  (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) )
        f.write('\n')
        f.close()
        print(err)
        return
    bs = BeautifulSoup(r.text, 'lxml')
    r.close()

    count = len(bs.select('div.sojob-item-main '))         #计数每个第一级页面有多少条工作

    positionNameBs = bs.select("div.job-info > h3 > a")    #岗位名称的HTML节点
    areaBs = bs.select(".area")                             #工作地区的HTML节点（一般是城市+区域）
    companyNameBs  = bs.select(".company-name > a")        #公司名称的HTML节点
    salaryBs  = bs.select(".text-warning")                 #薪水的HTML节点
    educationBs = bs.select(".edu")                        #学历要求的HTML节点
    welfareBs = bs.select(".temptation")                   #工作福利的HTML节点（企业招聘才有，其他三种没有）
    workYearBs = bs.select(".condition ")                  #工作年限要求的HTML节点
    createTimeBs = bs.select(".time-info > time")          #招聘的发布时间HTML节点
    jobTypeBs = (bs.select('.icon'))                       #招聘类型的HTML节点（企业，猎头,优，直 招聘等等）
    welfareFlag = 0     #其他的属性都是必有，count=40 ,但福利字段可能为空，所以不一定是40,因此此处设置flag，便于之后for循环


    for i in range(0,count):                  #pageSize = 40,该for表示一个页码

        rawDetailHtml = positionNameBs[i].get('href')
        if (not 'https' in rawDetailHtml):
            detailUrl = ('https://www.liepin.com' + rawDetailHtml )
        else :
            detailUrl = rawDetailHtml

        # 此处sleep不用太长
        time.sleep(0.1)

        # 打开detailurl页面，一般不会出错
        # 对详细信息链接再进行一次爬虫   抓取岗位具体信息（包括职位要求，岗位职责等等）
        try:
            rr = requests.get(str(detailUrl), headers=my_headers)
        except Exception as err:
            file = r'liePinLog.txt'
            f = open(file, 'a+')
            f.write('A detailUrl error :')
            f.write(repr(err))
            f.write('at time:' + (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            f.write('\n')
            f.close()
            print(err)
            continue
        bsDetail = BeautifulSoup(rr.text, 'lxml')
        rr.close()
        #
        # if  ( ('岗位职责' in  bsDetail.select("div.content-word ")[0].text
        #     or  '工作职责' in  bsDetail.select("div.content-word ")[0].text)  and
        #     ('任职要求' in  bsDetail.select("div.content-word ")[0].text )   ) :
        #
        #     return

        # 以下字段非直类型，（企、猎、优等三种类型）：  不固定格式，一般包括：岗位描述岗位的要求任职要求等等
        if( not  '/cjob' in detailUrl):
            detail = (
                (bsDetail.select("div.content-word "))[0].text.replace('<br/>', '\n').replace('：',': \n')
                .replace('1.','\n1.').replace('2.','\n2.').replace('3.','\n3.').replace('4.','\n4.')
                .replace('1、', '\n1、').replace('2、', '\n2、').replace('3、', '\n3、').replace('4、', '\n4、')
                .replace('岗位','\n岗位').replace('任职要求','\n任职要求').replace('工作职责','\n工作职责')
                )


        # 以下字段是职位描述（直 cjob 类型）：              不固定格式，一般包括：岗位描述岗位的要求任职要求等等
        else:
            detail = (
                (bsDetail.select("div.job-info-content "))[0].text.replace('<br/>','\n').replace('：',': \n')
                    .replace('1.', '\n1.').replace('2.', '\n2.').replace('3.', '\n3.').replace('4.', '\n4.')
                    .replace('1、', '\n1、').replace('2、', '\n2、').replace('3、', '\n3、').replace('4、', '\n4、')
                    .replace('岗位', '\n岗位').replace('任职要求', '\n任职要求').replace('工作职责', '\n工作职责')
            )

        getTime = (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        positionId = detailUrl[23:].replace('.shtml', '/').replace('\n','').replace('\r','')
        workYear        =    workYearBs[i].text.split('\n')[4]
        area            =    areaBs[i].text
        companyName     =    companyNameBs[i].text
        salary          =    salaryBs[i].text
        education       =    educationBs[i].text
        createTime      =    createTimeBs[i].get('title')
        jobType         =    jobTypeBs[i].get('title')
        positionName    =    positionNameBs[i].text.replace('	','').replace('\n','').\
                                    replace(' ','').replace('\r\n','').replace('\r','')
        welfare = ''    #猎聘网站四个类型招聘职位中，目前只发现企业这一类型招聘具有福利
        if ('企业') in jobTypeBs[i].get('title')  :

            welfare = (welfareBs[welfareFlag].text.replace('\n', ',')[1:-1])
            if(welfareFlag < len(welfareBs)-1):
                welfareFlag += 1

        # 利用list存储一条mysql记录，包括以下字段
        value = [positionName, cityName, companyName, salary, workYear, education,
                 createTime, welfare, searchKey,jobType,area,getTime,detail,positionId]


        pr.printTable(positionName,detail)
        # print(value)
        # with lock:
        #     DB.dbInsert(db,value)     #插入数据库
        #     db.commit()       #提交insert，之后关闭数据库，
        time.sleep(0.1)

    # time.sleep(1)

if __name__ == '__main__':

    # 该range语句表示抓取的page范围, 猎聘网中每page有40条工作职位，其page的最大值为100
    # page0代表第一页，以此类推
    #  c%23是c#的关键词,c%2B%2B是C++的关键词



    positionName = ['java',
                    'python',
                    'c%23',
                    'c%2B%2B',
                    'php',
                    '数据分析',
                    'AI',
                    '深度学习',
                    'C',
                    '爬虫',
                    '研发',
                    '算法'
                    ]
    positionNameLen = len(positionName)
    cityName =     ['北京',
                    '上海',
                    '厦门',
                    '广州',
                    '深圳',
                    '杭州',
                    '成都',
                    '南京'
                    ]
    cityNameLen = len(cityName)

    db = pymysql.connect("134.175.0.45", "lhy", "628628", "jobCrawer")

    thread = []
    now = datetime.now()  # 开始计时
    print(now)
    for page in range(0, 2):
        t = threading.Thread(target = crawerLiePin,
                             args = ('北京', '标准化工程师',page,db,))
        thread.append(t)

    threadingNum = 1
    for i in range(0, threadingNum):
        thread[i].start()

    for i in range(0, threadingNum):
        thread[i].join()

    end = datetime.now()    #结束计时
    print(end)
    print("程序耗时： " + str(end-now))

    db.close()
