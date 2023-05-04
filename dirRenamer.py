import os
import sys
import timeKeeper
import statusKeeper
import logging
from datetime import datetime as dt

#環境設定
sys.dont_write_bytecode = True

#変数定義
datetimeToday = dt.now()
dateStamp = datetimeToday.strftime("%Y-%m-%d") #("%Y-%m-%d_%H-%M-%S")

def rename(items, lock, eachStatusIndex):
    #引数分解
    name = items[0] + "_" + items[1] + "_" + items[2] + "_" + str(eachStatusIndex)
    rootPath = items[3]
    folderStructure = items[4]
    preservationDays = items[5]
    monthlyArchiveNumber = items[6]

    #log設定
    logger = logging.getLogger("main").getChild("renamer_" + name)
    logger.setLevel(logging.DEBUG)

    #ルートログフォルダ生成
    logRootDir = os.path.join(os.getcwd(),"log_フォルダ移動")
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

    logger.warning("移動開始:"+rootPath)

    #変数定義
    datetimeToday = dt.now()
    
    #事前確認
    if os.path.isdir(rootPath) == False:
        logger.error("移動中断_該当フォルダ無し")
        return
    
    #変数定義
    longtermPreservationDir = os.path.join(rootPath, "[_長期保存用フォルダ_]")
    permanentPreservationDir = os.path.join(rootPath, "[_恒久保存用フォルダ_]")

    #長期保存用フォルダと永久保存フォルダの有無チェック
    if os.path.isdir(longtermPreservationDir) == False:
        os.mkdir(longtermPreservationDir)

    if os.path.isdir(permanentPreservationDir) == False:
        os.mkdir(permanentPreservationDir)
    
    #フォルダ構造が、root/サブフォルダ/ファイルとなっているパターン
    if folderStructure == "root-folder-file":

        lock.acquire()
        statusKeeper.eachStatus[eachStatusIndex][1] = "移動開始_フォルダ一覧取得中"
        lock.release()

        #フォルダ一覧取得（事前に時刻確認）
        if timeKeeper.checkIfOutofTime():
            logger.error("移動中断_アクセス許可時間外エラー")
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
    logger.error("エラーテスト")
    
    lock.acquire()
    statusKeeper.eachStatus[eachStatusIndex][1] = "フォルダ移動完了"
    statusKeeper.eachStatus[eachStatusIndex][2] = 1
    lock.release()

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
        rename(items)
#----------------------------------動作確認用----------------------------------
