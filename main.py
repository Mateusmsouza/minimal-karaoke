from interface import *

if __name__ == "__main__":
    root = tk.Tk()
    app = KaraokePlayer(root)
    root.attributes("-fullscreen", True) 
    #root.geometry("600x400")
    root.mainloop()