import os
import sys
import shutil
import timeKeeper
from logging import getLogger
from datetime import datetime as dt
from datetime import timedelta as td

#環境設定
sys.dont_write_bytecode = True

#ロガー設定
logger = getLogger("main").getChild("remover")

#変数定義
datetimeToday = dt.now()

def remove(items):
    #引数分解
    rootPath = items[0]
    folderStructure = items[1]
    preservationDays = items[2]
    monthlyArchiveNumber = items[3]
    
    #安全の為、rootPathを長期保存用フォルダパスへ変更
    rootPath = os.path.join(rootPath, "[_長期保存用フォルダ_]")

    logger.warning("削除開始:"+rootPath)

    #NASアクセス許可時間帯確認
    if timeKeeper.checkIfOutofTime():
        logger.error("削除中断_アクセス許可時間外エラー")
        return

    #事前確認
    if os.path.isdir(rootPath) == False:
        logger.error("削除中断_該当フォルダ無し")
        return

    #フォルダ構造が、root/サブフォルダ/ファイルとなっているパターン
    if folderStructure == "root-folder-file":

        #変数定義 私の誕生日
        OldestPossibleFolderName = "1996-02"

        #保存期間日数が適切か確認
        preservationDays = int(preservationDays)
        if ((preservationDays > 547) and (preservationDays < 7300)) == False:
            logger.error("削除中断_保存日数設定が 547日未満")
            return

        #保存限界の日付から削除不可能かつ最も古いフォルダ名取得
        preservationLimit = datetimeToday - td(days = int(preservationDays))
        preservationLimitFolderName = format(preservationLimit,"%Y-%m")

        #長期保存用フォルダ内のフォルダ一覧取得
        monthlyFolderList = os.listdir(rootPath)

        for monthlyFolder in monthlyFolderList:
            #各フォルダで古いフォルダの削除実行
            
            #現在時刻とNASアクセス許可時間帯確認
            if timeKeeper.checkIfOutofTime():
                logger.error("削除中断_アクセス許可時間外エラー")
                return

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
                        logger.error("削除中断_アクセス許可時間外エラー")
                        return
                    
                    shutil.rmtree(os.path.join(monthlyFolderFullname,dirName))
                
                #空のフォルダ削除
                logger.warning("削除中:"+monthlyFolderFullname)
                shutil.rmtree(monthlyFolderFullname)

    logger.warning("削除完了:"+rootPath)

#----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")

    #dirList.csvを開いて、1行ずつ読み込み
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    f = open(dirListPath, 'r')
    dirListLines = f.readlines()[1:]

    for dirListLine in dirListLines:
        
        #各行をカンマで分割し、変数代入
        items = dirListLine.split(',')
        remove(items)
#----------------------------------動作確認用----------------------------------
