import os
import sys
import shutil
import timeKeeper
import statusKeeper
import logging
from datetime import datetime as dt
from datetime import timedelta as td

#環境設定
sys.dont_write_bytecode = True

#変数定義
datetimeToday = dt.now()
dateStamp = datetimeToday.strftime("%Y-%m-%d") #("%Y-%m-%d_%H-%M-%S")

def organize(items, lock, eachStatusIndex):
    #----------------変数定義----------------
    name = items[0] + "_" + items[1] + "_" + items[2] + "_" + str(eachStatusIndex)
    rootPath = items[3]
    folderStructure = items[4]
    preservationDays = items[5]

    #----------------log設定----------------
    logger = logging.getLogger("main").getChild("organizer_" + name)
    logger.setLevel(logging.DEBUG)

    #ルートログフォルダ生成
    logRootDir = os.path.join(os.getcwd(),"log_フォルダ別")
    if not os.path.isdir(logRootDir):
        os.mkdir(logRootDir)
        
    #ログフォルダ生成
    localLogFolder = os.path.join(logRootDir,name)
    if not os.path.isdir(localLogFolder):
        os.mkdir(localLogFolder)
    
    #ロガーフォーマット
    renameHandler = logging.FileHandler(os.path.join(localLogFolder,dateStamp+".log"))
    loggerFormat = logging.Formatter(
        '%(asctime)s:'
        '%(name)s:'
        '%(levelname)s:'
        '%(message)s'
    )
    renameHandler.setFormatter(loggerFormat)
    logger.addHandler(renameHandler)

    #----------------移動処理始動----------------
    logger.warning("移動開始:"+rootPath)

    #変数定義
    datetimeToday = dt.now()
    
    #事前確認
    if os.path.isdir(rootPath) == False:
        logger.error("移動中断_該当フォルダ無し")
        return
    
    #変数定義
    longtermPreservationDir = os.path.join(rootPath, "[_長期保存用フォルダ_]")

    #長期保存用フォルダと永久保存フォルダの有無チェック
    if os.path.isdir(longtermPreservationDir) == False:
        os.mkdir(longtermPreservationDir)
    
    #フォルダ構造が、root/サブフォルダ/ファイルとなっているパターン
    if folderStructure == "root-folder-file":

        lock.acquire()
        statusKeeper.eachStatus[eachStatusIndex][1] = "移動開始_フォルダ一覧取得中"
        lock.release()

        #フォルダ一覧取得（事前に時刻確認）
        if timeKeeper.checkIfOutofTime():
            logger.error("移動中断_アクセス許可時間外エラー")
            lock.acquire()
            statusKeeper.eachStatus[eachStatusIndex][1] = "移動中断_NASアクセス禁止時間帯"
            statusKeeper.eachStatus[eachStatusIndex][2] = -1
            lock.release()
            return
        else:
            dirListTemp = os.listdir(rootPath)
            dirList = [d for d in dirListTemp if os.path.isdir(os.path.join(rootPath,d))]
            folderCount = len(dirList)

        for dirIndex, dir in enumerate(dirList):
            #各フォルダで名前変更処理実行
            lock.acquire()
            statusKeeper.eachStatus[eachStatusIndex][1] = "フォルダ一覧取得完了_各フォルダ移動中("+str(dirIndex)+"/"+str(folderCount)+")"
            lock.release()

            #現在時刻とNASアクセス許可時間帯確認
            if timeKeeper.checkIfOutofTime():
                logger.error("移動中断_アクセス許可時間外エラー")
                return

            #特殊なフォルダは飛ばす
            if dir[0:2] == "[_":    
                continue

            #ファイル一覧取得（事前に時刻確認）
            if timeKeeper.checkIfOutofTime():
                logger.error("移動中断_アクセス許可時間外エラー")
                return
            else:
                dirFullPath = os.path.join(rootPath,dir)
                fileListTemp = os.listdir(dirFullPath)
                fileList = [f for f in fileListTemp if os.path.isfile(os.path.join(rootPath,dir,f))]
            
            #フォルダ内にファイルしかないことを確認
            if len(fileListTemp) != len(fileList):
                logger.error("移動中断_フォルダ構造エラー:"+dirFullPath + "内でフォルダ確認")
                continue

            #最新ファイルの日付取得
            lastestDate = "0000-00-00"
            latestMonth = ""
            latestDateWithin14Days = False
            for file in fileList:
                createdTime = os.path.getctime(os.path.join(rootPath,dir,file))
                strCreatedDate = format(dt.fromtimestamp(createdTime),"%Y-%m-%d")
                strCreatedMonth = format(dt.fromtimestamp(createdTime),"%Y-%m")
                if strCreatedDate > lastestDate:
                    lastestDate = strCreatedDate
                    latestMonth = strCreatedMonth
                    deltaDays = (datetimeToday - dt.fromtimestamp(createdTime)).days
                    if deltaDays < 14:
                        latestDateWithin14Days = True
            
            #長期保存フォルダ内の月別フォルダの有無チェック
            longtermPreservationMonthDir = os.path.join(longtermPreservationDir,latestMonth)
            if os.path.isdir(longtermPreservationMonthDir) == False:
                os.mkdir(longtermPreservationMonthDir)

            #フォルダ移動
            newDirFullPath = os.path.join(longtermPreservationMonthDir, dir)
            if latestDateWithin14Days == False:
                try:
                    os.rename(dirFullPath, newDirFullPath)
                    logger.info("フォルダ移動中:" + newDirFullPath)
                except FileExistsError:
                    logger.error("移動失敗:FileExistsError")

    logger.warning("移動終了:"+rootPath)

    #----------------削除処理始動----------------
    logger.warning("削除開始:"+rootPath)
    
    #安全の為、rootPathを長期保存用フォルダパスへ変更
    rootPath = os.path.join(rootPath, "[_長期保存用フォルダ_]")
    
    #事前確認
    if os.path.isdir(rootPath) == False:
        logger.error("削除中断_該当フォルダ無し")
        return

    #保存期間日数が適切か確認
    preservationDays = int(preservationDays)
    if ((preservationDays > 547) and (preservationDays < 7300)) == False:
        logger.error("削除中断_保存日数設定が 547日未満")
        return
    
    #変数定義 私の誕生日
    OldestPossibleFolderName = "1996-02"

    #保存限界の日付から削除不可能かつ最も古いフォルダ名取得
    preservationLimit = datetimeToday - td(days = int(preservationDays))
    preservationLimitFolderName = format(preservationLimit,"%Y-%m")

    logger.warning("削除開始:"+rootPath)

    lock.acquire()
    statusKeeper.eachStatus[eachStatusIndex][1] = "削除開始_フォルダ一覧取得中"
    lock.release()
    
    #長期保存用フォルダ内のフォルダ一覧取得(事前に時刻確認)
    if timeKeeper.checkIfOutofTime():
        logger.error("削除中断_アクセス許可時間外エラー")
        return
    else:
        monthlyFolderList = os.listdir(rootPath)
        monthlyDirCount = len(monthlyFolderList)

    for monthlyDirIndex, monthlyFolder in enumerate(monthlyFolderList):
        #保存限界より古いか確認
        if monthlyFolder >= preservationLimitFolderName:
            #保存限界より新しいか保存限界のフォルダはパス
            continue
        if monthlyFolder <= OldestPossibleFolderName:
            #私の誕生日より古いフォルダは意図しないフォルダの削除に繋がるのでパス
            continue
        
        #月別フォルダのパス取得
        monthlyFolderFullname = os.path.join(rootPath,monthlyFolder)

        #月別フォルダの削除開始
        logger.info("削除中:"+monthlyFolderFullname)

        #月別フォルダ内のフォルダ一覧取得(事前に時刻確認)
        if timeKeeper.checkIfOutofTime():
            logger.error("削除中断_アクセス許可時間外エラー")
            return
        else:
            dirListTemp = os.listdir(monthlyFolderFullname)
            dirList = [d for d in dirListTemp if os.path.isdir(os.path.join(rootPath,d))]
            dirCount = len(dirList)
        
        #月別フォルダ内のフォルダを一つずつ削除
        for dirIndex, dirName in enumerate(dirList):
            lock.acquire()
            statusKeeper.eachStatus[eachStatusIndex][1] = "各フォルダ削除中_月別フォルダ("+str(monthlyDirIndex)+"/"+str(monthlyDirCount)+")-月内フォルダ("+str(dirIndex)+"/"+str(dirCount)+")"
            lock.release()
            
            #フォルダ削除(事前に時刻確認)
            if timeKeeper.checkIfOutofTime():
                logger.error("削除中断_アクセス許可時間外エラー")
                return
            else:
                shutil.rmtree(os.path.join(monthlyFolderFullname,dirName))
        
        #月別フォルダ削除(事前に時刻確認)
        if timeKeeper.checkIfOutofTime():
            logger.error("削除中断_アクセス許可時間外エラー")
            return
        else:
            shutil.rmtree(monthlyFolderFullname)

    logger.warning("削除完了:"+rootPath)
    
    lock.acquire()
    statusKeeper.eachStatus[eachStatusIndex][1] = "フォルダ削除完了"
    statusKeeper.eachStatus[eachStatusIndex][2] = 1
    lock.release()

#----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")

    #dirList.csvを開いて、1行ずつ読み込み
    dirListPath = os.path.join(os.getcwd(), "dirList.csv")
    f = open(dirListPath, 'r', encoding="utf-8")
    dirListLines = f.readlines()[1:]

    for dirListLine in dirListLines:

        #各行をカンマで分割し、変数代入
        items = dirListLine.split(',')
        organize(items)
#----------------------------------動作確認用----------------------------------
