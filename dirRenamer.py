import os
from datetime import datetime as dt

def rename(rootPath, folderStructure, preservationDays, monthlyArchiveNumber):
    if folderStructure == "root-folder-file":
        #フォルダ構造が、root/サブフォルダ/ファイルとなっているパターン
        dirListTemp = os.listdir(rootPath)
        dirList = [d for d in dirListTemp if os.path.isdir(os.path.join(rootPath,d))]

        for dir in dirList:
            #各フォルダで名前変更処理実行
            if dir[0:2] == "[_":
                #処理実行済みフォルダは飛ばす
                continue
            else:
                fileListTemp = os.listdir(os.path.join(rootPath,dir))
                fileList = [f for f in fileListTemp if os.path.isfile(os.path.join(rootPath,dir,f))]
                for file in fileList:
                    createdTime = os.path.getctime(os.path.join(rootPath,dir,file))
                    strCreatedTime = format(dt.fromtimestamp(createdTime),"[_%Y-%m-%d_%H-%M-%S_]")
                    print(os.path.join(rootPath,dir,file) + ":" + strCreatedTime)


# check all the files and if the newest is older than 14 days, rename to [_YYYY-MM-DD_HH-mm-ss_]_Original Folder Name

# for folder structure = "root-file"
