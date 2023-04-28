import os
import sys
import dirRenamer
import dirRemover
import dirGenerator
from multiprocessing import Pool
from datetime import datetime as dt

#環境設定
sys.dont_write_bytecode = True

#変数設定
modeIndex = 2
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
    print(dirListPath)

    #dirList.csvを開いて、1行ずつ読み込み
    f = open(dirListPath, 'r')
    dirListLines = f.readlines()[1:]

    for dirListLine in dirListLines:
        #各行をカンマで分割し、変数代入
        items = dirListLine.split(',')

        if mode == "dirGeneration":
            rootPath = items[0]
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

#----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")

    startProcessing(mode)
#----------------------------------動作確認用----------------------------------