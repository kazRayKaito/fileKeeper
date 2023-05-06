import sys

#環境設定
sys.dont_write_bytecode = True

class robot():
    def __init__(self,data):
        self.data = data
    
    def changeData(self,newData):
        self.data = newData
    
    def printData(self):
        print(self.data)


class human():
    def __init__(self,name,robot):
        self.name = name
        self.robot = robot
    
    def sayName(self):
        print(self.name)
    
    def changeName(self,newName):
        self.name = newName
    
    def writedata(self):
        self.robot.changeData(self.name)

def changeHisName(human):
    human.changeName("Ray")

def initialize():
    global eachStatus
    eachStatus = []
    
 #----------------------------------動作確認用----------------------------------
if __name__ == "__main__":
    print("running as main")
    ourbot = robot("empty")
    kazuki = human("Kazuki", ourbot)
    lily = human("Lily", ourbot)

    print("")
    print("ourbot print data")
    ourbot.printData()

    print("")
    print("Kaz changes data")
    kazuki.writedata()

    print("")
    print("ourbot print data")
    ourbot.printData()

    print("")
    print("Lily changes data")
    lily.writedata()

    print("")
    print("ourbot print data")
    ourbot.printData()
    print(kazuki.robot.data)
    print(lily.robot.data)
#----------------------------------動作確認用----------------------------------
