'''
结构
<cc>
    <div>匹配项（去除img）</div>
    <br>
</cc>
'''
# url = r'https://tieba.baidu.com/p/2001164583?see_lz=1'
import urllib.request
import re
#logging用于Debug，可以控制不同的输入等级level=logging.DEBUG\INFO\WARNING\ERROR
import logging
logging.basicConfig(level=logging.DEBUG)

class My_TagExchange_Tool():
    #空白与换行标签匹配
    space2NoneRex = re.compile(r'(\t| |\n)')
    #图片标签匹配
    img2NoneRex = re.compile(r'<img.*?>')
    #换行标签匹配
    lineTag2Line = re.compile(r'<br>|<br/>|<hr>|<hr/>|<td>|<p.*?>|<a.*?>|</a>')
    #视频标签匹配
    #videoTag2NoneRex = re.compile(r'video')
    #特殊标签
    spec2sourceRex = [('&nbsp;',' '),('&quot;','\"'),('&amp;','&')]
    def Replace_Char(self,x):
        x = self.space2NoneRex.sub('',x)
        x = self.img2NoneRex.sub(' ',x)
        x = self.lineTag2Line.sub('\n',x)
        
        for i in self.spec2sourceRex:
            x = x.replace(i[0],i[1])
        return x
    
class Spider_BaiduTieBaOnlyLZ():
    def __init__(self,url):
        #实现传入帖子编号而不传入url预留
        #self.url = url.format()
        self.url = url
        self.datas = []
        self.myTool = My_TagExchange_Tool()
        print('爬虫启动中...')
    def open_url(self,cur_url):
        #获取页面原始信息
        #获取HTML是否载入成功
        myPage = None
        try:
            myHTML = urllib.request.urlopen(cur_url)
            myPage = myHTML.read().decode('utf-8')
        except urllib.error.URLError as e:
            #判断错误e有属性code吗
            if hasattr(e, "code"):
                print ('无法与服务器取得连接')
                print ("错误代码 : %s" % e.code)
            elif hasattr(e, "reason"):
                print ("服务器连接失败,请检查url是否正确")
                print ("结果: %s" % e.reason)
        return myPage
    #获取标题
    def find_title(self):
        pass
    #查找页码
    def serach_pages(self):
        pass
    #获取楼层数与发表日期和作者
    def find_authorNfloorNdate(self):
        author = '@' + 'getName'
        floor = '这是第%d楼' % 'getFloor'
        date = '日期是' + 'getDate'
        reS = author + floor + date
        return reS
        pass
    
    #获取需爬取的数据
    def deal_datas(self,HTML_page):
        #正则匹配page的LZ帖子内容，list
        source_date = re.findall(r'<div id="post_content.*?>(.*?)</div>', HTML_page)
        #将list内的匹配好的数据取出，并进行正则替换，并添加到最终数据组self.datas
        for item in source_date:
            deal_date = self.myTool.Replace_Char(item)
            self.datas.append(deal_date)
            
    def get_all_page(self,url,endPage):
        url = url + '&pn='
        #传入页数参数
        for i in range(1,endPage+1):
            cur_url = url + str(i)
            logging.info(cur_url)
            #HTML_page = urllib.request.urlopen(url).read().decode('utf-8')
            HTML_page = self.open_url(cur_url)
            if HTML_page != None:
                print('第%d页获取成功'% i )
                self.deal_datas(HTML_page)
    #爬虫入口启动
    def start_spider(self):
        #return: HTML原始页面，获取标题，页码
        #cur_page = self.open_url(self.url)
        self.get_all_page(self.url, 4)
        '''以下代码Debug'''
        if self.datas != []:
            logging.info(self.datas)

bdurl = r'http://tieba.baidu.com/p/4487155181?see_lz=1'
bdtbSpider = Spider_BaiduTieBaOnlyLZ(bdurl)
bdtbSpider.start_spider()

        
        
        

