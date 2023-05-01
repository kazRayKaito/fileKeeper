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
h = logging.FileHandler("log/"+timeStamp+"_logtest.log")
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
from multiprocessing import Pool

#変数設定
modeIndex = 0
modeList = [
    "dirGeneration",
    "dirRenaming",
    "dirRemoval"
]
mode = modeList[modeIndex]

def startProcessing(mode):
    #マルチプロセス設定
    p = Pool(20)
    multiProcessArgs = []

    #dirListの場所確認
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    logger.debug(dirListPath)
    if not os.path.isfile(dirListPath):
        logger.error("'dirList.csv'が見つかりません。")
        return

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r')
    dirListLines = f.readlines()[1:]

    for dirListLine in dirListLines:
        #各行をカンマで分割し、変数代入
        items = dirListLine.split(',')

        if mode == "dirGeneration":
            rootPath = items[3]
            multiProcessArgs.append(rootPath)
            #os.system("start cmd /c Python " + scriptDir + "/dirGenerator.py " + str(counter))
        elif mode == "dirRenaming":
            multiProcessArgs.append(items)
        elif mode == "dirRemoval":
            multiProcessArgs.append(items)
    
    if mode == "dirGeneration":
        p.map(dirGenerator.generate, multiProcessArgs)
    elif mode == "dirRenaming":
        p.map(dirRenamer.rename, multiProcessArgs)
    elif mode == "dirRemoval":
        p.map(dirRemover.remove, multiProcessArgs)

#----------------------------------実行----------------------------------
if __name__ == "__main__":
    logger.debug("running as main. mode:"+mode)
    startProcessing(mode)
#----------------------------------実行----------------------------------