from logging import root
from tkinter import DISABLED, Button,Canvas,Tk
from tkinter import messagebox
from turtle import bgcolor
from PIL import Image,ImageTk
from os import system
from threading import Thread
import tkinter.font as font
from voiceAssistant import voiceAssistant as va

root=Tk()
root.title("Navigation")
root.geometry("1920x1080")
canvas1 = Canvas( root, width = 1920,height = 1080)
canvas1.pack(fill = "both", expand = True)
img=Image.open("bg.jpg")
resized_image= img.resize((1920,1080), Image.ANTIALIAS)
bg=ImageTk.PhotoImage(resized_image)
canvas1.create_image( 0, 0, image = bg,anchor = "nw")

f = open("voice.txt", "w")
f.write("")
f.close()
f = open("state.txt", "w")
f.write("")
f.close()

def run_app():
    canvas1.itemconfig(2,state="hidden")
    try:
         system("sub.bat")
    except Exception as e:
        print(str(e))
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        exit(0)
buttonFont = font.Font(family='Helvetica', size=16, weight='bold')
button1 =Button( root, text = "Let's Navigate",command=Thread(target=run_app).start,bg='#00022b',fg='white',font=buttonFont)
button1_canvas = canvas1.create_window( 880, 350,anchor = "nw",window = button1)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.state('zoomed')
root.mainloop()