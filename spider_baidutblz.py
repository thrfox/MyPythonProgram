#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
结构
<cc>
    <div>匹配项（去除img）</div>
    <br>
</cc>
'''
# 测试url = r'https://tieba.baidu.com/p/5244165082?see_lz=1'
import urllib.request
import re
import itertools
#logging用于Debug，可以控制不同的输入等级level=logging.DEBUG\INFO\WARNING\ERROR
import logging
logging.basicConfig(level=logging.DEBUG)

class My_TagExchange_Tool():
    #空白与换行标签匹配
    space2NoneRex = re.compile(r'(\t| |\n)')
    #非换行标签匹配
    img2NoneRex = re.compile(r'<img.*?>|<div.*?>|<a.*?>|</a>|<span.*?>|</span>|<strong>|</strong>')
    #换行标签匹配
    lineTag2Line = re.compile(r'<br>|<br/>|<hr>|<hr/>|<td>|<p.*?>')
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
    def __init__(self,url_or_id,getAuthor):
        '''
        Args:
            self.url:需解析的url
            self.datas:用于存储匹配的数据
            self.myTool:创建工具类，用于替换无用字符
        '''
        #实现传入帖子编号而不传入url预留
        #self.url = url.format()
        self.url = self.url_format(url_or_id)
        self.datas = []
        #是否爬取作者数据
        # 如果url为只看楼主，则默认不每行添加作者，可将authorCtrlller设为1强制打开
        if re.search('see_lz', self.url):
            self.getAuthor = False
        self.getAuthor = getAuthor

        self.myTool = My_TagExchange_Tool()
        print('爬虫启动中...')

    def url_format(self,url):
        logging.info(url)
        cur_url = r'https://tieba.baidu.com/p/{id}?see_lz=1'
        allPage = re.compile(r'.*?tieba.baidu.com/p/\d+?')
        lzPage = re.compile(r'.*?tieba.baidu.com/p/\d+?\?see_lz=1')
        if str.isdigit(url):
            cur_url = cur_url.format(id=url)
        elif re.search(allPage,url):
            cur_url = url
        elif re.search(lzPage,url):
            cur_url = url
        else:
            print('请输入正确的贴吧链接或帖子id')
            exit()
        logging.info(cur_url)
        return cur_url

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
        try:
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
            return final_title,titleRex
        except AttributeError as e:
            print('请检查url是否正确，无法解析此url')
            exit()
        #多返回值

    #查找页码数
    def serach_pages(self,HTML_page):
        '''
        Args:
            pages:总页数匹配，后有.group(1)
        Returns:
            int(pages):返回一个int类型的页码，用于方法调用
        '''
        pages = 0
        pages = re.search(r'class="red">(\d+?)</span>', HTML_page).group(1)
        if pages != 0:
            print("获取页数成功，总页数为"+pages+"页")
        return int(pages)

    #获取楼层数与发表日期和作者
    def find_authorNfloorNdate(self,HTML_page):
        #控制如果启动，则爬取楼层与作者信息
        author = re.findall(r'<img username="(.*?)"',HTML_page)
        floor = re.findall(r'class="tail-info">(\d+?\S)</span>',HTML_page)
        date = re.findall(r'class="tail-info">([\d\- :]{12,16})</span>',HTML_page)
        #循环取出作者，楼层，日期，拼接成str装入list
        reS = []
        n = len(author)
        i = 0
        while(n>0):
            n = n - 1
            #拼接成str
            basic = '作者@' + author[i] + ';' + floor[i] + ';日期' +date[i]
            i = i + 1
            reS.append(basic)

        #返回一个list
        return reS

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
            f.writelines(title[0])
            for data in datas:
                f.writelines(data)

    #获取需爬取的数据
    def deal_datas(self,HTML_page):
        #正则匹配page的LZ帖子内容，list
        Floor = re.compile(r'<div id="post_content.*?>(.*?)</div>')
        #bubbleFloor = r'<div class="post_bubble_middle.*?>(.*?)</div>'
        source_date = re.findall(Floor, HTML_page)
        #将list内的匹配好的数据取出，并进行正则替换，并添加到最终数据组self.datas
        #插入正文
        ok_datas = []
        for item in source_date:
            deal_date = self.myTool.Replace_Char(item)
            ok_datas.append('\n'+deal_date+'\n')
        return ok_datas


    def get_all_page(self,url,endPage,getAuthor):
        '''
        Args:
            cur_url:将每个传入的url加上页码数
        '''
        #判断page是否为只看楼主
        if re.search(r'see_lz',url):
            url = url + '&pn='
        else:
            url = url + '?pn='

        #传入页数参数
        for i in range(1,endPage+1):
            cur_url = url + str(i)
            logging.info(cur_url)
            #HTML_page = urllib.request.urlopen(url).read().decode('utf-8')
            HTML_page = self.open_url(cur_url)
            if HTML_page != None:
                print('第%d页获取成功'% i )
                contents = self.deal_datas(HTML_page)
                for i in range(len(contents)):
                    self.datas.append(contents[i])
                    #控制器==True，爬取作者
                    if getAuthor==True:
                        authors = self.find_authorNfloorNdate(HTML_page)
                        self.datas.append(authors[i]+'\n')

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
        self.get_all_page(self.url, endPages,self.getAuthor)
        if self.datas != []:
            '''以下代码Debug'''
            logging.info(self.datas)
            self.sava_txt(title,self.datas)


bdurl = r'https://tieba.baidu.com/p/5244165082'
bdtbSpider = Spider_BaiduTieBaOnlyLZ(bdurl,getAuthor=True)
bdtbSpider.start_spider()
