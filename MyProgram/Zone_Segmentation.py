from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
from pandas import read_csv, DataFrame
from numpy import divide
from re import split


class MainWindow(object):
    def __init__(self, master):
        self.master = master

        # ----------------------------- Definite Main Window -----------------------------
        self.master.title("EMME Helper")
        self.master.geometry("1000x300+100+100")
        self.master.grid_propagate(0)
        # ----------------------------- Definite Menu bar -----------------------------
        self.menu_bar = Menu(self.master)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.do_nothing)
        self.file_menu.add_command(label="Open", command=self.do_nothing)
        self.file_menu.add_command(label="Save", command=self.do_nothing)
        self.file_menu.add_command(label="Save as...", command=self.do_nothing)
        self.file_menu.add_command(label="Close", command=self.do_nothing)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Undo", command=self.do_nothing)
        self.edit_menu.add_command(label="Copy", command=self.do_nothing)
        self.edit_menu.add_command(label="Paste", command=self.do_nothing)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Help", command=self.do_nothing)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.master.config(menu=self.menu_bar)
        # ----------------------------- Definite Tabs -----------------------------
        tab_control = ttk.Notebook(self.master)
        tab1 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Zone Segmentation')
        tab_control.pack(expand=1, fill="both")
        # ----------------------------- Declare Frames -----------------------------
        self.frame0 = Frame(tab1)
        self.frame0.pack()

        self.frame1 = LabelFrame(self.frame0, text=" Input Files ", height=80, width=480)
        self.frame1.grid(row=0, column=0, padx=8, pady=4)
        self.frame1.grid_propagate(0)

        self.frame2 = LabelFrame(self.frame0, text=" Configurations ", height=80, width=480)
        self.frame2.grid(row=1, column=0, padx=8, pady=4)
        self.frame2.grid_propagate(0)

        self.frame3 = LabelFrame(self.frame0, text=" Buttons ", height=80, width=480)
        self.frame3.grid(row=2, column=0, padx=8, pady=4)
        self.frame3.grid_propagate(0)

        self.frame4 = LabelFrame(self.frame0, text=" Messages ", height=252, width=480)
        self.frame4.grid(row=0, rowspan=3, column=1, padx=8, pady=4)
        self.frame4.grid_propagate(0)
        # ----------------------------- Declare Variables -----------------------------
        self.seg_num_sv = StringVar()
        self.target_zone_sv = StringVar()
        self.data_2 = DataFrame
        self.data_3 = DataFrame
        # ------------------------------------------ Frame 1 ------------------------------------------
        # --------------- Declare buttons ---------------
        self.browse_infile_button = Button(self.frame1,
                                           text=" Browse .in file ", command=self.browse_button_in)
        self.browse_infile_button.grid(sticky=W)

        self.browse_popfile_button = Button(self.frame1,
                                            text=" Browse pop file ", command=self.browse_button_pop)
        self.browse_popfile_button.grid(sticky=W)
        # --------------- Declare labels ---------------
        self.infile_label = Label(self.frame1)
        self.infile_label.grid(row=0, column=1)

        self.popfile_label = Label(self.frame1)
        self.popfile_label.grid(row=1, column=1)
        # ------------------------------------------ Frame 2 ------------------------------------------
        # --------------- Declare labels ---------------
        self.target_zone_msg = Label(self.frame2, text=" Input Target zone ")
        self.target_zone_msg.grid(row=0, column=0, sticky=W)

        self.seg_num_msg = Label(self.frame2, text=" Input Expected segmentation ")
        self.seg_num_msg.grid(row=1, column=0, sticky=W)
        # --------------- Declare entries ---------------
        self.entry_target_zone = Entry(self.frame2, textvariable=self.target_zone_sv)
        self.entry_target_zone.grid(row=0, column=1)

        self.entry_seg_num = Entry(self.frame2, textvariable=self.seg_num_sv)
        self.entry_seg_num.grid(row=1, column=1)
        # ------------------------------------------ Frame 3 ------------------------------------------
        # --------------- Declare buttons ---------------
        self.save_button = Button(self.frame3, text=" Save as... ", command=self.save)
        self.save_button.grid(row=0, column=0, sticky=W)

        self.run_button = Button(self.frame3, text=" RUN ", command=self.run)
        self.run_button.grid(row=1, column=0, sticky=W)
        # --------------- Declare labels ---------------
        self.save_dir_msg = Label(self.frame3)
        self.save_dir_msg.grid(row=0, column=1)
        # ------------------------------------------ Frame 4 ------------------------------------------
        # --------------- Declare texts ---------------
        self.text_data = scrolledtext.ScrolledText(self.frame4, height=17, width=60)
        self.text_data.grid(padx=8, pady=4)

    def do_nothing(self):
        print ("a")

    def browse_button_in(self):
        filename_in = filedialog.askopenfilename(title="Select file")
        if filename_in[-3:] == '.in':
            self.data = read_csv(filename_in, skiprows=2, header=None, names=['O', 'D', 'Traffic'])
            self.text_data.insert(CURRENT, "선택한 .in 파일 경로:" + filename_in +
                                  "\n\n----------------------------------\n\n")
            self.text_data.see("end")
            self.infile_label.config(text=filename_in)
            self.show_data()
        else:
            raise ValueError('Choose right file')

    def browse_button_pop(self):
        self.filename_pop = filedialog.askopenfilename(title="Select file")
        self.a = read_csv(self.filename_pop, header=None, delimiter='\t| ', engine='python').values[0]
        self.data_pop = self.a
        self.text_data.insert(END, "선택한 세분화 기준 파일 경로:" + self.filename_pop +
                              "\n\n----------------------------------\n\n")
        self.text_data.see("end")
        self.popfile_label.config(text=self.filename_pop)

    def show_data(self):
        self.text_data.insert(END, "[Head of Data]\n" + self.data.head().to_string() + "\n\n"
                              + "[Tail of Data]\n" + self.data.tail().to_string()
                              + "\n\n----------------------------------\n\n")

    def save(self):
        self.name = filedialog.asksaveasfilename(defaultextension=".txt")
        self.save_dir_msg.config(text=self.name)

    def run(self):
        self.data_pop = self.a

        self.text_data.insert(END, ". . . 존 세분화를 시작합니다 . . .\n\n")
        self.text_data.see("end")
        col = [int(i) for i in self.data['D'].unique()]
        row = [int(i) for i in self.data['O'].unique()]

        self.data_2 = DataFrame(columns=col, index=row)
        n = 0
        for i in col:
            for j in row:
                self.data_2[i][j] = self.data['Traffic'][n]
                n = n + 1

        self.data_3 = self.data_2.copy(deep=False)
        self.data_3.loc['Total', :] = self.data_3.sum(axis=0) # Total sum per column:
        self.data_3.loc[:, 'Total'] = self.data_3.sum(axis=1) # Total sum per row:

        self.seg_num = int(self.seg_num_sv.get())  # get the text from entry
        self.target_zone = int(self.target_zone_sv.get())

        if len(self.data_pop) != self.seg_num:
            self.popup()
            self.data_pop = self.entry_value()

        self.segmentation()

    def popup(self):
        self.w=PopUpWindow(self.master)
        self.run_button["state"] = "disabled"
        self.master.wait_window(self.w.top)
        self.run_button["state"] = "normal"

    def entry_value(self):
        return self.w.new_data_pop

    def segmentation(self):
        seg_zone_pop_ratio = divide(self.data_pop, sum(self.data_pop))
        for num in range(len(seg_zone_pop_ratio)):
            print("Population ratio for segmenting zone %s" % str(max(self.data_2.index) + 1 + num),
                  ": {:.2%}".format(seg_zone_pop_ratio[num]))
            self.text_data.insert(END, "존 %s의 인구(세분화 기준) 비율" %
                                  str(max(self.data_2.index) + 1 + num)+
                                  ": {:.2%}".format(seg_zone_pop_ratio[num])+"\n")
            self.text_data.see("end")
        n = 0
        for i in range(max(self.data_2.index) + 1, max(self.data_2.index) + self.seg_num + 1):
            self.data_2.loc[i] = self.data_2.loc[self.target_zone] * seg_zone_pop_ratio[n]
            self.data_2.loc[:, i] = self.data_2.loc[:, self.target_zone] * seg_zone_pop_ratio[n]
            n = n + 1

        self.data_2.loc[self.target_zone] = 0
        self.data_2.loc[:, self.target_zone] = 0
        self.data_2 = self.data_2.astype('float64').round(2)
        data_4 = self.data_2.copy(deep=False)
        data_4.loc['Total', :] = data_4.sum(axis=0)
        data_4.loc[:, 'Total'] = data_4.sum(axis=1)
        judge_1 = abs(self.data_3['Total']['Total'] / data_4['Total']['Total'])
        if 0.9999 < judge_1 < 1.0001:
            print("\nZone segmentation is successfully done!")
            print(judge_1)
            self.text_data.insert(END, "\n존 세분화를 성공적으로 완료하였습니다!\n\n")
            self.text_data.see("end")

        else:
            print("\nError...")
            self.text_data.insert(END, " 오류 . . .\n")
            self.text_data.insert(END, str(judge_1)+"\n\n")
            self.text_data.see("end")

        file = open(self.name, 'w', encoding = 'utf8')
        header = 't matrices\na matrix=mf01 2016auto\n'
        file.write(header)
        for i in self.data_2.index:
            for j in self.data_2.columns:
                lines = '%d\t%d\t%f\n' % (i, j, self.data_2[i][j])
                file.write(lines)
        print("- Total of raw data:", self.data_3['Total']['Total'],
              "\n- Total of segmented data:", data_4['Total']['Total'])
        self.text_data.insert(END, " - 기존 O/D 총량  :"+str(self.data_3['Total']['Total'])+"\n")
        self.text_data.see("end")
        self.text_data.insert(END, " - 세분화 O/D 총량:"+str(data_4['Total']['Total'])+"\n\n")
        self.text_data.see("end")
        self.text_data.insert(END, "지정한 경로에 저장하였습니다:"+self.name+"\n\n")
        self.text_data.see("end")


class PopUpWindow(object):
    def __init__(self, master):
        top = self.top = Toplevel(master)
        self.lb = Label(top, text="입력한 희망 존 세분화 개수와 선택한 세분화 기준 파일의 내용이 다릅니다.")
        self.lb.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text="확인", command=self.clean_up)
        self.b.pack()

    def clean_up(self):
        self.new_data_pop = list(map(int, split("[ ;,	]", self.e.get())))
        self.top.destroy()


if __name__ == "__main__":
    root = Tk()
    m = MainWindow(root)
    root.mainloop()