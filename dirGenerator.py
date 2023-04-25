import os
import sys
import random
import math
import time
from datetime import datetime as dt
from datetime import timedelta as td
from subprocess import call
import pywintypes, win32file, win32con

#環境設定
sys.dont_write_bytecode = True

#引数確認
nArgs = len(sys.argv)
emptyArgv = False
if nArgs == 1:
    emptyArgv = True

#日付取得
todaysdate = dt.now()
todaysdateStamp = todaysdate.strftime("%Y-%m-%d")

#パス生成
runningOS = "Windows"
rootDir = "C:/Users/Kazuk/Documents/2_Projects/VSCode/fileKeeperDirExample"
if emptyArgv:
    subrootDir = rootDir + "/dir1"
else:
    subrootDir = rootDir + "/dir" + sys.argv[1]

if os.path.isdir(rootDir) == False:
    print("rootDir does NOT exist.")
    exit()

if os.path.isdir(subrootDir) == False:
    os.mkdir(subrootDir)

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

for month in range(0, monthCount + 1):
    months.append(month)
    dirName = subrootDir + "/" + str(month)
    if os.path.isdir(dirName):
        print(dirName + " does exist")
    else:
        os.mkdir(dirName)
    
    for fileName in files:
        #ファイルパス定義
        filePath = os.path.join(dirName,fileName)

        if os.path.isfile(filePath) == False:
            print("File does NOT exitst")
            with open(dirName + "/" + fileName, "w") as f:
                f.write("New File Generated!")

        if os.path.isfile(filePath):
            print("File does exist:" + dirName+"/"+fileName)
            randomDays = math.floor(random.random()*30)
            newDate = todaysdate - td(days = (month * 1 + randomDays/30))

            if runningOS == "Mac":
                changeFileDateOnMac(filePath, newDate)
            #elif runningOS == "Windows":
                #changeFileDateOnWindows(filePath, newDate)

print("Hello")
time.sleep(1)
print("Bye")
