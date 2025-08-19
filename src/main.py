from tkinter import *
import frame as fm

class MainW(Tk):

    def __init__(self, parent, width, height, title_str):
        Tk.__init__(self, parent)
        self.parent = parent
        self.width =width
        self.height = height
        self.title_str = title_str     
        self.setupWindow()
        
    # Sets up window size and icons
    def setupWindow(self):
        self.geometry(f"{self.width}x{self.height}")
        self.title(f'{self.title_str}')
        self.iconbitmap("Simulation-Software\\resources\\umass_logo.ico")



if __name__=="__main__":
    app = MainW(None, 800, 600, "Settting up main app")
    
    app.mainloop()