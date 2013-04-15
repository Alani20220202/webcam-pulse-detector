from lib.device import Camera
from lib.processors import findFacesAndPulses
from lib.interface import plotXY, imshow, waitKey,destroyWindow, moveWindow
import numpy as np      

class getPulseApp(object):
    """
    Finds faces in webcam stream & isolates foreheads.
    
    Then mean green-light intensity data is gathered from a detected forhead 
    over time and the detected person's pulse is estimated.
    """
    def __init__(self):
        #Imaging device
        self.camera = Camera(camera=0)
        self.w,self.h = 0,0
        #Containerized analysis of recieved image frames (an openMDAO assembly)
        #This assembly is designed to handle all image & signal analysis,
        #such as face detection, forehead isolation, time series collection,
        #heart-beat detection, etc.
        self.processor = findFacesAndPulses()
        
        #Init parameters for the cardiac data plot
        self.bpm_plot = False
        self.plot_title = "Cardiac info - raw signal, filtered signal, and PSD"
        
        #Maps keyboard controls to internal methods
        self.key_controls = {"s" : self.toggle_search,
                        "d" : self.toggle_display_plot}
        
    
    def toggle_search(self):
        """
        Toggles a lock on the processor's face detection component.
        Locking the forehead location in place improves data quality. 
        """
        state = self.processor.find_faces.toggle()
        print "face detection lock =",not state
    
    def toggle_display_plot(self):
        """
        Toggles the data display 
        """
        if self.bpm_plot:
            print "bpm plot disabled"
            self.bpm_plot = False
            destroyWindow(self.plot_title)
        else:
            print "bpm plot enabled"
            self.bpm_plot = True
            self.make_bpm_plot()
            moveWindow(self.plot_title, self.w,0)
    
    def make_bpm_plot(self):
        """
        Creates / updates the data display
        """
        plotXY([[self.processor.fft.times, self.processor.fft.samples],
            [self.processor.fft.even_times[4:-4], self.processor.heart.filtered[4:-4]],
                [self.processor.heart.freqs, self.processor.heart.fft]], 
               labels = [False, False, True],
               showmax = [False,False, "bpm"], 
               name = self.plot_title, 
               bg = self.processor.grab_faces.slices[0])
    
    def key_handler(self):    
        """
        Handle keypresses.
        A plotting or camera frame window must have focus for keypresses to be
        detected.
        """
        pressed = waitKey(10) & 255 #wait for keypress for 10 ms
        if pressed == 27: #exit program on 'esc'
            quit()
        for key in self.key_controls.keys():
            if chr(pressed) == key:
                self.key_controls[key]()
                
    def main_loop(self):
        """
        Single iteration of the application's main loop.
        """
        # Get current image frame from the camera
        frame = self.camera.get_frame()
        self.h,self.w,_c = frame.shape
        #display unaltered frame
        #imshow("Original",frame)
        
        #set current image frame to the processor's input
        self.processor.frame_in = frame
        #process the image frame
        self.processor.run()
        #collect the output frame for display
        output_frame = self.processor.frame_out
        
        #show the processed/annotated output frame
        imshow("Processed",output_frame)
        
        #create and/or update the raw data display
        if self.bpm_plot:
            self.make_bpm_plot()
        
        #handle any key presses
        self.key_handler()

if __name__ == "__main__":
    App = getPulseApp()
    while True:
        App.main_loop()
        
        