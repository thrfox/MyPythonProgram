import wx
'''
启动类GUI
    创建GUI界面
'''
import os
import random
class GUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title,size=(300,-1))
        self.GUI()
        self.Show(show=True)
        
    def OnClick(self,e): #Bind()里的Event需要两个参数，所以需要传入e
        dlg = wx.MessageDialog(self,"文本框内内容","关于编辑器标题") #一个文本提示框，wx.OK是wx自带的ID
        dlg.ShowModal() #Show这个dlg,Model代表在该show结束之前无法对原程序做其他操作
        dlg.Destroy() #最后close()dlg，避免占用资源
    
    def OnExit(self,e):
        self.Close(True)
    
    def OnOpen(self,e):
        self.dirname = ''
        dlg = wx.FileDialog(self,"选择一个文件",self.dirname,"","*.txt") #FileDialog可以打开程序
        if dlg.ShowModal() == wx.ID_OK: #用户点击OK则打开文件
            self.filename = dlg.GetFilename() #dlg打开文件后获得的文件名赋值给filename，提供给with open
            self.dirname = dlg.GetDirectory() #文件路径\文件夹
            with open(os.path.join(self.dirname,self.filename),'r') as f:
                self.control.SetValue(f.read())
            dlg.Destroy() #关闭资源
            
    def OnStartButton(self,e):    
        TextValue = self.control.GetValue().replace(' ','') #replace去空格
        L = TextValue.split('\n')
        choice = random.choice(L)
        if choice != '':
            wx.MessageBox(choice,"结果",wx.OK)
        else:
            wx.MessageBox("请输入数据","结果")
    
    def OnResetButton(self,e):
        self.control.SetValue('')
    
    def create_menuBar(self):
        #创建菜单，并在菜单中创建选项
        menu = wx.Menu()
        menuItem_Open = menu.Append(wx.ID_OPEN, "&打开文件"," 打开一个文本")
        menuItem_About = menu.Append(wx.ID_ABOUT, "&关于"," 程序简介")
        menu.AppendSeparator()
        menuItem_Exit = menu.Append(wx.ID_EXIT,"&退出"," 结束程序")
        
        #创建菜单栏
        menuBar = wx.MenuBar()
        menuBar.Append(menu, '菜单名') #绑定menu到菜单栏menuBar
        self.SetMenuBar(menuBar) #绑定menuBar到程序GUI
#         self.Show() #创建GUI Frame
        
        
    
    #用Bind()绑定事件（点击Button，文本输入时，鼠标移动到时等等）
        #绑定一个单击的事件到‘关于’
        self.Bind(wx.EVT_MENU, self.OnClick, menuItem_About) 
        self.Bind(wx.EVT_MENU, self.OnExit, menuItem_Exit)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuItem_Open)
        

    def create_button(self):
        self.control = wx.TextCtrl(self,style=wx.TE_MULTILINE) #文本输入框，style可多行输入
        
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL) #Button框型容器
        self.buttons = []
        
        Button_Start = wx.Button(self,-1,"开始")
        Button_Reset = wx.Button(self,-1,"重置")
        self.buttons.append(Button_Start)
        self.buttons.append(Button_Reset)
        self.sizer2.Add(self.buttons[0], 1, wx.EXPAND) #在Button容器中装入Button
        self.sizer2.Add(self.buttons[1], 1, wx.EXPAND) #在Button容器中装入Button
        
        self.sizer = wx.BoxSizer(wx.VERTICAL) #总容器，装Button容器和TextCtrl
        self.sizer.Add(self.control, 1, wx.EXPAND)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)
        
        self.SetSizer(self.sizer, deleteOld=True)
        self.SetAutoLayout(1)
#         self.sizer.Fit(self) 使界面自适应
        
        self.Bind(wx.EVT_BUTTON,self.OnStartButton,Button_Start)
        self.Bind(wx.EVT_BUTTON,self.OnResetButton,Button_Reset)
        
    def GUI(self):
        self.CreateStatusBar()
        self.create_menuBar()
        self.create_button()
        
        
if __name__ == '__main__':
    myapp = wx.App()
    frame = GUI(None,'程序名称')
    myapp.MainLoop()
