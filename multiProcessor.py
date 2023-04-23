import os
import sys
import multiprocessing
import dirRenamer
from datetime import datetime as dt

#環境設定
sys.dont_write_bytecode = True

todaysdate = dt.now()
todaysdateStamp = todaysdate.strftime("%Y-%m-%d")

rootDir = "C:/Users/Kazuk/Documents/2_Projects/fileControl2"
dirListPath = os.getcwd() + "/dirList.csv"

print(dirListPath)

#dirList.csvを開いて、1行ずつ読み込み
f = open(dirListPath, 'r')
dirListLines = f.readlines()

for dirListLine in dirListLines:
    #各行をカンマで分割し、変数代入
    items = dirListLine.split(',')
    rootPath = items[0]
    folderStructure = items[1]
    preservationDays = items[2]
    monthlyArchiveNumber = items[3]
    
    dirRenamer.rename(rootPath, folderStructure, preservationDays, monthlyArchiveNumber)

#for each dir do following

# for folder structure  = "root-folder-file"
# read all folders and sort by name oldest to newest
# dont add to list if folder starts with "[_"
# check all the files and if the newest is older than 14 days, rename to [_YYYY-MM-DD_HH-mm-ss_]_Original Folder Name

# for folder structure = "root-file"
