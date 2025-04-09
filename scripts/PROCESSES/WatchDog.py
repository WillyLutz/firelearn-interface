import threading
import multiprocessing
import time
from threading import Thread

from scripts.PROCESSES.FileProcessor import FileProcess
from scripts.PROCESSES.SpikeDetector import SpikeDetectorProcess

import logging
logger = logging.getLogger("__WatchDog__")
class WatchDog(Thread):
    def __init__(self, prisoners: list[FileProcess] |
                                  list[SpikeDetectorProcess],
                 watch_time=10, **kwargs):
        super().__init__(**kwargs)
        self.daemon = True
        self.prisoners = prisoners
        self.watch_time = watch_time  # time interval in seconds at which the thread will look after the prisoner threads
        self._stop_event = threading.Event()
    
    def watching(self):
        return True if not self.stopped() else False
    
    def stop(self):
        logger.info("Stopping prisoners")
        alive_prisoners = [p for p in self.prisoners if p.is_alive()]
        for prisoner in alive_prisoners:
            prisoner.stop()
        
        logger.info("Stopping watch dog")
        self._stop_event.set()
    
    def stopped(self):
        return self._stop_event.is_set()
    
    def run(self):
        while not self.stopped():
            alive_prisoners = [p.name for p in self.prisoners if p.is_alive()]
            logger.info(f"Alive prisoners {alive_prisoners}")
            if not alive_prisoners:
                self.stop()
                
            time.sleep(self.watch_time)