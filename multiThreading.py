#環境設定
import os
import sys
import time
from datetime import datetime as dt
sys.dont_write_bytecode = True

#日付取得
datetimeToday = dt.now()
dateStamp = datetimeToday.strftime("%Y-%m-%d") #("%Y-%m-%d_%H-%M-%S")

#ロガー設定
import logging
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

#ログフォルダ生成
logFolder = os.path.join(os.getcwd(),"異常ログ")
if not os.path.isdir(logFolder):
    os.mkdir(logFolder)

#ロガーフォーマット
errorHandler = logging.FileHandler(os.path.join("異常ログ",dateStamp+".log"))
fmt = logging.Formatter(
    '%(asctime)s:'
    '%(name)s:'
    '%(levelname)s:'
    '%(message)s'
)
errorHandler.setFormatter(fmt)
errorHandler.setLevel(logging.ERROR)
logger.addHandler(errorHandler)

eachStatus = []

#モジュールインポート
import statusKeeper
import dirOrganizer
import threading

def startProcessing():
    #マルチスレッド設定

    #dirListの場所確認
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    logger.debug(dirListPath)
    if not os.path.isfile(dirListPath):
        logger.error("'dirList.csv'が見つかりません。")
        return

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r', encoding="utf-8")
    dirListLines = f.readlines()[1:]

    multiThreadArgs = []
    names = []
    for dirListLine in dirListLines:
        items = dirListLine.split(',')
        names.append(items[0] + "_" + items[1] + "_" + items[2])
        multiThreadArgs.append(items)

    localEachStatus = []

    for name in names:
        statusKeeper.eachStatus.append([name, "開始前待機中", 0])
        localEachStatus.append([name, "開始前待機中", 0])

    statusLock = threading.Lock()

    threads = []
    for threadIndex in range(len(multiThreadArgs)):
        threads.append(threading.Thread(target=dirOrganizer.organize, args=(multiThreadArgs[threadIndex], statusLock, threadIndex)))
    
    for thread in threads:
        thread.start()

    while True:
        statusLock.acquire()
        for threadIndex, thread in enumerate(statusKeeper.eachStatus):
            for itemIndex, threadIteam in enumerate(thread):
                localEachStatus[threadIndex][itemIndex] = threadIteam
        statusLock.release()

        allDone = True
        allClear = True

        #os.system('cls')
        for localStatus in localEachStatus:
            print(localStatus[0] + ":" + localStatus[1])
            if localStatus[2] == 0:
                allDone = False
            if localStatus[2] != 1:
                allClear = False
        
        if allClear:
            print("完了：全て正常終了")
            break

        if allDone:
            print("終了：一部異常終了")
            break
        
        time.sleep(1)

    for thread in threads:
        thread.join()

#----------------------------------実行----------------------------------
if __name__ == "__main__":
    logger.debug("running as main")
    statusKeeper.initialize()
    startProcessing()
#----------------------------------実行----------------------------------