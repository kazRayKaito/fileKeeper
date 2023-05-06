import os
import sys
import shutil
import statusKeeper
import logging
from datetime import datetime as dt
from datetime import timedelta as td

#環境設定
sys.dont_write_bytecode = True



class organizer():
    def __init__(self, name, rootPath, folderStructure, preservationDays, preservationStructure, eachStatusIndex, sk: statusKeeper.statusKeeper):
        #----------------変数定義----------------
        self.name = name
        self.rootPath = rootPath
        self.folderStructure = folderStructure
        self.preservationDays = preservationDays
        self.eachStatusIndex = eachStatusIndex
        self.preservationStructure = preservationStructure
        self.sk = sk

        self.datetimeToday = dt.now()
        self.longtermPreservationDir = os.path.join(self.rootPath, "[_長期保存用フォルダ_]")

        #logger生成
        self.renameLogger = self.setupLogger(f"renamer_{self.name}","ログ_フォルダ移動履歴")
        self.removeLogger = self.setupLogger(f"remover_{self.name}","ログ_フォルダ削除履歴")
    
    def setupLogger(self, logName, folderName):
        #----------------log設定----------------
        logger = logging.getLogger("main").getChild(logName)
        logger.setLevel(logging.INFO)

        #ルートログフォルダ生成
        logRootDir = os.path.join(os.getcwd(),folderName)
        if not os.path.isdir(logRootDir):
            os.mkdir(logRootDir)
            
        #ログフォルダ生成
        localLogFolder = os.path.join(logRootDir,self.name)
        if not os.path.isdir(localLogFolder):
            os.mkdir(localLogFolder)
        
        #ロガーフォーマット#変数定義
        dateStamp = self.datetimeToday.strftime("%Y-%m-%d")
        handler = logging.FileHandler(os.path.join(localLogFolder,dateStamp+".log"))
        loggerFormat = logging.Formatter(
            '%(asctime)s:'
            '%(name)s:'
            '%(levelname)s:'
            '%(message)s'
        )
        handler.setFormatter(loggerFormat)
        logger.addHandler(handler)

        return logger
    
    def updateStatus(self, msg = None, ns = None): self.sk.updateStatus(self.eachStatusIndex, msg, ns)
    def checkStatusAlive(self): return self.sk.checkStatus(self.eachStatusIndex) == 0

    def listdir(self, dirPath, logger: logging.Logger):
        #フォルダ一覧取得（事前に時刻確認）
        if self.sk.checkIfOutofTime():
            logger.error("移動中断_アクセス許可時間外エラー")
            self.updateStatus("移動中断_NASアクセス禁止時間帯", -1)
        else:
            return os.listdir(dirPath)
        
    def isdir(self, dirPath):
        #フォルダ有無確認
        if os.path.isdir(dirPath) == False:
            self.renameLogger.error("移動中断_該当フォルダ無し")
            self.updateStatus("移動中断_該当フォルダ無し", -1)

    def getLatestDateinDir(self, dirPath):
        #ファイル/フォルダ一覧取得
        dirListTemp = self.listdir(dirPath, self.renameLogger)
        if not self.checkStatusAlive(): return
        if self.latestDateWithin14Days: return

        fileList = [f for f in dirListTemp if os.path.isfile(os.path.join(dirPath,f))]
        dirList = [d for d in dirListTemp if os.path.isdir(os.path.join(dirPath,d))]

        #最新ファイルの日付取得
        for file in fileList:
            createdTime = os.path.getctime(os.path.join(dirPath,file))
            strCreatedDate = format(dt.fromtimestamp(createdTime),"%Y-%m-%d")
            if strCreatedDate > self.latestDate:
                self.latestDate = strCreatedDate
                deltaDays = (self.datetimeToday - dt.fromtimestamp(createdTime)).days
                if deltaDays < 14:
                    self.latestDateWithin14Days = True
                    return
                
        for dir in dirList:
            self.getLatestDateinDir(os.path.join(dirPath,dir))
    
    def moveDir(self, moveFromDir, dir):
        #保存先取得（長期保存）
        latestMonth = self.latestDate[0:7]
        monthDir = os.path.join(self.longtermPreservationDir,latestMonth)
        dateDir = os.path.join(monthDir,self.latestDate)

        #保存先フォルダの有無チェック
        if os.path.isdir(monthDir) == False:
            os.mkdir(monthDir)
        
        if self.folderStructure == "month":
            targetDir = monthDir
        else:
            targetDir = dateDir
            if os.path.isdir(targetDir) == False:
                os.mkdir(targetDir)

        #フォルダ移動
        newDirFullPath = os.path.join(targetDir, dir)
        try:
            self.renameLogger.info("フォルダ移動中:" + newDirFullPath)
            os.rename(moveFromDir, newDirFullPath)
        except FileExistsError:
            self.renameLogger.error("移動失敗:FileExistsError")

    def rename(self):
        
        # 各フォルダでiterate
        #   日付取得（フォルダ内の全ファイル確認）
        #   転送先確認(長期保存用フォルダの構造からめて)
        #   フォルダごと転送;
        self.renameLogger.warning("移動開始:"+self.rootPath)

        #変数定義
        
        #事前に rootPath の有無確認
        self.isdir(self.rootPath)
        if not self.checkStatusAlive(): return

        #長期保存用フォルダの有無チェック
        if os.path.isdir(self.longtermPreservationDir) == False:
            os.mkdir(self.longtermPreservationDir)

        #フォルダ一覧取得
        self.updateStatus("移動開始_フォルダー一覧取得中")
        dirListTemp = self.listdir(self.rootPath, self.renameLogger)
        if not self.checkStatusAlive(): return

        dirList = [d for d in dirListTemp if os.path.isdir(os.path.join(self.rootPath,d))]
        folderCount = len(dirList)

        for dirIndex, dir in enumerate(dirList):
            #各フォルダで名前変更処理実行
            self.updateStatus("フォルダ一覧取得完了_各フォルダ移動中("+str(dirIndex)+"/"+str(folderCount)+")")

            #特殊なフォルダは飛ばす
            if dir[0:2] == "[_":    
                continue

            #フォルダ内の最も新しいファイルの日付取得
            dirFullPath = os.path.join(self.rootPath,dir)
            self.latestDate = "0000-00-00"
            self.latestDateWithin14Days = False
            self.getLatestDateinDir(dirFullPath)
            if not self.checkStatusAlive(): return
            if self.latestDateWithin14Days: continue

            self.moveDir(dirFullPath, dir)

        self.renameLogger.warning("移動終了:"+self.rootPath)

    def remove(self):
        self.removeLogger.warning("削除開始:"+self.rootPath)
        
        #安全の為、rootPathを長期保存用フォルダパスへ変更
        rootPath = os.path.join(self.rootPath, "[_長期保存用フォルダ_]")
        
        #事前確認
        if os.path.isdir(rootPath) == False:
            self.removeLogger.error("削除中断_該当フォルダ無し")
            self.updateStatus("削除中断_該当フォルダ無し", -1)
            return

        #保存期間日数が適切か確認
        preservationDays = int(self.preservationDays)
        if ((preservationDays > 547) and (preservationDays < 7300)) == False:
            self.removeLogger.error("削除中断_保存日数設定が 547日未満")
            self.updateStatus("削除中断_保存日数設定が547日未満", -1)
            return
        
        #変数定義 私の誕生日
        OldestPossibleFolderName = "1996-02"

        #保存限界の日付から削除不可能かつ最も古いフォルダ名取得
        preservationLimit = self.datetimeToday - td(days = preservationDays)
        preservationLimitFolderName = format(preservationLimit,"%Y-%m")
        
        #長期保存用フォルダ内のフォルダ一覧取得(事前に時刻確認)
        self.updateStatus("削除開始_フォルダ一覧取得中")
        monthlyFolderList = self.listdir(rootPath, self.removeLogger)
        if not self.checkStatusAlive(): return

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
            self.removeLogger.info("削除中:"+monthlyFolderFullname)


            #月別フォルダ内のフォルダ一覧取得(事前に時刻確認)
            dirListTemp = self.listdir(monthlyFolderFullname, self.removeLogger)
            if not self.checkStatusAlive(): return

            dirList = [d for d in dirListTemp if os.path.isdir(os.path.join(rootPath,d))]
            dirCount = len(dirList)
            
            #月別フォルダ内のフォルダを一つずつ削除
            for dirIndex, dirName in enumerate(dirList):
                self.updateStatus("各フォルダ削除中_月別フォルダ("+str(monthlyDirIndex)+"/"+str(monthlyDirCount)+")-月内フォルダ("+str(dirIndex)+"/"+str(dirCount)+")")
                
                #フォルダ削除(事前に時刻確認)
                if self.sk.checkIfOutofTime():
                    self.removeLogger.error("削除中断_アクセス許可時間外エラー")
                    self.updateStatus("移動中断_NASアクセス禁止時間帯", -1)
                    return
                else:
                    shutil.rmtree(os.path.join(monthlyFolderFullname,dirName))
            
            #月別フォルダ削除(事前に時刻確認)
            if self.sk.checkIfOutofTime():
                self.removeLogger.error("削除中断_アクセス許可時間外エラー")
                self.updateStatus("移動中断_NASアクセス禁止時間帯", -1)
                return
            else:
                shutil.rmtree(monthlyFolderFullname)

        self.removeLogger.warning("削除完了:"+rootPath)

    def organize(self):
        self.rename()
        if not self.checkStatusAlive(): return

        self.remove()
        if not self.checkStatusAlive(): return
        
        self.updateStatus("処理完了", 1)

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
#----------------------------------動作確認用----------------------------------
