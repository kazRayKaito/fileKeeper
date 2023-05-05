import os
import sys
import random
import math
import logging
import threading
from datetime import datetime as dt
from datetime import timedelta as td
from subprocess import call
import pywintypes, win32file, win32con

#環境設定
sys.dont_write_bytecode = True

#日付取得
todaysdate = dt.now()
todaysdateStamp = todaysdate.strftime("%Y-%m-%d")

#ロガー設定
import logging
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

#ロガーフォーマット
handler = logging.StreamHandler()
fmt = logging.Formatter(
    '%(asctime)s:'
    '%(name)s:'
    '%(levelname)s:'
    '%(message)s'
)
handler.setFormatter(fmt)
logger.addHandler(handler)

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

def generate(items):
    #変数定義
    rootDir = items[3]
    runningOS = "Windows"
    
    if os.path.isdir(os.path.dirname(rootDir)) == False:
        logger.error(f"Parent Directory does NOT exist at {os.path.dirname(rootDir)}")
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
            "fileG.txt"]


    for month in range(0, monthCount + 1):
        months.append(month)
        dirName = os.path.join(rootDir,str(month))
        if os.path.isdir(dirName):
            logger.info(f"{dirName} already exists")
        else:
            logger.info(f"creating {dirName}")
            os.mkdir(dirName)
        
        for fileName in files:
            #ファイルパス定義
            filePath = os.path.join(dirName,fileName)

            if os.path.isfile(filePath) == False:
                with open(filePath, "w") as f:
                    f.write("New File Generated!")

            if os.path.isfile(filePath):
                randomDays = math.floor(random.random()*30)
                newDate = todaysdate - td(days = (month*30 + randomDays))

                if runningOS == "Mac":
                    changeFileDateOnMac(filePath, newDate)
                elif runningOS == "Windows":
                    changeFileDateOnWindows(filePath, newDate)

def startProcessing():
    #dirListの場所確認
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    if not os.path.isfile(dirListPath):
        logger.error("'dirList.csv'が見つかりません。")
        return

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r', encoding="utf-8")
    dirListLines = f.readlines()[1:]

    multiThreadArgs = []
    for dirListLine in dirListLines:
        items = dirListLine.split(',')
        multiThreadArgs.append(items)

    threads = []
    for threadIndex in range(len(multiThreadArgs)):
        threads.append(threading.Thread(target=generate, args=(multiThreadArgs[threadIndex], )))
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
#----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    logger.debug("running as main")
    startProcessing()
#----------------------------------動作確認用----------------------------------