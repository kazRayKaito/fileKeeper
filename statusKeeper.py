import os
import sys
import logging
import threading
from datetime import datetime as dt

#環境設定
sys.dont_write_bytecode = True

class statusKeeper():
    allowedTimeHourList = [
        [ 0, 4], #月：0時～4時まで可    (厳密には03:59:59.999999まで)
        [-1,-1], #火：不可
        [-1,-1], #水：不可
        [-1,-1], #木：不可
        [-1,-1], #金：不可
        [20,24], #土：20時～24時まで可  (厳密には23:59:59.999999まで)
        [ 0,24], #日：0時～24時まで可   (厳密には23:59:59.999999まで)
    ]
    def __init__(self, lock: threading.Lock, watchTime = True):
        #変数定義
        self.eachStatus = [] #(name, message, status(0:処理中,1:正常終了,-1:異常終了))
        self.watchTime = watchTime #真ならNASアクセス許可時間帯を確認
        self.lock = lock #マルチスレッド用

        #ロガー設定
        self.logger = logging.getLogger("main").getChild("statusKeeper")

    def appendStatus(self, newStatus):
        newStatus.append("")
        self.eachStatus.append(newStatus)

    def updateStatus(self, statusIndex, message = None, newStatus = None):
        self.lock.acquire()
        if not message == None:
            self.eachStatus[statusIndex][1] = message
        if not newStatus == None:
            self.eachStatus[statusIndex][2] = newStatus    
        self.lock.release()

    def checkStatus(self, statusIndex): return self.eachStatus[statusIndex][2]

    def displayStatus(self):
        os.system('cls')
        allDone = True
        allClear = True
        printLinesData = []
        gapLength = 0
        for eachStatus in self.eachStatus:
            if eachStatus[2] == 0:
                allDone = False
            if eachStatus[2] != 1:
                allClear = False

        for eachStatus in self.eachStatus:
            if allDone or allClear or eachStatus[2] != 0 and eachStatus[2] != 1:
                printLinesData.append([eachStatus[0],eachStatus[1]])
                gapLength = max(gapLength, len(eachStatus[0][2]))
        
        printLinesData.reverse()

        firstLayer = [True, True]
        gapLength += 1

        printLines = []
        for lineIndex, printLineData in enumerate(printLinesData):
            if firstLayer[0]:
                if firstLayer[1]:
                    firstLayer[1] = False
                    printLines.append("    └─{name:<{length}}:{status}".format(name = printLineData[0][2], length = gapLength, status = printLineData[1]))
                else:
                    printLines.append("    ├─{name:<{length}}:{status}".format(name = printLineData[0][2], length = gapLength, status = printLineData[1]))
            else:
                if firstLayer[1]:
                    firstLayer[1] = False
                    printLines.append(" │  └─{name:<{length}}:{status}".format(name = printLineData[0][2], length = gapLength, status = printLineData[1]))
                else:
                    printLines.append(" │  ├─{name:<{length}}:{status}".format(name = printLineData[0][2], length = gapLength, status = printLineData[1]))
            if lineIndex == len(printLinesData)-1:
                #最上層
                if firstLayer[0]:
                    printLines.append(f" └─{printLineData[0][1]}")
                    printLines.append(f"{printLineData[0][0]}")
                else:
                    printLines.append(f" ├─{printLineData[0][1]}")
                    printLines.append(f"{printLineData[0][0]}")
            elif printLineData[0][1] != printLinesData[lineIndex + 1][0][1]:
                #3列目最上層
                firstLayer[1] = True
                if firstLayer[0]:
                    #2列目最下層
                    firstLayer[0] = False
                    printLines.append(f" └─{printLineData[0][1]}")
                else:
                    printLines.append(f" ├─{printLineData[0][1]}")
                if printLineData[0][0] != printLinesData[lineIndex + 1][0][0]:
                    printLines.append(f"{printLineData[0][0]}")
                    printLines.append("")
                    firstLayer[0] = True
                else:
                    printLines.append(" │")

        printLines.reverse()

        for printLine in printLines:
            print(printLine)
        
        if allClear:
            print("完了：全て正常終了")
            return True
        
        if allDone:
            print("終了：一部異常終了")
            return True
        
        return False
    
    def checkIfOutofTime(self):
        if not self.watchTime:
            return False

        #現在時刻と曜日取得 [0:月曜日～6:日曜日]
        currentTime = dt.now()
        weekday = currentTime.weekday()

        #曜日別のNASアクセス許可時間取得
        allowedStartTime = self.allowedTimeHourList[weekday][0]
        allowedEndTime = self.allowedTimeHourList[weekday][1]

        return not ((currentTime.hour >= allowedStartTime) and (currentTime.hour < allowedEndTime))
    
 #----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")
#----------------------------------動作確認用----------------------------------
