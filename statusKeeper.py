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
        self.eachStatus = []
        self.watchTime = watchTime
        self.lock = lock

        #ロガー設定
        self.logger = logging.getLogger("main").getChild("statusKeeper")

    def appendStatus(self, newStatus):
        self.eachStatus.append(newStatus)

    def updateStatus(self, statusIndex, message = None, newStatus = None):
        self.lock.acquire()
        if not message == None:
            self.eachStatus[statusIndex][1] = message
        if not newStatus == None:
            self.eachStatus[statusIndex][2] = newStatus    
        self.lock.release()

    def displayStatus(self):
        os.system('cls')
        allDone = True
        allClear = True
        for eachStatus in self.eachStatus:
            print(f"{eachStatus[0]}:{eachStatus[1]}")
            if eachStatus[2] == 0:
                allDone = False
            if eachStatus[2] != 1:
                allClear = False
        
        if allClear:
            print("完了：全て正常終了")
            return True
        
        if allDone:
            print("終了：一部異常終了")
            return True
        
        return False
    
    def checkIfOutofTime(self):
        #現在時刻取得
        if not self.watchTime:
            return False

        currentTime = dt.now()

        #デバッグ用
        #if offsetHour != 0:
        #    currentTime = currentTime + td(hours = offsetHour)

        #曜日取得 [0:月曜日～6:日曜日]
        weekday = currentTime.weekday()

        #曜日別のNASアクセス許可時間取得
        allowedStartTime = self.allowedTimeHourList[weekday][0]
        allowedEndTime = self.allowedTimeHourList[weekday][1]

        notAllowed = not ((currentTime.hour >= allowedStartTime) and (currentTime.hour < allowedEndTime))

        return notAllowed
    
 #----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")
#----------------------------------動作確認用----------------------------------
