from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
from pandas import read_csv, DataFrame
from numpy import divide
from time import process_time


class MainWindow(object):
    def __init__(self, master):
        self.master = master

        # ----------------------------- Definite Main Window -----------------------------
        self.master.title("EMME Helper")
        self.master.geometry("1000x350+100+100")
        self.master.grid_propagate(0)
        # ----------------------------- Definite Menu bar -----------------------------
        # self.menu_bar = Menu(self.master)
        #
        # self.file_menu = Menu(self.menu_bar, tearoff=0)
        # self.file_menu.add_command(label="New", command=self.do_nothing)
        # self.file_menu.add_command(label="Open", command=self.do_nothing)
        # self.file_menu.add_command(label="Save", command=self.do_nothing)
        # self.file_menu.add_command(label="Save as...", command=self.do_nothing)
        # self.file_menu.add_command(label="Close", command=self.do_nothing)
        # self.file_menu.add_separator()
        # self.file_menu.add_command(label="Exit", command=root.quit)
        # self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        #
        # self.edit_menu = Menu(self.menu_bar, tearoff=0)
        # self.edit_menu.add_command(label="Undo", command=self.do_nothing)
        # self.edit_menu.add_command(label="Copy", command=self.do_nothing)
        # self.edit_menu.add_command(label="Paste", command=self.do_nothing)
        # self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        #
        # self.help_menu = Menu(self.menu_bar, tearoff=0)
        # self.help_menu.add_command(label="Help", command=self.do_nothing)
        # self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        #
        # self.master.config(menu=self.menu_bar)
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

        self.frame2 = LabelFrame(self.frame0, text=" Configurations ", height=110, width=480)
        self.frame2.grid(row=1, column=0, padx=8, pady=4)
        self.frame2.grid_propagate(0)

        self.frame3 = LabelFrame(self.frame0, text=" Buttons ", height=80, width=480)
        self.frame3.grid(row=2, column=0, padx=8, pady=4)
        self.frame3.grid_propagate(0)

        self.frame4 = LabelFrame(self.frame0, text=" Messages ", height=300, width=480)
        self.frame4.grid(row=0, rowspan=3, column=1, padx=8, pady=4)
        self.frame4.grid_propagate(0)
        # ----------------------------- Declare Variables -----------------------------
        # self.seg_num_sv = StringVar()
        # self.target_zone_sv = StringVar()
        # self.seg_zone_num_sv = StringVar()
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
        self.target_zone_msg = Label(self.frame2, text=" Input target zone ")
        self.target_zone_msg.grid(row=0, column=0, sticky=W)
        self.target_zone_lb = Label(self.frame2)
        self.target_zone_lb.grid(row=0, column=1, sticky=W)
        
        self.seg_zone_msg = Label(self.frame2, text=" Input segmented zone number ")
        self.seg_zone_msg.grid(row=1, column=0, sticky=W)
        self.seg_zone_lb = Label(self.frame2)
        self.seg_zone_lb.grid(row=1, column=1, sticky=W)
        
        self.pop_ratio_msg = Label(self.frame2, text=" Input population ratio ")
        self.pop_ratio_msg.grid(row=2, column=0, sticky=W)
        self.pop_ratio_lb = Label(self.frame2)
        self.pop_ratio_lb.grid(row=2, column=1, sticky=W)
        
        self.confirm_lb = Label(self.frame2)
        self.confirm_lb.grid(row=3, column=0, sticky=W)

        # self.seg_zone_num_msg = Label(self.frame2, text=" Input expected segmented zone number ")
        # self.seg_zone_num_msg.grid(row=2, column=0, sticky=W)

        self.confirm_b = Button(self.frame2,
                                            text=" confirm ", command=self.check_expected_seg)
        self.confirm_b.grid(row=2, column=2, sticky=W)
        # --------------- Declare entries ---------------
        # self.entry_target_zone = Entry(self.frame2, textvariable=self.target_zone_sv)
        # self.entry_target_zone.grid(row=0, column=1)

        # self.entry_seg_num = Entry(self.frame2, textvariable=self.seg_num_sv)
        # self.entry_seg_num.grid(row=1, column=1)

        # self.entry_seg_zone_num = Entry(self.frame2, textvariable=self.seg_zone_num_sv)
        # self.entry_seg_zone_num.grid(row=2, column=1)
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
        self.text_data = scrolledtext.ScrolledText(self.frame4, height=20, width=60)
        self.text_data.grid(padx=8, pady=4)

        
    def do_nothing(self):
        print ("a")

    def browse_button_in(self):
        filename_in = filedialog.askopenfilename(title="Select file", initialfile="2016auto.in")
        if filename_in[-3:] == '.in':
            self.data = read_csv(filename_in, skiprows=2, header=None, names=['O', 'D', 'Traffic'])
            self.text_data.insert(CURRENT, "선택한 .in 파일 경로:" + filename_in +
                                  "\n\n----------------------------------\n\n")
            self.infile_label.config(text=filename_in)
            self.show_data(self.data)
        else:
            self.popup(warning_txt="올바른 .in 파일을 선택해주세요.", warning_txt_sub="현재 선택한 파일: " + filename_in)

    def browse_button_pop(self):
        filename_pop = filedialog.askopenfilename(title="Select file", initialfile="pop.in")
        if filename_pop[-3:] == '.in':
            self.data_pop = read_csv(filename_pop, skiprows=1, header=None, names=['before', 'after', 'ratio'])
            self.text_data.insert(END, "선택한 세분화 기준 파일 경로:" + filename_pop +
                                  "\n\n----------------------------------\n\n")
            self.text_data.see("end")
            self.popfile_label.config(text=filename_pop)
        else:
            self.popup(warning_txt="올바른 .in 파일을 선택해주세요.", warning_txt_sub="현재 선택한 파일: " + filename_pop)

    def check_expected_seg(self):
        # 세분화할 존, 세분화 후 존 번호, 세분화 기준 추출
        seg_zone_df = self.data_pop[self.data_pop.duplicated(subset='before', keep=False)].groupby('before')
        seg_data = [seg_zone_df.get_group(name) for name, group in seg_zone_df]
        a = [dict(before=int(item.values[0][0]),
                  after=[int(item['after'].iloc[i]) for i in range(len(item))],
                  ratio=[item['ratio'].iloc[i] for i in range(len(item))]) for item in seg_data]
        
        self.target_zone = [a[i]['before'] for i in range(len(a))]
        self.seg_zone = [a[i]['after'] for i in range(len(a))]
        self.pop_ratio = [a[i]['ratio'] for i in range(len(a))]

        # 세분화 데이터 표시
        self.target_zone_lb.config(text=self.target_zone)
        self.seg_zone_lb.config(text=self.seg_zone)
        self.pop_ratio_lb.config(text=self.pop_ratio)
        self.confirm_lb.config(text=" Check input data finished. \n Please run segmentation! ")
        
    def popup(self, warning_txt, warning_txt_sub):
        self.w=PopUpWindow(self.master, warning_txt, warning_txt_sub)
        self.run_button["state"] = "disabled"
        self.master.wait_window(self.w.top)
        self.run_button["state"] = "normal"
        
    def show_data(self, data):
        self.text_data.insert(END, "[Head of Data]\n" + data.head().to_string() + "\n\n"
                              + "[Tail of Data]\n" + data.tail().to_string()
                              + "\n\n----------------------------------\n\n")
        self.text_data.see("end")

    def save(self):
        self.name = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="wow.txt")
        self.save_dir_msg.config(text=self.name)

    def run(self):
        self.text_data.insert(END, ". . . 존 세분화를 시작합니다 . . .\n\n")
        self.text_data.see("end")

        start_time_const_OD = process_time()
        self.text_data.insert(END, ". . . OD 매트릭스 생성 시작 . . .\n\n")
        # O/D 매트릭스 생성(self.data_OD)
        col = [int(i) for i in self.data['D'].unique()]
        row = [int(i) for i in self.data['O'].unique()]
        # col = self.data['D'].unique()
        # row = self.data['O'].unique()
        data_OD = DataFrame(columns=col, index=row)
        self.text_data.insert(END, " - 소요시간: " + str(process_time() - start_time_const_OD) + "\n\n")

        start_time_finish_OD = process_time()
        n = 0
        for i in col:
            for j in row:
                data_OD.at[i, j] = self.data['Traffic'][n]
                n = n + 1
        self.text_data.insert(END, " - 소요시간: " + str(process_time() - start_time_finish_OD) + "\n\n")
        self.text_data.insert(END, ". . . OD 매트릭스 생성 완료 . . .\n\n")
        self.text_data.insert(END, " - 전체 OD 구축 소요시간: " + str(process_time() - start_time_const_OD) + "\n\n")

        self.text_data.see("end")

        # 세분화 시작
        start_time_seg = process_time()
        self.segmentation(data_OD, self.target_zone, self.seg_zone, self.pop_ratio)
        self.text_data.insert(END, ". . . 존 세분화 완료 . . .\n\n")
        self.text_data.insert(END, " - 소요시간: " + str(process_time() - start_time_seg))
        self.text_data.see("end")

    def segmentation(self, data_OD, target_zone, seg_zone, pop_ratio):
        # Total 판별용 매트릭스 생성(data_judge_be / deep copy X)
        data_judge_be = data_OD.copy(deep=False)
        data_judge_be.loc['Total'] = data_judge_be.sum(axis=0) # Total sum per column:
        data_judge_be.loc[:, 'Total'] = data_judge_be.sum(axis=1) # Total sum per row:

        start_time_seg = process_time()
        self.text_data.insert(END, ". . . 세분화 작업 시작 . . .\n\n")
        for i in range(len(target_zone)):
            for n in range(len(seg_zone[i])):
                data_OD.loc[seg_zone[i][n]] = data_OD.loc[target_zone[i]] * pop_ratio[i][n]
                data_OD.loc[:, seg_zone[i][n]] = data_OD.loc[:, target_zone[i]] * pop_ratio[i][n]
        self.text_data.insert(END, ". . . 세분화 작업 완료 . . .\n\n")
        self.text_data.insert(END, " - 소요시간: " + str(process_time() - start_time_seg) + "\n\n")

        delete_time_seg = process_time()
        self.text_data.insert(END, ". . . 기존 존 삭제 작업 시작 . . .\n\n")
        for i in target_zone:
            data_OD.loc[i] = 0
            data_OD.loc[:, i] = 0
        self.text_data.insert(END, ". . . 기존 존 삭제 작업 완료 . . .\n\n")
        self.text_data.insert(END, " - 소요시간: " + str(process_time() - delete_time_seg) + "\n\n")

        data_OD = data_OD.astype('float64').round(2)

        judge_time = process_time()
        self.text_data.insert(END, ". . . 판별 작업 시작 . . .\n\n")
        # 세분화 후 Total 판별용 매트릭스 생성(data_judge_af)
        data_judge_af = data_OD.copy(deep=False)
        data_judge_af.loc['Total'] = data_judge_af.sum(axis=0)
        data_judge_af.loc[:, 'Total'] = data_judge_af.sum(axis=1)
        judge = abs(data_judge_be['Total']['Total'] / data_judge_af['Total']['Total'])
        self.text_data.insert(END, ". . . 판별 작업 완료 . . .\n\n")
        self.text_data.insert(END, " - 소요시간: " + str(process_time() - judge_time) + "\n\n")

        if 0.9999 < judge < 1.0001:
            self.text_data.insert(END, "\n존 세분화를 성공적으로 완료하였습니다!\n\n")
            self.text_data.see("end")

        else:
            print("\nError...")
            self.text_data.insert(END, " 오류 . . .\n")
            self.text_data.insert(END, str(judge)+"\n\n")
            self.text_data.see("end")

        file = open(self.name, 'w', encoding = 'utf8')
        header = 't matrices\na matrix=mf01 2016auto\n'
        file.write(header)
        for i in data_OD.index:
            for j in data_OD.columns:
                lines = '%d\t%d\t%f\n' % (i, j, data_OD[i][j])
                file.write(lines)

        self.text_data.insert(END, " - 기존 O/D 총량  :"+str(data_judge_be['Total']['Total'])+"\n")
        self.text_data.see("end")
        self.text_data.insert(END, " - 세분화 O/D 총량:"+str(data_judge_af['Total']['Total'])+"\n\n")
        self.text_data.see("end")
        self.text_data.insert(END, "지정한 경로에 저장하였습니다:"+self.name+"\n\n")
        self.text_data.see("end")


class PopUpWindow(object):
    def __init__(self, master, warning_txt, warning_txt_sub):
        top = self.top = Toplevel(master)
        self.lb = Label(top, text=warning_txt)
        self.lb.pack()
        self.lb_2 = Label(top, text=warning_txt_sub)
        self.lb_2.pack()
        self.b = Button(top, text="확인", command=self.clean_up)
        self.b.pack()

    def clean_up(self):
        self.top.destroy()


if __name__ == "__main__":
    root = Tk()
    m = MainWindow(root)
    root.mainloop()