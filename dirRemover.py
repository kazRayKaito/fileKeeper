import os
import sys
import shutil
import timeKeeper
from datetime import datetime as dt
from datetime import timedelta as td

#環境設定
sys.dont_write_bytecode = True

#変数定義
datetimeToday = dt.now()

def remove(rootPath, folderStructure, preservationDays, monthlyArchiveNumber):
    #NASアクセス許可時間帯確認
    if timeKeeper.checkIfOutofTime():
        return
    
    #安全の為、rootPathを長期保存用フォルダパスへ変更
    rootPath = os.path.join(rootPath, "[_長期保存用フォルダ_]")

    #事前確認
    if os.path.isdir(rootPath) == False:
        print("rootPath does NOT exist.")
        return

    #フォルダ構造が、root/サブフォルダ/ファイルとなっているパターン
    if folderStructure == "root-folder-file":

        #変数定義 私の誕生日
        OldestPossibleFolderName = "1996-02"

        #保存期間日数が適切か確認
        preservationDays = int(preservationDays)
        if ((preservationDays > 547) and (preservationDays < 7300)) == False:
            print("preservationDays Invalid.")
            return

        #保存限界の日付から削除不可能かつ最も古いフォルダ名取得
        preservationLimit = datetimeToday - td(days = int(preservationDays))
        preservationLimitFolderName = format(preservationLimit,"%Y-%m")

        #長期保存用フォルダ内のフォルダ一覧取得
        monthlyFolderList = os.listdir(rootPath)

        for monthlyFolder in monthlyFolderList:

            #保存限界より古いか確認
            if (monthlyFolder > OldestPossibleFolderName) and (monthlyFolder < preservationLimitFolderName):
                
                #月別フォルダのパス取得
                monthlyFolderFullname = os.path.join(rootPath,monthlyFolder)
                
                #月別フォルダ内のフォルダ一覧取得
                dirList = os.listdir(monthlyFolderFullname)
                
                #各フォルダを一つずつ削除
                for dirName in dirList:

                    #現在時刻とNASアクセス許可時間帯確認
                    if timeKeeper.checkIfOutofTime():
                        return
                    else:
                        shutil.rmtree(os.path.join(monthlyFolderFullname,dirName))
                
                #空のフォルダ削除
                shutil.rmtree(monthlyFolderFullname)

#----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")

    rootDir = "C:\\Users\\Kazuk\\Documents\\2_Projects\\fileControl2"
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")

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
        
        remove(rootPath, folderStructure, preservationDays, monthlyArchiveNumber)
#----------------------------------動作確認用----------------------------------
