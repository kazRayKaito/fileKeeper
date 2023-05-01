#環境設定
import os
import sys
from datetime import datetime as dt
sys.dont_write_bytecode = True

#日付取得
timenow = dt.now()
timeStamp = timenow.strftime("%Y-%m-%d") #("%Y-%m-%d_%H-%M-%S")

#ロガー設定
import logging
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

#ログフォルダ生成
logFolder = os.getcwd()+"/log"
if not os.path.isdir(logFolder):
    os.mkdir(logFolder)

#ロガーフォーマット
h = logging.FileHandler("log/"+timeStamp+"_log.log")
fmt = logging.Formatter(
    '%(asctime)s:'
    '%(name)s:'
    '%(levelname)s:'
    '%(message)s'
)
h.setFormatter(fmt)
logger.addHandler(h)

#モジュールインポート
import dirRenamer
import dirRemover
import dirGenerator
import threading
from multiprocessing import Pool

#変数設定
modeIndex = 0
modeList = [
    "dirGeneration",
    "dirRenaming",
    "dirRemoval"
]
mode = modeList[modeIndex]

eachStatus = []

def startProcessing(mode):
    #マルチスレッド設定

    #dirListの場所確認
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    logger.debug(dirListPath)
    if not os.path.isfile(dirListPath):
        logger.error("'dirList.csv'が見つかりません。")
        return

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r')
    dirListLines = f.readlines()[1:]

    multiThreadArgs = []
    names = []
    for dirListLine in dirListLines:
        items = dirListLine.split(',')
        names.append(items[0] + "_" + items[1] + "_" + items[2])
        multiThreadArgs.append(items)
    if mode == "dirGeneration":
        multiThreadRun = dirGenerator.generate
    elif mode == "dirRenaming":
        multiThreadRun = dirRenamer.rename
    elif mode == "dirRemoval":
        multiThreadRun = dirRemover.remove

    global eachStatus

    for name in names:
        eachStatus.append([name,"InitialState"])

    statusLock = threading.Lock()

    threads = []
    for threadIndex in range(len(multiThreadArgs)):
        threads.append(threading.Thread(target=multiThreadRun, args=(multiThreadArgs[threadIndex],statusLock)))
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

#----------------------------------実行----------------------------------
if __name__ == "__main__":
    logger.debug("running as main. mode:"+mode)
    startProcessing(mode)
#----------------------------------実行----------------------------------