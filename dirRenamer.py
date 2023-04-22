import os
import csv
from datetime import datetime as dt

todaysdate = dt.now()
todaysdateStamp = todaysdate.strftime("%Y-%m-%d")

print(todaysdateStamp)