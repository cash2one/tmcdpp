import time 
class CommonFunc:
    def get_current_day(self):
        return time.strftime("%Y-%m-%d",time.localtime(time.time()))

    def get_current_day_2(self):
        return time.strftime("%Y%m%d",time.localtime(time.time()))


