﻿# -*- conding: utf-8 -*-
'''
# python

- Project Name : Image File Selector (for make image Data-Set)
- Created Date : 26/Dec/2020
- Updated Date : 27/Dec/2020
- Author : Minku Koo
- E-Mail : corleone@kakao.com
- Version : 1.0.1
- Keywords : 'PyQt5', 'Python', 'image', 'viewer', 'big data', 'gui', 'selector', 'classify'
- Github URL : https://github.com/Minku-Koo/Image-Selector

# How to use?
- Select directory (Work Place)
- Classifying files on selected directory, correct or incorrect

'''

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5 import QtCore
import PyQt5
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication
import os
import PySide2
import shutil

# QPixmap에서 JPG 파일이 보여지지 않는 경우 설정(환경변수 추가)
# if jpg file cannot showed on pixmap -> try, add this code 
qt_path= os.path.dirname(PyQt5.__file__)
os.environ['QT_PLUGIN_PATH'] = os.path.join(qt_path, "Qt/plugins")

class ImageSelector(QWidget):
    def __init__(self):
        super(ImageSelector, self).__init__()
        # GUI 높이/길이
        self.HEIGHT = 800
        self.WIDTH = 700
        
        self.setFixedSize(self.WIDTH, self.HEIGHT) #높이 길이 설정
        self.dir_path = "" #작업 디렉토리 선언
        self.img_list=[] #이미지 파일 리스트
        self.file_extension = ["jpg","jpeg","png"] #작업 가능한 파일 확장자
        self.imageScrollHeight = self.HEIGHT * 0.7 #중앙 작업 박스(스크롤 영역) 높이 설정
        self.imageWindow = None # 이미지 보여주기 window 초기화
        self.fileDict = {} # key=file name value=Label Stylesheet
        self.radioSet = {} # key=file name, value=RadioButton Click Position
        self.radioGroupset={} # key=file name, value= 하나만 클릭가능한지 여부
        self.checkedRadio =0 #라디오 버튼 체크 개수
        self.color_correct = "#FAB773" #  Correct Clicked Label Color
        self.color_incorrect = "#CDC7C1"#  Incorrect Clicked Label Color
        self.fontName = "roboto"  #전체 폰트 설정
        
        self.initUI() #GUI 시작
    
    # 파라미터 전달을 위한 클릭 이벤트
    def clickable(self,widget): 
        class Filter(QObject):
            clicked = pyqtSignal()	#pyside2 사용자는 pyqtSignal() -> Signal()로 변경
            def eventFilter(self, obj, event):
                if obj == widget:
                    if event.type() == QEvent.MouseButtonRelease:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            # The developer can opt for .emit(obj) to get the object within the slot.
                            return True
                            
                return False
        
        filter = Filter(widget)
        widget.installEventFilter(filter)
        return filter.clicked
   
    # 라벨(파일 이름) 클릭 시, 이미지 팝업창 생성
    def showImagePopUp(self, path): #Parameter: Image Path<String> 
        if self.imageWindow is not None: # 기존에 켜져있는 경우
            self.imageWindow =None #종료
            
        location =self.pos() #현재 GUI 위치 Now GUI Position
        imagePath = self.dir_path+"/"+path #클릭 이미지 경로 Clicked Image Path
        if self.imageWindow is None:
            # 이미지 팝업 윈도우 새로 열기 Image Pop Up Window New Open
            # Parameter: image path<String>, GUI Width<int>, GUI Location X Value<int>, GUI Location Y Value<int>
            self.imageWindow = ImageShowWindow(imagePath, self.WIDTH, location.x(), location.y())
            
        self.imageWindow.show() #이미지 팝업 보여주기 
        return 0
        
    # RadioButton 전체 Correct로 선택 
    def AllRadioSelectCorrect(self):
        for file in self.img_list: # 모든 이미지 파일 이름 All ImageFile Name
            self.radioSet[file][0].setChecked(True) #RadioButton Selec just one 라디오 버튼 하나만 선택 가능
            # Correct 선택한 모든 Label 색상 변경
            self.fileDict[file].setStyleSheet("background-color:"+self.color_correct)
            
        self.checkedRadio = len(self.img_list) # Checked RadioButton 개수 == 전체 이미지파일 개수
        self.SelectCountText=str(self.checkedRadio)+" Select"
        self.SelectBox.setText(self.SelectCountText) #Label Text Change, Count
        self.progressPercent.setText("100 %..") #Label Text Change, Percent
        return 0
    
    # RadioButton 전체 Incorrect 선택
    def AllRadioSelectIncorrect(self):
        for file in self.img_list: # 모든 이미지 파일 이름 All ImageFile Name
            self.radioSet[file][1].setChecked(True) #RadioButton Selec just one 라디오 버튼 하나만 선택 가능
            # Incorrect 선택한 모든 Label 색상 변경
            self.fileDict[file].setStyleSheet("background-color:"+self.color_incorrect)
            
        self.checkedRadio = len(self.img_list) # Checked RadioButton 개수 == 전체 이미지파일 개수
        self.SelectCountText=str(self.checkedRadio)+" Select"
        self.SelectBox.setText(self.SelectCountText) #Label Text Change, Count
        self.progressPercent.setText("100 %..") #Label Text Change, Percent
        return 0
    
    # 전체 Radio Button Reset
    def AllResetFunc(self):
        for file in self.img_list: # 모든 이미지 파일 이름 All ImageFile Name
            # RadioButton 중복 선택 가능으로 설정
            self.radioGroupset[file].setExclusive(False)
            # RadioButton 모두 선택 해제
            self.radioSet[file][0].setChecked(False)
            self.radioSet[file][1].setChecked(False)
            #RadioButton Selec just one 라디오 버튼 하나만 선택 가능으로 설정
            self.radioGroupset[file].setExclusive(True)
            self.fileDict[file].setStyleSheet("")
            
        self.checkedRadio = 0 # Checked RadioButton 개수 == 0
        self.SelectCountText="0 Select"
        self.SelectBox.setText(self.SelectCountText) #Label Text Change, Count
        self.progressPercent.setText("0 %..") #Label Text Change, Percent
        return 0
    
    # Checked RadioButton개수 파악 및 Background Color 설정
    def CountRadioCheck(self):
        count =0 # Checked Count 초기화
        for file in self.img_list: # 모든 이미지 파일 이름 All ImageFile Name
            backColor = "background-color:" 
            
            if self.radioSet[file][0].isChecked() : #Checked Correct Button
                count+=1 # 개수 증가
                backColor+=self.color_correct # Correct Color 설정
            elif self.radioSet[file][1].isChecked(): #Checked Incorrect Button
                count+=1 # 개수 증가
                backColor+=self.color_incorrect # Incorrect Color 설정
            self.fileDict[file].setStyleSheet(backColor) #해당 Color로 배경색 변경
            
        self.checkedRadio = count #Checked RadioButton 개수 설정
        return count
    
    # Just click RadioButton 그냥 라디오 버튼 클릭 / RadioButton 클릭할 때마다 실행
    def justClickedRadio(self):
        self.CountRadioCheck() #라디오 버튼 개수 파악 + 배경색 설정
        self.SelectCountText = str(self.checkedRadio)+" Select"
        self.SelectBox.setText(self.SelectCountText) # Clicked  RadioButton개수 설정
        percent = int(self.checkedRadio/ len(self.img_list)*100) # Clicked  RadioButton Percent 계산
        self.progressPercent.setText(str(percent)+" %..")# Clicked  RadioButton 진행률 설정
        return 0
    
    # RadioButton Unclicked 경우 판단
    def uncheckRadio(self):
        for file in self.img_list: # 모든 이미지 파일 Label
            if self.radioSet[file][0].isChecked() or self.radioSet[file][1].isChecked(): pass
            else: return False # 하나라도 클릭 안 된 경우
        return True # 모두 클릭 완료한 경우
    
    #작업 완료 Clicked
    def doneWork(self):
        correct, incorrect = [],[] # correct, incorrect 이미지 파일 리스트 초기화
        move =True # 파일 이동 여부
        
        if self.uncheckRadio(): #모두 체크된 경우 All Checked
            for file in self.img_list:
                if self.radioSet[file][0].isChecked() : correct.append(file) # Correct List Append
                else: incorrect.append(file) # Incorrect List Append
                
        else: #RadioButton 하나라도 클릭 안 된 경우
            # message box 따로 설정해주어 Button text 변경
            buttonReply = QMessageBox()
            buttonReply.setIcon(QMessageBox.Question)
            buttonReply.setWindowTitle('Warning!!')
            buttonReply.setText('Unclassified file exist')
            buttonReply.setStandardButtons(QMessageBox.Yes|QMessageBox.Reset|QMessageBox.Save)#|QMessageBox.No)
            button1 = buttonReply.button(QMessageBox.Yes)
            button1.setText('Unclassified file to Correct')
            button2 = buttonReply.button(QMessageBox.Reset)
            button2.setText('Back to WorkSpace')
            button3 = buttonReply.button(QMessageBox.Save)
            button3.setText('Unclassified file to Inorrect')
            buttonReply.exec_()
            
            if buttonReply.clickedButton() == button3: #모두 Incorrect
                for file in self.img_list:
                    # correct
                    if self.radioSet[file][0].isChecked() : correct.append(file)
                    #incorrect
                    elif self.radioSet[file][1].isChecked() :incorrect.append(file)
                    #아무것도 체크 안됨
                    else:incorrect.append(file) # Incorrect에 추가
                    
            elif buttonReply.clickedButton() == button1: #모두 Correct  
                for file in self.img_list:
                    # correct
                    if self.radioSet[file][0].isChecked() : correct.append(file)
                    #incorrect
                    elif self.radioSet[file][1].isChecked() :incorrect.append(file)
                    #아무것도 체크 안됨
                    else: correct.append(file) # Correct에 추가
                
            elif buttonReply.clickedButton() == button2:# 작업으로 되돌아가기
                move = False # 파일 이동 안함
            
        if move: # 작업 되돌아가기 아닌 경우
            # 파일 이동
            self.moveImageFile(correct, incorrect)
            # New MessageBox Open
            nextStep = QMessageBox.question(self, 'Warning!!', "Keep Working?", QMessageBox.Yes | QMessageBox.No)
            
            # Keep Working
            if nextStep== QMessageBox.Yes: self.changeDirFunc()
            elif nextStep== QMessageBox.No: # Stop Working
                print("Program Close..\nGoodBye~")
                self.close() # GUI Close
        return 0
    
    # 파라미터 전달 받은 레이아웃 내용 모두 삭제 Clear Layout
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        return 0
                    
    # 선택한 디렉토리 모든 이미지 파일을 표시  Show All ImageFile in Selected Directory
    # Parameter: 이미지 파일 보여질 레이아웃  Showed Image File Layout<QLayout> 
    def addFileNameLayout(self, centerBox): 
        self.clearLayout(centerBox) # Clear Layout
        self.fileDict = {} # File Dictionary Clear
        
        for file in self.img_list: #All Image File List
            self.fileDict[file]= QLabel(file) #File Dictionary Append
            
        for file in self.fileDict.keys(): # All Image File Name
             #클릭하면 함수 실행 / FileName Label Click -> Image Viewer Window 실행
            self.clickable(self.fileDict[file]).connect(lambda f=file:self.showImagePopUp(f))
            # MouseOver  on File Name Label -> Change Cursor to Hand Shape 마우스 커서 손모양으로 변경
            self.fileDict[file].setCursor(QCursor(Qt.PointingHandCursor))
            
            fileLayout = QHBoxLayout() # File Name Layout, one line
            fileLayout.addWidget(self.fileDict[file], 2) # add File Name Label 
            
            radio_group = QButtonGroup() # Each File RadioButton GroupBox
            radio_group_layout = QHBoxLayout() # Group Layout
            radio_group.setExclusive(True) # RadioButton Click 하나만 되게 설정
            self.radioGroupset[file]=radio_group # add RadioButton Layout  to GoupBox 
            
            btn1 = QRadioButton( text="Correct")
            btn2 = QRadioButton( text="Incorrect")
            
            # set RadioButton Clicked Function 
            btn1.clicked.connect(self.justClickedRadio) 
            btn2.clicked.connect(self.justClickedRadio)
            
            # set StyleSheet on RadioButton
            radio_style = 'QRadioButton{font: 11pt;} QRadioButton::indicator { width: 15px; height: 15px;};'
            btn1.setStyleSheet(radio_style)
            btn2.setStyleSheet(radio_style)
            
            # add RadioButton on GroupBox
            radio_group.addButton(btn1)
            radio_group.addButton(btn2)
            self.radioSet[file] = (btn1, btn2)
            
            # add GroupBox on  Layout
            radio_group_layout.addWidget(self.radioSet[file][0]) # 라디오 버튼을 레이아웃에 추가
            radio_group_layout.addWidget(self.radioSet[file][1])
            # add GroupBoxLyaout on FileName Layout
            fileLayout.addLayout(radio_group_layout)
            
            # add FileNameLayout on MainLayout
            centerBox.addLayout(fileLayout)
        return 0
    
    # make Directory / Correct and Incorrect Directory
    def makeNewDir(self, dirname): #Parameter: directory name 폴더 이름 <string>
        try:
            # if same name directory do not exists 같은 이름 폴더 존재하지 않으면
            if not os.path.exists(self.dir_path +"/"+dirname):
                # make directory 폴더 생성
                os.makedirs(self.dir_path +"/"+dirname)
                
        except OSError:pass # same name directory exists
        return 0
    
    # File move to directory 분류한 파일을 디렉토리 이동
    def moveImageFile(self, correct, incorrect): #Parameter: correct file name list<list>, incorrect file name list<list>
        # file make using function
        self.makeNewDir("correct")
        self.makeNewDir("incorrect")
        
        for file in correct: # correct file list move to correct directory
            shutil.move(self.dir_path+"/"+file, self.dir_path+"/correct/"+file)
            
        for file in incorrect: # incorrect file list move to incorrect directory
            shutil.move(self.dir_path+"/"+file, self.dir_path+"/incorrect/"+file)
        
        return 0
    
    # New directory Open 디렉터리 새로 열기
    def changeDirFunc(self):
        temp = self.dir_path # original Directory Path
        orgDirText = self.dir_text.text() # original Label Text
        
        try:
            # Select Directory 폴더 선택창
            self.dir_path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
            self.dir_text.setText(self.dir_path) #Label Text Change
            self.img_list=[] # image FileName List 초기화
            
            for file in os.listdir(self.dir_path) : # Selected Directory All File 선택된 폴더의 모든 파일
                # file extension is image file 파일 확장자가 이미지 파일인 경우만 추가
                if file.split(".")[-1].lower() in self.file_extension: 
                    self.img_list.append(file)
                    
            # Label Text Change 라벨 텍스트 재설정
            self.AllBox.setText("Total "+str(len(self.img_list))+" /")
            self.addFileNameLayout(self.vbox)
            
        except(FileNotFoundError): # if close 취소할 경우
            # set original value  기존 값 재설정
            self.dir_path =temp
            self.dir_text.setText(orgDirText)
        
        return 0
    
    # GUI show on window center position / 어플을화면 중심에 위치시키는 함수
    def showCenter(self):
        appInfo = self.frameGeometry() # get Window Size, Position / 창의 위치 크기 정보 불러옴
        centerPositon = QDesktopWidget().availableGeometry().center() # get Window Center Postion / 화면 가운데 위치 식별
        appInfo.moveCenter(centerPositon) #move to Window Center / 화면 중심으로 이동
        self.move(appInfo.topLeft())
    
    # make GUI
    def initUI(self): # main user interface 
        self.setWindowTitle('Image Selector') #GUI Title
        self.setWindowIcon(QIcon('logo.PNG')) #set Icon File, 16x16, PNG file
        self.showCenter() #GUI position on window center 화면 중앙에 배치 
        self.setStyleSheet("background-color:white;") #배경색 설정
        
        """
        ------------  GUI 헤더  -------------
        """
        lb_head =  QVBoxLayout()
        head_style = ( # header stylesheet
                      "border-width: 0px;"
                      "color:white;"
                      "background-color: #F99625;"
                    )
        lb_title = QLabel('Image Selector',self) # Title Text
        # set Label Font 라벨 폰트 설정 /  ( font / size / bold )  
        lb_title.setFont(QFont('Trebuchet MS',20, QFont.Bold))
        lb_title.setAlignment(QtCore.Qt.AlignCenter) # text on center
        
        # directory path text 초기화
        self.dir_text = QLabel("Select Directory, first", self)
        self.dir_text.setFont(QFont(self.fontName,11))
        self.dir_text.setAlignment(QtCore.Qt.AlignCenter)
        
        
        lb_title.setStyleSheet(head_style) # set StyleSheet 
        # set Label Height 라벨 높이
        lb_title.setFixedHeight( int(self.HEIGHT/13) )
        self.dir_text.setFixedHeight( int(self.HEIGHT/18) )
        self.dir_text.setStyleSheet("background-color: #F7DCC2;")
        
        head_hbox = QHBoxLayout() # for open Folder Button 파일 열기 버튼
        path_change = QPushButton(self, text="Open Directory") # Button Name 버튼 이름
        # Button StyleSheet 버튼 스타일
        change_style  = "font-size: 13px;font-family:"+self.fontName+"""; background-color: #E7E3DF;\
                border-radius: 3px;border: 2px solid  #DDD9D5;padding:5px"""
        path_change.setStyleSheet(change_style)
        # set Function on Open Directory  버튼에 함수 설정
        path_change.clicked.connect(self.changeDirFunc)
        # add Empty Label for float:right 오른쪽 배치를 위해 빈 라벨 추가
        head_hbox.addWidget(QLabel(), 4) 
        head_hbox.addWidget(path_change)
        
        # add Widget on Header Label 헤더 라벨에 위젯 추가
        lb_head.addWidget(lb_title)
        lb_head.addWidget(self.dir_text)
        lb_head.addLayout(head_hbox)
        
        lb_head.setAlignment(Qt.AlignTop) # Header Label to top 헤더 라벨을 맨 위로 올리기
        
        
        """
        ------------  GUI 중앙  -------------
        """
        self.imageScroll = QScrollArea() # Scroll Area Box 스크롤 박스
        self.centerBox = QWidget() # Widget in Scrollbox
        self.vbox = QVBoxLayout() # Layout on Widget
        
        # set StyleSheet
        self.imageScroll.setStyleSheet("background-color:white;border:2px solid #F7DCC2;") 
        self.centerBox.setStyleSheet("border:0px solid #EFEBC0;")
        # set file Label  on Layout 파일 이름을 레이아웃에 추가
        self.addFileNameLayout(self.vbox)
        self.centerBox.setLayout(self.vbox) 

        self.imageScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) # 수직 스크롤바 항상 on
        self.imageScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) #수평 스크롤바 항상 off
        self.imageScroll.setWidgetResizable(True) # file size can resizeable 파일 사이즈 변경 가능
        self.imageScroll.setWidget(self.centerBox)
        
        """
        ------------  GUI 하단  -------------
        """
        
        # set Layouts
        self.lb_bottom = QVBoxLayout()
        self.lb_bottom_up = QHBoxLayout()
        self.lb_bottom_center = QHBoxLayout()
        self.lb_bottom_down =  QHBoxLayout()
        
        emptyBox = QLabel()
        emptyBoxLayout = QHBoxLayout()
        emptyBox.setLayout(emptyBoxLayout)
        
        '''
        Progress / 진행률
        '''
        self.progressBox = QLabel("Progress ") # Progress Text
        self.progressBox.setFont(QFont(self.fontName,13))
        self.progressBox.setAlignment(QtCore.Qt.AlignBottom)
        self.progressBox.setAlignment(QtCore.Qt.AlignLeft)
        
        self.progressPercent = QLabel("0 %..") # Working Percent 진행률 초기화
        self.progressPercent.setFont(QFont(self.fontName,13))
        self.progressPercent.setAlignment(QtCore.Qt.AlignLeft)
        
        emptyBoxLayout.addWidget(self.progressBox)
        emptyBoxLayout.addWidget(self.progressPercent)
        
        '''
        All Clickable Button / 전체 클릭 버튼
        '''
        self.lb_bottom_up.addWidget(emptyBox)
        self.lb_bottom_up.addWidget(QLabel())
        
        all_btn_group = QGroupBox() # All Correct / All Incorrect Button Groupbox
        all_btn_group.setStyleSheet("border:0px")
        all_btn_group.setFixedHeight(60)
        all_btn_layout = QHBoxLayout() # Group Layout
        AllButtonHeight = 40 # All Click Button Layout  Height모두 클릭 버튼 높이
        btn_style = "font-size: 15px;font-family: "+self.fontName+";border-radius: 8px;border: 4px solid "
        
        # make All Correct Button
        btn1 = QPushButton(all_btn_group, text="All Correct")
        btn1.setStyleSheet(btn_style+self.color_correct+";background-color:"+self.color_correct )
        btn1.setFixedHeight(AllButtonHeight) # set Button Height
        btn1.clicked.connect(self.AllRadioSelectCorrect)  # set Function on Button  클릭하면 함수 실행
        
        # make All Incorrect Button
        btn2 = QPushButton(all_btn_group, text="All Incorrect")
        btn2.setStyleSheet(btn_style+self.color_incorrect+";background-color:"+self.color_incorrect )
        btn2.setFixedHeight(AllButtonHeight)
        btn2.clicked.connect(self.AllRadioSelectIncorrect) 
        
        
        all_btn_layout.addWidget(btn1) # add PushButton on ButtonGruopLayout
        all_btn_layout.addWidget(btn2)
        all_btn_group.setLayout(all_btn_layout) # set Layout on GroupBox
        self.lb_bottom_up.addWidget(all_btn_group) # add GroupBox on Bottom Layout
        
        self.lb_bottom.addLayout(self.lb_bottom_up)
        self.lb_bottom.addLayout(self.lb_bottom_center)
        self.lb_bottom.addLayout(self.lb_bottom_down)
        
        '''
        Count Clicked Button 클릭 개수 / Reset Button 리셋 버튼
        '''
        # count Clicked Button 클릭된 버튼 개수 Label
        countBox = QHBoxLayout()
        self.AllBox = QLabel("Total "+str(len(self.img_list))+" /")
        self.AllBox.setAlignment(QtCore.Qt.AlignRight)
        self.AllBox.setFont(QFont(self.fontName,13))
        
        self.SelectCountText = str(self.checkedRadio)+" Select"
        self.SelectBox = QLabel(self.SelectCountText)
        self.SelectBox.setFont(QFont(self.fontName,13))
        self.SelectBox.setAlignment(QtCore.Qt.AlignLeft)
        
        countBox.addWidget(self.AllBox)
        countBox.addWidget(self.SelectBox)
        countBox.addWidget(QLabel(), 3)
        
        # make Reset Button 리셋 버튼 
        btn_reset_style = "font-size: 14px;font-family: "+self.fontName+""";background-color: #E7E3DF;
                        border-radius: 3px;border: 2px solid #DDD9D5;"""
        self.ResetButton = QPushButton("R E S E T")
        self.ResetButton.setStyleSheet(btn_reset_style+"margin-right: 11px;")
        self.ResetButton.clicked.connect(self.AllResetFunc)
        self.ResetButton.setFixedHeight(30)
        self.ResetButton.setFixedWidth(120)
        
        self.lb_bottom_center.addLayout(countBox)
        self.lb_bottom_center.addWidget(self.ResetButton)
        
        '''
        Working DONE Button / 작업 완료 버튼
        '''
        btn_finish_style = """color: white;font-weight:600;font-size: 25px ;background-color: #F6881A  ;
                        border-radius: 22px;border: 5px solid #E2811F ;font-family:"""+self.fontName#border: 4px solid #FE2E2E;
        selectFinish = QPushButton("D O N E")
        selectFinish.setStyleSheet(btn_finish_style)
        selectFinish.clicked.connect(self.doneWork) # set Function when clicked Button  함수 적용
        selectFinish.setFixedHeight(60)
        selectFinish.setFixedWidth(210)
        self.lb_bottom_down.addWidget(selectFinish)
        
        """
        ------------  set Final Layout / 최종 레이아웃 설정  -------------
        """
        # main Layout 
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(lb_head)
        self.mainLayout.addWidget(self.imageScroll)
        self.mainLayout.addLayout(self.lb_bottom)
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.mainLayout) #main layout
        
        self.show() # show GUI
        
    


