from tkinter import *
from tkinter import filedialog

window = Tk()
window.title("Zone Segmentation")
window.geometry("640x400+200+200")
window.resizable(False, False)

window.filename = filedialog.askopenfilename(title = "Select file",filetypes = (("txt files","*.txt"), ("all files","*.*")))
file_name = window.filename
print(file_name)