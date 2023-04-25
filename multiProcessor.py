import os
import sys
from datetime import datetime as dt

#環境設定
sys.dont_write_bytecode = True

todaysdate = dt.now()
todaysdateStamp = todaysdate.strftime("%Y-%m-%d")

rootDir = "C:/Users/Kazuk/Documents/2_Projects/fileControl2"
scriptDir = os.getcwd()
dirListPath = scriptDir + "/dirList.csv"


print(dirListPath)

#dirList.csvを開いて、1行ずつ読み込み
f = open(dirListPath, 'r')
dirListLines = f.readlines()

counter = 0

for dirListLine in dirListLines:
    #各行をカンマで分割し、変数代入
    items = dirListLine.split(',')
    rootPath = items[0]
    folderStructure = items[1]
    preservationDays = items[2]
    monthlyArchiveNumber = items[3]
    
    #dirRenamer.rename(rootPath, folderStructure, preservationDays, monthlyArchiveNumber)
    os.system("start cmd /c Python " + scriptDir + "/dirGenerator.py " + str(counter))
    counter = counter + 1