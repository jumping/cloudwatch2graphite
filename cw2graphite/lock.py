#coding=utf-8

import fcntl  
  
class ProcessLock(object):  
  
    __lockfd = None  
 
    @staticmethod  
    def lock():  
            ProcessLock.__lockfd = open(__file__, 'a+')  
            fcntl.flock(ProcessLock.__lockfd, fcntl.LOCK_EX)  
 
    @staticmethod  
    def unlock():  
            fcntl.flock(ProcessLock.__lockfd, fcntl.LOCK_UN) 
