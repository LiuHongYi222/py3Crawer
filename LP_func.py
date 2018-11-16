#猎聘网，每一个page有40条记录
#第一级简介信息爬虫无需设置反爬虫，但是第二级链接详细信息有反爬机制，目前没找到方法
import requests
from bs4 import BeautifulSoup
import  pymysql
import  liepin_mysql as DB
import  time

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

    proxies = {
        "http": "http://134.175.0.45:2765",
        "https": "http://134.175.0.45:2765",
    }

    my_headers,base_url = argu(cityName,searchKey)
    try:
        r = requests.get(base_url + str(page), headers=my_headers)
    except Exception as err:
        file = r'liePinLog.txt'
        f = open(file, 'a+')
        f.write('A base_url error :')
        f.write(repr(err))
        f.write('at time:' +  (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) )
        f.write('\n')
        f.close()
        print(err)
        return
    bs = BeautifulSoup(r.text, 'lxml')
    r.close()

    positionNameBs = bs.select("div.job-info > h3 > a")    #岗位名称的HTML节点
    areaBs = bs.select(".area")                            #工作地区的HTML节点（一般是城市+区域）
    companyNameBs  = bs.select(".company-name > a")        #公司名称的HTML节点
    salaryBs  = bs.select(".text-warning")                 #薪水的HTML节点
    educationBs = bs.select(".edu")                        #学历要求的HTML节点
    welfareBs = bs.select(".temptation")                   #工作福利的HTML节点（企业招聘才有，猎头没有）
    workYearBs = bs.select(".condition ")                  #工作年限要求的HTML节点
    createTimeBs = bs.select(".time-info > time")          #招聘的发布时间HTML节点
    jobTypeBs = (bs.select('.icon'))                       #招聘类型的HTML节点（企业直招，急招，猎头招聘等等）
    welfareCount = 0     #其他的属性都是必有，count=40 ,但福利字段可能为空，所以不一定是40,因此此处单独计数
    count = len(positionNameBs)

    db = pymysql.connect("134.175.0.45", "lhy", "628628", "jobCrawer")

    for i in range(0,count):                  #pageSize = 40,该for表示一个页码

        detailHtml =''
        rawDetailHtml = positionNameBs[i].get('href')
        if (not 'https' in rawDetailHtml):
            detailHtml = ('https://www.liepin.com' + rawDetailHtml )
        else :
            detailHtml = rawDetailHtml

        # 此处sleep不用太长
        time.sleep(0.1)

        # 对详细信息链接再进行一次爬虫   抓取岗位具体信息（包括职位要求，岗位职责等等）
        try:
            rr = requests.get(str(detailHtml), headers=my_headers)
        except Exception as err:
            file = r'liePinLog.txt'
            f = open(file, 'a+')
            f.write('A detailHtml error :')
            f.write(repr(err))
            f.write('at time:' + (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            f.write('\n')
            f.close()
            print(err)
            continue
        bsDetail = BeautifulSoup(rr.text, 'lxml')
        rr.close()

        # 以下字段是职位描述（企、猎、优等三种类型）：  不固定格式，一般包括：岗位描述岗位的要求任职要求等等
        if( not  '/cjob' in detailHtml):
            detail = (
                (bsDetail.select("div.content-word "))[0].text
                    .replace('	','').replace('<br/>', '').replace(' ', '').replace('\n', ''))
        # 以下字段是职位描述（直 类型）：              不固定格式，一般包括：岗位描述岗位的要求任职要求等等
        else:
            detail = (
                (bsDetail.select("div.job-info-content "))[0].text
                    .replace('	', '').replace('<br/>','').replace(' ','').replace('\n',''))

        positionId = detailHtml[23:].replace('.shtml', '/').replace('\n','').replace('\r','')
        getTime = (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        workYear        =    workYearBs[i].text.split('\n')[4]
        area            =    areaBs[i].text
        positionName    =    positionNameBs[i].text.replace('	','').replace('\n','').\
                                    replace(' ','').replace('\r\n','').replace('\r','')
        companyName     =    companyNameBs[i].text
        salary          =    salaryBs[i].text
        education       =    educationBs[i].text
        createTime      =    createTimeBs[i].get('title')
        jobType         =    jobTypeBs[i].get('title')
        welfare = ''                                    #猎聘网站中，目前只发现企业招聘具有福利
        if ('企业') in jobTypeBs[i].get('title')  :

            welfare = (welfareBs[welfareCount].text.replace('\n', ',')[1:-1])
            if(welfareCount < len(welfareBs)-1):
                welfareCount += 1

        # 利用list存储一条mysql记录，包括以下字段
        value = [positionName, cityName, companyName, salary, workYear, education,
                 createTime, welfare, searchKey,jobType,area,getTime,detail,positionId]

        DB.dbInsert(db,value)     #插入数据库

        #提交insert，之后关闭数据库，
        db.commit()
        time.sleep(0.1)
    db.close()
    # time.sleep(1)



if __name__ == '__main__':

    #  c%23是c#的关键词,c%2B%2B是C++的关键词
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

    # 该range语句表示抓取的page范围, 猎聘网中每page有40条工作职位，其页面的最大值为100
    # page0代表第一页，以此类推
    for page in range(0,10):
        crawerLiePin('北京', 'python',page )
        crawerLiePin('上海', 'java', page)
        crawerLiePin('杭州', 'c%2B%2B', page)

