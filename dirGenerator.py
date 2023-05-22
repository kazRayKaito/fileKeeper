import os
import sys
import random
import math
import shutil
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

#変数設定
runningOS = "Windows"
lotOfDirs = True

def changeFileDateOnWindows(filePath, newDate):
    #Windowsでファイル生成日時変更
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
    #Macでファイル生成日時変更
    tmMonth = str(newDate.timetuple().tm_mon).zfill(2)
    tmDay = str(newDate.timetuple().tm_mday).zfill(2)
    tmYear = str(newDate.timetuple().tm_year)
    dateString = tmMonth + "/" + tmDay + "/" + tmYear
    command = 'SetFile -d ' + dateString + ' 00:00:00 ' + filePath
    call(command, shell=True)

def generate(rootDir):
    #変数定義
    monthCount = 180 if lotOfDirs else 30
    files = ["fileA.txt",
            "fileB.txt",
            "fileC.txt",
            "fileD.txt",
            "fileE.txt",
            "fileF.txt",
            "fileG.txt"]
    
    #親フォルダがない場合はエラーで終了
    if os.path.isdir(os.path.dirname(rootDir)) == False:
        logger.error(f"Parent Directory does NOT exist at {os.path.dirname(rootDir)}")
        return()
    
    #対象フォルダがない場合は、フォルダ生成前に削除
    if os.path.isdir(rootDir):
        shutil.rmtree(rootDir)
    
    os.mkdir(rootDir)

    for month in range(0, monthCount + 1):
        #対象フォルダ内で月別フォルダを生成
        monthlydDirName = os.path.join(rootDir,str(month))
        if os.path.isdir(monthlydDirName):
            logger.info(f"{monthlydDirName} already exists")
        else:
            logger.info(f"creating {monthlydDirName}")
            os.mkdir(monthlydDirName)
        
        for fileName in files:
            #月別フォルダ内で各ファイル生成
            filePath = os.path.join(monthlydDirName,fileName)
            if not os.path.isfile(filePath):
                with open(filePath, "w") as f:
                    f.write("New File Generated!")

            #フォルダが生成されてない場合はエラーでスキップ
            if not os.path.isfile(filePath):
                logger.error("New File Generation Failed")
                continue

            #ファイルの新規日付を算出
            offset = 6 if lotOfDirs else 30
            randomDays = math.floor(random.random()*offset) * 0
            randomTime = random.random()
            newDate = todaysdate - td(days = (month*offset + randomDays + randomTime))

            #ファイルの日付を変更
            if runningOS == "Mac":
                changeFileDateOnMac(filePath, newDate)
            elif runningOS == "Windows":
                changeFileDateOnWindows(filePath, newDate)

def startProcessing():
    #変数定義
    rootDirList = []
    threads = []

    #dirListの場所確認
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    if not os.path.isfile(dirListPath):
        logger.error("'dirList.csv'が見つかりません。")
        return

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r', encoding="CP932")
    dirListLines = f.readlines()[1:]

    #フォルダ名取得
    for dirListLine in dirListLines:
        rootDir = dirListLine.split(',')[3]
        rootDirList.append(rootDir)

    #スレッド定義
    for threadIndex in range(len(rootDirList)):
        threads.append(threading.Thread(target=generate, args=(rootDirList[threadIndex], )))
    
    #スレッド処理開始
    for thread in threads:
        thread.start()

    #スレッド処理合流
    for thread in threads:
        thread.join()
#----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    logger.debug("running as main")
    startProcessing()
#----------------------------------動作確認用----------------------------------