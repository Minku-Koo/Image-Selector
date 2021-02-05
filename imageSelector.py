# -*- conding: utf-8 -*-
'''
# python

- Project Name : Image File Selector (for make image Data-Set)
- Created Date : 26/Dec/2020
- Updated Date : 06/Jan/2021
- Author : Minku Koo
- E-Mail : corleone@kakao.com
- Version : 1.1.1
- Keywords : 'PyQt5', 'Python', 'image', 'viewer', 'big data', 'gui', 'selector', 'classify'
- Github URL : https://github.com/Minku-Koo/Image-Selector

# How to use?
- Select Source directory (Work Place)
- Select Target directory (Classified file save)
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
from PyQt5.Qt import Qt
import datetime

# QPixmap에서 JPG 파일이 보여지지 않는 경우 설정(환경변수 추가)
# if jpg file cannot showed on pixmap -> try, add this code 
qt_path= os.path.dirname(PyQt5.__file__)
os.environ['QT_PLUGIN_PATH'] = os.path.join(qt_path, "Qt/plugins")

class ImageSelector(QWidget):
    def __init__(self):
        super(ImageSelector, self).__init__()
        # GUI 높이/길이
        self.HEIGHT = 800
        self.WIDTH = 800 * 2
        self.resize(self.WIDTH, self.HEIGHT)
        # self.setFixedSize(self.WIDTH, self.HEIGHT) #높이 길이 설정
        self.dir_path = "" #작업 디렉토리 선언
        self.target_path = "" #대상 디렉토리 선언
        self.img_list=[] #이미지 파일 리스트
        self.file_extension = ["jpg","jpeg","png"] #작업 가능한 파일 확장자
        self.imageScrollHeight = self.HEIGHT * 0.7 #중앙 작업 박스(스크롤 영역) 높이 설정
        # self.imageWindow = None # 이미지 보여주기 window 초기화
        self.fileDict = {} # key=file name value=Label Stylesheet
        self.radioSet = {} # key=file name, value=RadioButton Click Position
        self.radioGroupset={} # key=file name, value= 하나만 클릭가능한지 여부
        self.checkedRadio =0 #라디오 버튼 체크 개수
        self.now_file = -1 #현재파일 index
        # self.before_file = -1 #기존 클릭 파일 index
        self.scrollMax = 0 #스크롤바 최대 값
        self.now_scroll = 0.0 #현재 스크롤바 값
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
   
    # file name clieck -> image show 이미지 클릭하면 이미지 보여줌
    # default key =0, if keyboard  pressed > 1, mouse pressed >0 / key는 기본값 0, 키보드 입력의 경우 1 입력
    def showImageViewer(self, filename, key=0): 
        if key==0: # 마우스 클릭인 경우만 now_scroll 변수 변경
            self.now_scroll = self.imageScroll.verticalScrollBar().value()
        
        self.image_path.setText(filename) # 파일 이름 설정
        self.now_file = self.img_list.index(filename) #현재 클릭 파일 이름 설정
        self.CountRadioCheck()
        
        myPixmap = QPixmap(self.dir_path+"/"+filename) # get Image File
        myScaledPixmap = myPixmap.scaled(self.viewer.size(), Qt.KeepAspectRatio)
        self.viewer.setPixmap(myScaledPixmap) # show image
    
    # all correct / all incorrect button clicked function
    def AllSelector(self):
        self.checkedRadio = len(self.img_list) # Checked RadioButton 개수 == 전체 이미지파일 개수
        self.SelectCountText=str(self.checkedRadio)+" Select"
        self.SelectBox.setText(self.SelectCountText) #Label Text Change, Count
        self.progressPercent.setText("100 %..") #Label Text Change, Percent
        return 0
    
    # RadioButton 전체 Correct로 선택 
    def AllRadioSelectCorrect(self):
        for file in self.img_list: # 모든 이미지 파일 이름 All ImageFile Name
            self.radioSet[file][0].setChecked(True) #RadioButton Selec just one 라디오 버튼 하나만 선택 가능
            # Correct 선택한 모든 Label 색상 변경
            self.fileDict[file].setStyleSheet("background-color:"+self.color_correct)
            
        self.AllSelector()
        return 0
    
    # RadioButton 전체 Incorrect 선택
    def AllRadioSelectIncorrect(self):
        for file in self.img_list: # 모든 이미지 파일 이름 All ImageFile Name
            self.radioSet[file][1].setChecked(True) #RadioButton Selec just one 라디오 버튼 하나만 선택 가능
            # Incorrect 선택한 모든 Label 색상 변경
            self.fileDict[file].setStyleSheet("background-color:"+self.color_incorrect)
            
        self.AllSelector()
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
            else:  backColor+="#ffffff"
            
            if file == self.img_list[self.now_file]:
                backColor += ";border: 2px solid ;padding:0px;"
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
            if nextStep== QMessageBox.Yes: self.changeDirFunc(0)
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
            
        # for file in self.fileDict.keys(): # All Image File Name
             #클릭하면 함수 실행 / FileName Label Click -> Image Viewer 실행
            self.clickable(self.fileDict[file]).connect(lambda f=file:self.showImageViewer(f))
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
            if not os.path.exists(self.target_path +"/"+dirname):
                # make directory 폴더 생성
                os.makedirs(self.target_path +"/"+dirname)
        except OSError: pass # same name directory exists
        return 0
    
    # File move to directory 분류한 파일을 디렉토리 이동
    def moveImageFile(self, correct, incorrect): #Parameter: correct file name list<list>, incorrect file name list<list>
        dir_name = "/"+self.dir_path.split('/')[-1]+"-classified"
        # file make using function
        self.makeNewDir(dir_name+"/correct")
        self.makeNewDir(dir_name+"/incorrect")
        
        for file in correct: # correct file list move to correct directory
            shutil.move(self.dir_path+"/"+file, self.target_path+dir_name+"/correct/"+file)
            
        for file in incorrect: # incorrect file list move to incorrect directory
            shutil.move(self.dir_path+"/"+file, self.target_path+dir_name+"/incorrect/"+file)
        
        # write log file for history 로그 파일 기록
        self.makeLogfile(len(correct),len(incorrect))
        return 0
    
    #  make Log file  that file classify history (.txt.) / 파일 분류 기록을 위한 로그 파일 생성
    def makeLogfile(self, correct_count, incorrect_count): #Parameter: correct count <int>, incorrect count <int>
        dir_name = "/"+self.dir_path.split('/')[-1]+"-classified" # now work directory name 현재 작업 폴더 이름
        nowTime = datetime.datetime.now() # now date and time 현재 날짜 및 시간
        nowDateTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
        fileWrite = '['+nowDateTime+'] <' + self.dir_path +" => " +self.target_path+dir_name+"> "
        fileWrite += "Correct File :"+str(correct_count)+" / Incorrect File :"+str(incorrect_count)
        
        logfile = "log.txt" # log file name 로그 파일 이름
        with open(logfile, 'at', encoding='utf-8') as f:
            f.write(fileWrite)
            f.write('\n')
        
        return 0

    # New directory Open 디렉터리 새로 열기 / Parameter: source (0) OR target (1) <int>
    def changeDirFunc(self, where):
        if where==0: # source directory
            temp = self.dir_path # original Directory Path
            orgDirText = self.dir_text.text() # original Label Text
        else: # target directory
            temp = self.target_path # original Directory Path
            orgDirText = self.target_dir_text.text() # original Label Text
        
        try:
            if where==0:
                # Select Directory 폴더 선택창
                self.dir_path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
                self.dir_text.setText(self.dir_path) #Label Text Change
                
                self.target_path = self.dir_path
                self.target_dir_text.setText(self.target_path) #Label Text Change
                
                if self.dir_path!="":self.img_list=[] # image FileName List 초기화
                
                for file in os.listdir(self.dir_path) : # Selected Directory All File 선택된 폴더의 모든 파일
                    # file extension is image file 파일 확장자가 이미지 파일인 경우만 추가
                    if file.split(".")[-1].lower() in self.file_extension: 
                        self.img_list.append(file)
                
                # Label Text Change 라벨 텍스트 재설정
                self.AllBox.setText("Total "+str(len(self.img_list))+" /")
                self.addFileNameLayout(self.vbox)
            else:
                self.target_path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
                self.target_dir_text.setText(self.target_path) #Label Text Change
            
        except(FileNotFoundError): # if close 취소할 경우
            # set original value  기존 값 재설정
            if where ==0:
                self.dir_path =temp
                self.dir_text.setText(orgDirText)
        if self.target_path=="":
            if where==1 :
                self.target_path =temp
                self.target_dir_text.setText(orgDirText)
            if where==0 :
                self.target_path = self.dir_path
                self.target_dir_text.setText(self.dir_path)
        
        return 0
    
    # GUI show on window center position / 어플을화면 중심에 위치시키는 함수
    def showCenter(self):
        appInfo = self.frameGeometry() # get Window Size, Position / 창의 위치 크기 정보 불러옴
        centerPositon = QDesktopWidget().availableGeometry().center() # get Window Center Postion / 화면 가운데 위치 식별
        appInfo.moveCenter(centerPositon) #move to Window Center / 화면 중심으로 이동
        self.move(appInfo.topLeft())
        return 0
    
    #키보드를 누르면 함수 실행
    def keyPressEvent(self, e):
        move = 0 # file chage check 위아래인지 구별, 이미지 바뀌는지 여부
        
        def addBorder(): # now label add border 현재 보여주는 이미지 파일 라벨에 테두리 추가
            filename = self.img_list[self.now_file]
            self.showImageViewer(filename, key=1)
            self.CountRadioCheck()
            
        if e.key() == Qt.Key_W: # W key
            if self.now_file > 0: # file is not first 파일이 첫번째가 아닌 경우
                self.now_file -=1 
                addBorder()
                move = -1 # file move
                
        elif e.key() == Qt.Key_S: # S key
            if self.now_file < len(self.img_list)-1: # file is not end 파일이 마지막이 아닌 경우
                self.now_file +=1
                addBorder()
                move = 1 # file move
                
        elif e.key() == Qt.Key_Return: # Enter key 엔터
            # check correct 
            self.radioSet[self.img_list[self.now_file]][0].setChecked(True)
            self.justClickedRadio()
            
        elif e.key() == Qt.Key_Shift: # Shift key 쉬프트
            # check incorrect 
            self.radioSet[self.img_list[self.now_file]][1].setChecked(True)
            self.justClickedRadio()
        
        # calculation for scroll move 
        if move != 0: # if W or S key 
            # scroll max height 스크롤 최대 길이
            self.scrollMax =self.imageScroll.verticalScrollBar().maximum()
            # center label height 중앙 라벨 길이
            centerHeight = self.imageScroll.height()
            # file label height 파일 라벨 길이
            labelHeight = self.fileDict[self.img_list[self.now_file]].height()
            # file label count in center label 중앙 라벨에 표시되는 파일 라벨 개수
            count = int(centerHeight / labelHeight) 
            # scroll up or down at one 한번에 이동할 스크롤 범위
            scroll =  int((self.scrollMax+centerHeight) / len(self.img_list))
            
            if self.now_file > len(self.img_list)-int(count/2) and move<0: pass
            elif  self.now_file < int(count/2)  and move>0: pass
            else: # if file is not first and end
                if move>0 and self.now_scroll >= self.scrollMax : pass
                elif move<0 and self.now_scroll <=0: pass
                # calculate scroll
                else:  self.now_scroll = self.now_scroll +  scroll * move
            # scroll move 스크롤 이동
            self.imageScroll.verticalScrollBar().setSliderPosition( self.now_scroll )
        
    # make GUI
    def initUI(self): # main user interface 
        self.setWindowTitle('Image Selector') #GUI Title
        self.setWindowIcon(QIcon('logo.PNG')) #set Icon File, 16x16, PNG file
        self.showCenter() #GUI position on window center 화면 중앙에 배치 
        self.setStyleSheet("background-color:white;") #배경색 설정
        
        """
        ------------  GUI Header 헤더  -------------
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
        self.dir_text.setFont(QFont(self.fontName,9))
        self.dir_text.setAlignment(QtCore.Qt.AlignCenter)
        
        lb_title.setStyleSheet(head_style) # set StyleSheet 
        # set Label Height 라벨 높이
        lb_title.setFixedHeight( int(self.HEIGHT/13) )
        self.dir_text.setFixedHeight( int(self.HEIGHT/20) )
        self.dir_text.setStyleSheet("background-color: #F7DCC2;")
        
        source_box = QHBoxLayout() # for open Folder Button 파일 열기 버튼
        path_change = QPushButton(self, text=" Source Directory") # Button Name 버튼 이름
        path_change.setCursor(QCursor(Qt.PointingHandCursor))
        # Button StyleSheet 버튼 스타일
        change_style  = "font-size: 13px;font-family:"+self.fontName+"""; background-color: #E7E3DF;\
                border-radius: 3px;border: 2px solid  #DDD9D5;padding:5px"""
        path_change.setStyleSheet(change_style)
        # set Function on Open Directory  버튼에 함수 설정
        self.clickable(path_change).connect(lambda :self.changeDirFunc(0))
        # add Empty Label for float:right 오른쪽 배치를 위해 빈 라벨 추가
        source_box.addWidget(self.dir_text, 4) 
        source_box.addWidget(path_change)
        
        # target directory path text 초기화
        self.target_dir_text = QLabel("Target Directory Path", self)
        self.target_dir_text.setFont(QFont(self.fontName,9))
        self.target_dir_text.setAlignment(QtCore.Qt.AlignCenter)
        self.target_dir_text.setFixedHeight( int(self.HEIGHT/20) )
        self.target_dir_text.setStyleSheet("background-color: #F7DCC2;")
        
        target_box = QHBoxLayout() # for open Folder Button 파일 열기 버튼
        target_path_change = QPushButton(self, text=" Target Directory ") # Button Name 버튼 이름
        target_path_change.setCursor(QCursor(Qt.PointingHandCursor))
        # Button StyleSheet 버튼 스타일
        change_style  = "font-size: 13px;font-family:"+self.fontName+"""; background-color: #E7E3DF;\
                border-radius: 3px;border: 2px solid  #DDD9D5;padding:5px"""
        target_path_change.setStyleSheet(change_style)
        # set Function on Open Directory  버튼에 함수 설정
        self.clickable(target_path_change).connect(lambda :self.changeDirFunc(1))
        # add Empty Label for float:right 오른쪽 배치를 위해 빈 라벨 추가
        target_box.addWidget(self.target_dir_text, 4) 
        target_box.addWidget(target_path_change)
        
        # Keyboard pressed information 키보드 입력 정보
        keyboard_info = QLabel("Up:<W>  Down:<S>  Correct:<Enter>  Incorrect:<Shift>", self)
        keyboard_info.setFont(QFont(self.fontName,10))
        keyboard_info.setFixedHeight( 14)
        keyboard_info.setAlignment(QtCore.Qt.AlignCenter)
        
        # add Widget on Header Label 헤더 라벨에 위젯 추가
        lb_head.addWidget(lb_title)
        lb_head.addLayout(source_box)
        lb_head.addLayout(target_box)
        lb_head.addWidget(keyboard_info)
        
        lb_head.setAlignment(Qt.AlignTop) # Header Label to top 헤더 라벨을 맨 위로 올리기
        
        
        """
        ------------  GUI Center 중앙  -------------
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
        ------------  GUI Bottom 하단  -------------
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
        btn1.setCursor(QCursor(Qt.PointingHandCursor))
        btn1.setStyleSheet(btn_style+self.color_correct+";background-color:"+self.color_correct )
        btn1.setFixedHeight(AllButtonHeight) # set Button Height
        btn1.clicked.connect(self.AllRadioSelectCorrect)  # set Function on Button  클릭하면 함수 실행
        
        # make All Incorrect Button
        btn2 = QPushButton(all_btn_group, text="All Incorrect")
        btn2.setCursor(QCursor(Qt.PointingHandCursor))
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
        self.ResetButton.setCursor(QCursor(Qt.PointingHandCursor))
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
        selectFinish.setCursor(QCursor(Qt.PointingHandCursor))
        selectFinish.setStyleSheet(btn_finish_style)
        selectFinish.clicked.connect(self.doneWork) # set Function when clicked Button  함수 적용
        selectFinish.setFixedHeight(60)
        selectFinish.setFixedWidth(210)
        self.lb_bottom_down.addWidget(selectFinish)
        
        """
        ------------  set Final Layout / 최종 레이아웃 설정  -------------
        """
        #    Image Viewer     이미지 뷰어 
        self.imageBoxLayout = QVBoxLayout()
        self.view_layout = QVBoxLayout()
        # file name / 파일 이름 초기화
        self.image_path = QLabel("[ Image Viewer ]  File Path will be showed here")
        self.viewer = QLabel()
        self.viewer.setAlignment(QtCore.Qt.AlignCenter)
        self.viewer.resize( int(self.WIDTH/2),700) # image size
        # self.viewer.setFixedSize( int(self.WIDTH/2),700) # window size
        self.view_layout.addWidget(self.image_path, 1)
        self.view_layout.addWidget(self.viewer,6)
        self.image_path.setFont(QFont(self.fontName, 13))
        self.imageBoxLayout.addLayout(self.view_layout)
        
        # main Layout 
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(lb_head)
        self.mainLayout.addWidget(self.imageScroll)
        self.mainLayout.addLayout(self.lb_bottom)
        self.mainLayout.setAlignment(Qt.AlignTop)
        
        self.allLayout = QHBoxLayout()
        self.allLayout.addLayout(self.imageBoxLayout, 5)
        self.allLayout.addLayout(self.mainLayout, 3)
        self.setLayout(self.allLayout) 
        
        self.show() # show GUI
        
    

if __name__ == '__main__':
    # START APP
    app = QApplication(sys.argv)
    ex = ImageSelector()
    sys.exit(app.exec_())
        