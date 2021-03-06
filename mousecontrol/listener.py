
import numpy as np
import time
import itertools
from PIL import Image
from pathlib import Path

import win32gui
import win32api




class MouseMoveListener:
    def __init__(self):
        
        self.width,self.height = self.get_width_height()



    def get_width_height(self):
        width,height = win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1)
        return width,height


    def get_mouse_pos(self):
        _, _, (x,y) = win32gui.GetCursorInfo()
        return x,y

    def pad_mouse_pos(self,x,y,pad = 10):
        x_range = lambda x : list(range(max([0,x-pad]),min([self.width,x+pad])))
        y_range = lambda y : list(range(max([0,y-pad]),min([self.height,y+pad])))
        arr_range = lambda x,y : np.array(list(itertools.product(x_range(x),y_range(y))))
        arr = arr_range(x,y)
        return arr[:,0],arr[:,1]



    def start_capture(self):
        capture = np.zeros((self.width,self.height))
        return capture


    def _prepare_img(self,capture,resize = None):
        img = Image.fromarray(np.uint8(capture.T*255))
        if resize is not None:
            assert len(resize) == 2
            img = img.resize(resize)
        return img



    def listen(self,duration: int = 8*3600,pad: int = 10,max_stop: int = 1,save: str = None,resize: tuple = (100,100)):

        capture = self.start_capture()
        captures = []
        
        s = time.time()
        i = 1

        # Save in folder if precised
        if save is not None:
            folder = Path(save)
            folder.mkdir(exist_ok = True)
        
        # Prepare triggers
        old_record = False
        record = True
        stop_duration = None
        print("Start recording")
        
        # Main loop
        while time.time() - s < duration:

            t = time.time()

            # Get mouse and pad around position
            x,y = self.get_mouse_pos()
            x_arr,y_arr = self.pad_mouse_pos(x,y,pad)

            # Append to the array
            capture[x_arr,y_arr] = 1
            
            if i > 1:
                
                # If stops moving
                if (old_x,old_y) == (x,y):

                    # Starts counting stop
                    if stop_duration is None:
                        stop_duration = 0
                        stopped_at = t
                    # Continues counting stop
                    else:
                        stop_duration = t - stopped_at
                    
                    # Stop recording if stop is more than the threshold
                    if stop_duration > max_stop:
                        record = False
                
                # Resume moving
                else:
                    stop_duration = None
                    record = True
                    
                # Triggers when re-starts 
                if (old_record,record) == (False,True):
                    print("Start recording")
                    capture = self.start_capture()

                elif (old_record,record) == (True,False):
                    print("... Stop recording")
                    captures.append(capture)

                    if save is not None:
                        img = self._prepare_img(capture,resize)
                        img_name = f"{int(time.time())}.png"
                        img.save(folder / img_name)
            
            old_x,old_y = (x,y)
            old_record = record
            old_t = t
            
            i += 1
            
        return captures