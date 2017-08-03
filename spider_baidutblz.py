#!/usr/bin/env python
# -*- coding:utf-8 -*-
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
        '''
        Args:
            self.url:需解析的url
            self.datas:用于存储匹配的数据
            self.myTool:创建工具类，用于替换无用字符
        '''
        #实现传入帖子编号而不传入url预留
        #self.url = url.format()
        self.url = url
        self.datas = []
        self.myTool = My_TagExchange_Tool()
        print('爬虫启动中...')
    def open_url(self,cur_url):
        '''
        Args:
            cur_url:传入url连接
        Returns:
            myPage:返回HTML页面
        '''
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
    def find_title(self,HTML_page):
        '''
        Args:
            titleRex:标题名称
            tiebaRex:贴吧名称
        Returns:
            final_title:替换过字符后用于写入文档的标题
            titleRex:帖子标题，用于方法调用
        '''
        #若连接失败，则返回None
        if isinstance(HTML_page, str)==False:
            return None 
        titleRex = re.search(r'(<h1.*?>|<h3.*?>)(.*?)(</h1>|</h3>)', HTML_page).group(2)
        tiebaRex = re.search(r'<a class="card_title_fname".*?>(.*?)</a>', HTML_page).group(1)
        final_title = None
        logging.info(titleRex)
        logging.info(tiebaRex)
        if titleRex != [] and tiebaRex != []:
            #Rex为list内包含一个tuple
            title = '来自百度贴吧:\"'+tiebaRex+'\" \n标题:\"'+titleRex+'\"'
            #对标题进行处理
            final_title = self.myTool.Replace_Char(title)
        #多返回值
        return final_title,titleRex
    #查找页码数
    def serach_pages(self,HTML_page):
        '''
        Args:
            pages:总页数匹配，后有.group(1)
        Returns:
            int(pages):返回一个int类型的页码，用于方法调用
        '''
        pages = re.search(r'class="red">(\d+?)</span>', HTML_page).group(1)
        logging.info('s_pages,总页码数-'+pages)
        return int(pages)
    #获取楼层数与发表日期和作者
    def find_authorNfloorNdate(self,HTML_page):
        author = '@' + 'getName'
        floor = '这是第%d楼' + 'getFloor'
        date = '日期是' + 'getDate'
        reS = author + floor + date
        #返回一个list
        return 'floors方法'
        pass
    #存储数据为txt
    def sava_txt(self,title,datas):
        '''
        Args:
            datas:爬取的数据 List
            title:多返回值
                [0]:添加到第一行的标题数据
                [1]:帖子标题
        '''
        file = '百度贴吧爬虫-'+title[1]+'.txt'
        with open(file,'w',encoding='utf-8') as f:
            f.writelines(title[0]+'\n')
            for data in datas:
                f.writelines(data)
    
    #获取需爬取的数据
    def deal_datas(self,HTML_page):
        #正则匹配page的LZ帖子内容，list
        source_date = re.findall(r'<div id="post_content.*?>(.*?)</div>', HTML_page)
        #将list内的匹配好的数据取出，并进行正则替换，并添加到最终数据组self.datas
        floors = self.find_authorNfloorNdate(HTML_page)
        floor = 0
        #插入正文
        for item in source_date:
            deal_date = self.myTool.Replace_Char(item)
            self.datas.append(deal_date)
            #插入楼层数据
            self.datas.append('\n'+str(floor)+'\n')
            floor = floor + 1
        
    def get_all_page(self,url,endPage):
        '''
        Args:
            cur_url:将每个传入的url加上页码数
        '''
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
        '''
            Args:
                HTML_page：原始页面，获取该帖子的标题，与总页数
                title:标题，有两个返回值，[0]为写入文本开头,[1]用于调用
                endPages:总页数，用于方法调用
        '''
        HTML_page = self.open_url(self.url)
        title = self.find_title(HTML_page)
        endPages = self.serach_pages(HTML_page)
        
        self.get_all_page(self.url, endPages)
        if self.datas != []:
            '''以下代码Debug'''
            logging.info(self.datas)
            self.sava_txt(title,self.datas)
            

bdurl = r'https://tieba.baidu.com/p/3698425746?see_lz=1'
bdtbSpider = Spider_BaiduTieBaOnlyLZ(bdurl)
bdtbSpider.start_spider()

