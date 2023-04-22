import os
from datetime import datetime as dt
from datetime import timedelta as td
from subprocess import call

todaysdate = dt.now()
todaysdateStamp = todaysdate.strftime("%Y-%m-%d")

rootDir = "/Volumes/raySSD2T/Data/rootFolder"

monthCount = 30
months = []

files = ["fileA.txt", "fileB.txt", "fileC.txt"]

for month in range(1, monthCount + 1):
    months.append(month)
    dirName = rootDir + "/" + str(month)
    if os.path.isdir(dirName):
        print(dirName + " does exist")
    else:
        os.mkdir(dirName)
    
    for fileName in files:
        if os.path.isfile(dirName + "/" + fileName):
            print("File does exist at " + fileName)
            olddate = todaysdate - td(days = month * 30)
            print(olddate.timetuple())
            print(olddate.timetuple().tm_year)
            print(str(olddate.timetuple().tm_mon).zfill(2))
            print(str(olddate.timetuple().tm_mday).zfill(2))
            dateString =  str(olddate.timetuple().tm_mon).zfill(2) + "/" + str(olddate.timetuple().tm_mday).zfill(2) + "/" + str(olddate.timetuple().tm_year)
            command = 'SetFile -d ' + dateString + ' 00:00:00 ' + dirName + "/" + fileName
            call(command, shell=True)
        else:
            print("File does NOT exitst")
            with open(dirName + "/" + fileName, "w") as f:
                f.write("New File Generated!")

print("Hello")
