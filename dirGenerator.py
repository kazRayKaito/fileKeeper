import os
import sys
import random
import math
import time
import logging
from datetime import datetime as dt
from datetime import timedelta as td
from subprocess import call
import pywintypes, win32file, win32con

#環境設定
sys.dont_write_bytecode = True

#ロガー設定
logger = logging.getLogger("main").getChild("generator")

#日付取得
todaysdate = dt.now()
todaysdateStamp = todaysdate.strftime("%Y-%m-%d")

def changeFileDateOnWindows(filePath, newDate):
    wintime = pywintypes.Time(newDate)
    winfile = win32file.CreateFile(
        filePath,
        win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL,
        None
    )
    win32file.SetFileTime(winfile, wintime, wintime, wintime)
    winfile.close()

def changeFileDateOnMac(filePath, newDate):
    tmMonth = str(newDate.timetuple().tm_mon).zfill(2)
    tmDay = str(newDate.timetuple().tm_mday).zfill(2)
    tmYear = str(newDate.timetuple().tm_year)
    dateString = tmMonth + "/" + tmDay + "/" + tmYear
    command = 'SetFile -d ' + dateString + ' 00:00:00 ' + filePath
    call(command, shell=True)

def generate(items, lock):
    #引数分解
    name = items[0] + "_" + items[1] + "_" + items[2]
    rootDir = items[3]
    folderStructure = items[4]
    preservationDays = items[5]
    monthlyArchiveNumber = items[6]
    runningOS = "Windows"
    
    if os.path.isdir(os.path.dirname(rootDir)) == False:
        print("Parent Directory does NOT exist at " + os.path.dirname(rootDir))
        return()

    if os.path.isdir(rootDir) == False:
        os.mkdir(rootDir)

    monthCount = 30
    months = []

    files = ["fileA.txt",
            "fileB.txt",
            "fileC.txt",
            "fileD.txt",
            "fileE.txt",
            "fileF.txt",
            "fileG.txt",
            "fileH.txt",
            "fileI.txt",
            "fileJ.txt",
            "fileK.txt",
            "fileL.txt",
            "fileM.txt",
            "fileN.txt",
            "fileO.txt",
            "fileP.txt",
            "fileQ.txt",
            "fileR.txt",
            "fileS.txt"]


    for month in range(0, monthCount + 1):
        months.append(month)
        dirName = rootDir + "/" + str(month)
        if os.path.isdir(dirName):
            logger.info(dirName + " does exist")
        else:
            os.mkdir(dirName)
        
        for fileName in files:
            #ファイルパス定義
            filePath = os.path.join(dirName,fileName)

            if os.path.isfile(filePath) == False:
                logger.info("File does NOT exitst")
                with open(dirName + "/" + fileName, "w") as f:
                    f.write("New File Generated!")

            if os.path.isfile(filePath):
                logger.info("File does exist:" + dirName+"/"+fileName)
                randomDays = math.floor(random.random()*30)
                newDate = todaysdate - td(days = (month * 30 + randomDays/30))

                if runningOS == "Mac":
                    changeFileDateOnMac(filePath, newDate)
                elif runningOS == "Windows":
                    changeFileDateOnWindows(filePath, newDate)

#----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")

    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    print(dirListPath)

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r')
    dirListLines = f.readlines()[1:]

    for dirListLine in dirListLines:
        #各行をカンマで分割し、変数代入
        rootPath = dirListLine.split(',')[0]
        generate(rootPath)
#----------------------------------動作確認用----------------------------------