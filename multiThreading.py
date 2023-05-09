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
logFolder = os.path.join(os.getcwd(),"ログ_異常履歴")
if not os.path.isdir(logFolder):
    os.mkdir(logFolder)

#ロガーフォーマット
errorHandler = logging.FileHandler(os.path.join(logFolder,dateStamp+".log"))
fmt = logging.Formatter(
    '%(asctime)s:'
    '%(name)s:'
    '%(levelname)s:'
    '%(message)s'
)
errorHandler.setFormatter(fmt)
errorHandler.setLevel(logging.ERROR)
logger.addHandler(errorHandler)

#モジュールインポート
import statusKeeper
import dirOrganizer
import threading

def startProcessing():
    #dirListの場所確認
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    if not os.path.isfile(dirListPath):
        logger.error(f"'dirList.csv'が見つかりません。 at {dirListPath}")
        return
    
    #statusKeeper設定
    sk = statusKeeper.statusKeeper(threading.Lock(),False)

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r', encoding="utf-8")
    dirListLines = f.readlines()[1:]

    organizers = []
    for dirIndex, dirListLine in enumerate(dirListLines):
        items = dirListLine.split(',')
        name = f"{items[0]}_{items[1]}_{items[2]}_{dirIndex}"
        rootPath = items[3]
        preservationStructure = items[4]
        preservationDays = items[5]
        sk.appendStatus([name, "開始待機中", 0])
        organizers.append(dirOrganizer.organizer(name,
                                                 rootPath,
                                                 preservationStructure,
                                                 preservationDays,
                                                 dirIndex,
                                                 sk))

    threads = []
    for organizer in organizers:
        threads.append(threading.Thread(target=organizer.organize, args=()))
    
    for thread in threads:
        thread.start()

    while True:
        if sk.displayStatus():
            break

        time.sleep(0.2)

    for thread in threads:
        thread.join()

#----------------------------------実行----------------------------------
if __name__ == "__main__":
    logger.debug("running as main")
    startProcessing()
#----------------------------------実行----------------------------------