# Image File Viewer Window, like Pop Up / 이미지 보여주는 별도의 창 생성
class ImageShowWindow(QWidget):
    # Parameter: file path 파일 경로<string>, gui width 기존 창 넓이<int>, gui x position 기존 창 x 값<int>, gui y position 기존 창 y 값<int>
    def __init__(self, path, parent_width, x, y):
        super().__init__()
        self.setWindowTitle('Image Viewer') #image Viewer Title
        
        layout = QVBoxLayout()
        self.viewer = QLabel()
        self.viewer.setAlignment(QtCore.Qt.AlignCenter)
        self.viewer.setFixedSize(570,570) # window size
        layout.addWidget(self.viewer)
        
        myPixmap = QPixmap(path) # get Image File
        myScaledPixmap = myPixmap.scaled(self.viewer.size(), Qt.KeepAspectRatio)
        self.viewer.setPixmap(myScaledPixmap)
        
        self.setFixedSize(600,600) # set Window Size
        self.setLayout(layout)
        # move window position -> left to original window / 이미지 팝업창을 기존 창 왼쪽으로 이동
        self.move(x-parent_width+20, y)
    

if __name__ == '__main__':
    # START GUI
    app = QApplication(sys.argv)
    ex = ImageSelector()
    sys.exit(app.exec_())
        