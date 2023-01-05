import tkinter as tk
from tkinter.ttk import Frame, Notebook, Style, Treeview

from multiprocessing import freeze_support
import file_system

def main():
    root = tk.Tk()
    m = MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

class MainApplication(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master

        # ----------------------------- Definite Main Window -----------------------------
        self.master.title("EMME Helper")

        w = self.master.winfo_screenwidth()
        h = self.master.winfo_screenheight()
        self.master.geometry("960x1020+%d+%d" % ((w-960)/2, (h-1020)/2))

        self.master.grid_propagate(0)
        self.master.update()

        # ----------------------------- Definite Menu bar -----------------------------
        menu_bar = tk.Menu(self.master)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.do_nothing)
        file_menu.add_command(label="Open", command=self.do_nothing)
        file_menu.add_command(label="Save", command=self.do_nothing)
        file_menu.add_command(label="Save as...", command=self.do_nothing)
        file_menu.add_command(label="Close", command=self.do_nothing)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.do_nothing)
        edit_menu.add_command(label="Copy", command=self.do_nothing)
        edit_menu.add_command(label="Paste", command=self.do_nothing)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.master.config(menu=menu_bar)

        # ----------------------------- Definite Style -----------------------------
        style = Style()
        style.configure('TNotebook.Tab', foreground='dark blue')

        # ----------------------------- Definite Tabs -----------------------------
        tab_control = Notebook(self.master, name='main application tab control')
        tab1 = Frame(tab_control, name='main application tab1')
        tab_control.add(tab1, text='Zone Segmentation')
        tab_control.pack(expand=1, fill="both", padx=4)

        # ----------------------------- Definite Frame Wrapper -----------------------------
        wrapper1 = tk.LabelFrame(tab1, text=" File List ", name='main application wrapper1')
        wrapper2 = tk.LabelFrame(tab1, text=" File Data ", name="main application wrapper2")
        wrapper3 = tk.LabelFrame(tab1, text=" Search ")

        wrapper1.grid(row=0, padx=20, pady=10, sticky='we')
        wrapper2.grid(row=1, padx=20, pady=10, sticky='we')
        wrapper3.grid(row=2, padx=20, pady=10, sticky='we')

        # ----------------------------- Definite wrapper1 -----------------------------
        # 만약 파일 시스템만 불러오고 싶으면,
        # fs_list = file_system.FileSystem(wrapper1).wrapper1
        fs_list = file_system.FileSystem(wrapper1).wrapper2()
        fs_list.grid()

    def do_nothing(self):
        print("a")

if __name__ == "__main__":
    freeze_support()
    main()