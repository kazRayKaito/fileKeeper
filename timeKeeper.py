import os
import sys
from datetime import datetime as dt
from datetime import timedelta as td

#環境設定
sys.dont_write_bytecode = True

#曜日別のNASへのアクセスが許可されている時間帯（設定）
allowedTimeHourList = [
    [0, 4],  #月：0時～4時まで可    (厳密には03:59:59.999999まで)
    [-1,-1], #火：不可
    [-1,-1], #水：不可
    [-1,-1], #木：不可
    [-1,-1], #金：不可
    [20,24], #土：20時～24時まで可  (厳密には23:59:59.999999まで)
    [0,24],  #日：0時～24時まで可   (厳密には23:59:59.999999まで)
]

def checkIfOutofTime(offsetHour = 0):
    #現在時刻取得
    currentTime = dt.now()

    #デバッグ用
    #if offsetHour != 0:
    #    currentTime = currentTime + td(hours = offsetHour)

    #曜日取得 [0:月曜日～6:日曜日]
    weekday = currentTime.weekday()

    #曜日別のNASアクセス許可時間取得
    allowedStartTime = allowedTimeHourList[weekday][0]
    allowedEndTime = allowedTimeHourList[weekday][1]

    #判定
    notAllowed = not ((currentTime.hour >= allowedStartTime) and (currentTime.hour < allowedEndTime))
    
    #デバッグ用
    #print(str(currentTime) + ":" + str(allowed))

    #デバッグ用に常時許可
    return False
    return notAllowed

 #----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")

    for hr in range(-100,100):
        checkIfOutofTime(hr)
#----------------------------------動作確認用----------------------------------
