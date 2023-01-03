from traceback import format_exc

from tkinter import *
from tkinter import filedialog, scrolledtext
from tkinter.ttk import Frame, Notebook, Progressbar, Style

from os import listdir
from zipfile import ZipFile
from csv import Sniffer
from pandas import read_csv, pivot_table

from threading import Thread
from multiprocessing import Queue, cpu_count, Pool, Manager, freeze_support
from queue import Empty

from time import perf_counter

queue1 = Queue()
queue2 = Queue()

def main():
    root = Tk()
    m = MainWindow(root)
    root.mainloop()

def queue_confirm(data, queue):
    try:
        queue.put('통행량 데이터 읽기')
        queue.put('start')
        data_list = []
        filepath_list = []
        filename_in, _, _, _ = data
        # sep = ',' if select_file_type_in == 'in_csv' else '\s'

        for file in filename_in:
            # 단일 파일 통행량 정보 추출
            if file.split('.')[-1] in ['in', 'txt', 'csv', 'tsv']:
                filepath_list.append(file)

            # 압축 파일 통행량 정보 추출
            elif file.split('.')[-1] == 'zip':
                directory_to_extract_to = file.split('.')[0]
                with ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(directory_to_extract_to)
                filename_list = listdir(directory_to_extract_to)
                for file in filename_list:
                    filepath_list.append(directory_to_extract_to+'/'+file)

            else:
                queue.put("올바른 파일을 선택해주세요.\n현재 선택한 파일: " + filename_in)

        data_list = read_data(filepath_list, queue, data_list)

        queue.put(data_list)
        queue.put(". . . 통행량 파일 읽기 작업 완료 . . .\n\n - {}개 파일".format(len(data_list)))
        queue.put('done')
        queue.put('all done')
        queue.put(" Check input data finished. Please run segmentation!"
                  "\n\n-----------------------------------------------------------")
        queue.put(None)
        return
    except Exception as e:
        queue.put('*ERROR*'+format_exc())

def read_data(filepath_list, queue, data_list):
    try:
        i = 0
        dtype = {'O': int, 'D': int, 'Traffic': float}
        for filepath in filepath_list:
            header = []
            file = open(filepath, 'r', encoding='utf8')
            for skip_index, line in enumerate(file):
                if line[0].isdigit():
                    sep = Sniffer().sniff(line).delimiter
                    break
                header.append(line)
            file.seek(0)
            data_chunk = read_csv(filepath, skiprows=skip_index, sep=sep, header=None, names=['O', 'D', 'Traffic'], dtype=dtype)
            data_title = filepath.split('/')[-1]

            i += 1
            queue.put(i / len(filepath_list))

            data_list.append({'header': header, 'data': data_chunk, 'data_title': data_title})
        return data_list

    except Exception as e:
        queue.put('*ERROR*'+format_exc())

def seg_confirm(data, queue):
    try:
        queue.put('세분화 기준 데이터 읽기')
        queue.put('start')

        _, _, filename_pop, select_file_type_pop = data
        sep = ',' if select_file_type_pop == 'pop_csv' else '\s'

        # 세분화 파일 추출
        if filename_pop.split('.')[-1] in ['in', 'txt', 'csv', 'tsv']:
            pass
        else:
            queue.put("올바른 파일을 선택해주세요.\n현재 선택한 파일: " + filename_pop)

        data_pop = read_csv(filename_pop, skiprows=1, sep=sep, header=None, names=['before', 'after', 'ratio'])

        # 세분화할 존, 세분화 후 존 번호, 세분화 기준 추출
        seg_zone_df = data_pop[data_pop.duplicated(subset='before', keep=False)].groupby('before')
        seg_data = [seg_zone_df.get_group(name) for name, group in seg_zone_df]
        a = [dict(before=int(item.values[0][0]),
                  after=[int(item['after'].iloc[i]) for i in range(len(item))],
                  ratio=[item['ratio'].iloc[i] for i in range(len(item))]) for item in seg_data]

        target_zone = [a[i]['before'] for i in range(len(a))]
        seg_zone = [a[i]['after'] for i in range(len(a))]
        pop_ratio = [a[i]['ratio'] for i in range(len(a))]

        data_list = [target_zone, seg_zone, pop_ratio]
        queue.put(data_list)

        # 세분화 데이터 표시
        queue.put(". . . 세분화 파일 읽기 작업 완료 . . .")
        queue.put(" - 세분화 전 존 번호:" + str(target_zone))
        queue.put(" - 세분화 후 존 번호:" + str(seg_zone))
        queue.put(" - 세분화 기준 데이터:" + str(pop_ratio))
        queue.put('done')
        queue.put(None)
        return

    except Exception as e:
        queue.put('*ERROR*'+format_exc())

def constOD(data, data_q, stat_q):
    try:
        data['data'] = pivot_table(data['data'], index='O', columns='D', values='Traffic')
        stat_q.put(1)
        return data
    except Exception as e:
        data_q.put('*ERROR*' + format_exc())

def segmentation(data, data_pop, data_q, stat_q):
    try:
        # ----------------------------------------- 변수 선언 -----------------------------------------
        header, data_OD, data_title = data.values()
        target_zone, seg_zone, pop_ratio = data_pop

        # ----------------------------------------- 세분화 작업 -----------------------------------------
        # Total 판별용 매트릭스 생성(data_judge_be / deep copy X)
        data_judge_be = data_OD.copy(deep=False)
        data_judge_be.loc['Total'] = data_judge_be.sum(axis=0)  # Total sum per column:
        data_judge_be.loc[:, 'Total'] = data_judge_be.sum(axis=1)  # Total sum per row:

        for target_zone_num, seg_zone_list, pop_list in zip(target_zone, seg_zone, pop_ratio):
            for index, seg_zone_num in enumerate(seg_zone_list):
                try:
                    data_OD.loc[seg_zone_num] = (data_OD.loc[target_zone_num] * pop_list[index]).round(2)
                    data_OD.loc[:, seg_zone_num] = (data_OD.loc[:, target_zone_num] * pop_list[index]).round(2)
                except KeyError as e:
                    data_q.put(f' - \'{data_title}\' 통행량 O/D에 존 번호(\'{target_zone_num}\')가 없습니다.')
                    data_q.put('*ERROR*' + format_exc())

        # ----------------------------------------- 기존 존 삭제 -----------------------------------------
        for i in target_zone:
            data_OD = data_OD.drop([i], axis=0).drop([i], axis=1)

        # data_OD = data_OD.astype('float64').round(2)

        # ----------------------------------------- 판별 작업 -----------------------------------------
        # 세분화 후 Total 판별용 매트릭스 생성(data_judge_af)
        data_judge_af = data_OD.copy(deep=False)
        data_judge_af.loc['Total'] = data_judge_af.sum(axis=0)
        data_judge_af.loc[:, 'Total'] = data_judge_af.sum(axis=1)
        judge = abs(data_judge_be['Total']['Total'] / data_judge_af['Total']['Total'])

        if 0.9999 < judge < 1.0001:
            pass
            # queue.put("존 세분화를 성공적으로 완료하였습니다!")
        else:
            # print("\nError...")
            data_q.put(" - {} 데이터 세분화 오류 . . . ".format(data_title))
            data_q.put(" - 기존 O/D 총량  :" + str(data_judge_be['Total']['Total']))
            data_q.put(" - 세분화 O/D 총량:" + str(data_judge_af['Total']['Total']))
            data_q.put(" - 일치도: {}".format(str(judge)))

        # queue.put(" - 기존 O/D 총량  :" + str(data_judge_be['Total']['Total']))
        # queue.put(" - 세분화 O/D 총량:" + str(data_judge_af['Total']['Total']))
        # queue.put(" - 일치도: {}".format(str(judge)))

        # ----------------------------------------- 세분화 종료 -----------------------------------------
        data['data'] = data_OD
        stat_q.put(1)
        return data
    except Exception as e:
        data_q.put('*ERROR*' + format_exc())

def after_write(data, dir_name, data_q, stat_q):
    try:
        # ----------------------------------------- 변수 선언 -----------------------------------------
        header, data_OD, data_title = data.values()

        # ----------------------------------------- 파일 쓰기 작업 -----------------------------------------
        save_name = dir_name + '/' + data_title.split('.')[0] + '_after.csv'
        file = open(save_name, 'w', encoding='utf8')
        file.write(''.join(header))
        data_OD.T.unstack().dropna(axis=0).to_csv(file, header=False, lineterminator='\n')
        file.close()
        stat_q.put(1)
    except Exception as e:
        data_q.put('*ERROR*' + format_exc())

def do_run(data: dict, data_pop, dir_name, data_q, stat_q):
    try:
        pool = Pool(cpu_count())
        progress = Thread(target=mp_progress, args=(data_q, stat_q, len(data)))
        progress.start()

        # ----------------------------------------- OD 구축 -----------------------------------------
        data_q.put('OD 구축')
        data_q.put('start')
        data_q.put(". . . OD 구축 시작 . . .")
        data = pool.starmap_async(constOD, [(data_chunk, data_q, stat_q) for data_chunk in data]).get()
        data_q.put(". . . OD 구축 완료 . . .")
        data_q.put('done')
        # ----------------------------------------- 세분화 작업 -----------------------------------------
        data_q.put('세분화 작업')
        data_q.put('start')
        data_q.put(". . . 세분화 작업 시작 . . .")
        data = pool.starmap_async(segmentation, [(data_chunk, data_pop, data_q, stat_q) for data_chunk in data]).get()
        data_q.put(". . . 세분화 작업 완료 . . .")
        data_q.put('done')
        # ----------------------------------------- 결과 파일 내보내기 -----------------------------------------
        data_q.put('결과 파일 내보내기')
        data_q.put('start')
        data_q.put(". . . 결과 파일 내보내기 시작 . . .")
        pool.starmap(after_write, [(data_chunk, dir_name, data_q, stat_q) for data_chunk in data])
        data_q.put(". . . 결과 파일 내보내기 완료 . . .")
        data_q.put('done')
        data_q.put('all done')
        data_q.put(". . . {}개 파일 존 세분화 완료 . . .".format(len(data)))
        data_q.put(None)
        pool.close()

    except Exception as e:
        data_q.put('*ERROR*'+format_exc())

def mp_progress(data_q, stat_q, size):
    try:
        indicator = []
        while len(indicator) < size:
            num = stat_q.get()
            if type(num) == int:
                indicator.append(num)
            progress = sum(indicator) / size
            data_q.put(progress)
            if len(indicator) == size:
                indicator = []
                continue
    except Exception as e:
        data_q.put('*ERROR*'+format_exc())

class MainWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, name="frame")

        self.master = master
        self.initUI()

    def initUI(self):

        # ----------------------------- Definite Main Window -----------------------------
        self.master.title("EMME Helper")
        self.master.geometry("1020x360+100+100")
        self.master.grid_propagate(0)

        # ----------------------------- Definite Style -----------------------------
        style = Style()
        style.configure('TNotebook.Tab', foreground='dark blue')

        # ----------------------------- Definite Menu bar -----------------------------
        # menu_bar = Menu(self.master)
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
        # self.master.config(menu=menu_bar)

        # ----------------------------- Definite Tabs -----------------------------
        tab_control = Notebook(self.master)
        tab1 = Frame(tab_control)
        tab_control.add(tab1, text='Zone Segmentation')
        tab_control.pack(expand=1, fill="both", padx=4)

        # ----------------------------- Declare Frames -----------------------------
        frame0 = Frame(tab1)
        frame0.pack()

        frame1 = LabelFrame(frame0, text=" Input Files ", height=80, width=500)
        frame1.grid(row=0, column=0, padx=8, pady=4)
        frame1.grid_propagate(0)

        frame2 = LabelFrame(frame0, text=" Configurations ", height=120, width=500)
        frame2.grid(row=1, column=0, padx=8, pady=4)
        frame2.grid_propagate(0)

        frame3 = LabelFrame(frame0, text=" Progress ", height=90, width=500)
        frame3.grid(row=2, column=0, padx=8, pady=4)
        frame3.grid_propagate(0)

        frame4 = LabelFrame(frame0, text=" Messages ", height=200, width=460)
        frame4.grid(row=0, rowspan=3, column=1, sticky=N+S, padx=8, pady=4)
        frame4.grid_propagate(0)

        # ----------------------------- Declare Variables -----------------------------
        # self.seg_num_sv = StringVar()
        # self.target_zone_sv = StringVar()
        # self.seg_zone_num_sv = StringVar()

        # ------------------------------------------ Frame 1 ------------------------------------------
        # --------------- Declare RadioButton ---------------
        self.select_file_type_in = StringVar()
        self.select_file_type_pop = StringVar()

        radio1 = Radiobutton(frame1, text='csv', value='in_csv', variable=self.select_file_type_in)
        radio1.select()
        radio1.grid(row=0, column=0, sticky=W, padx=4)
        radio1lb = Label(frame1)
        radio1lb.grid(row=0, column=1)

        radio2 = Radiobutton(frame1, text='tsv', value='in_tsv', variable=self.select_file_type_in)
        radio2.grid(row=0, column=2, sticky=W)
        radio2lb = Label(frame1)
        radio2lb.grid(row=0, column=3)

        radio3 = Radiobutton(frame1, text='csv', value='pop_csv', variable=self.select_file_type_pop)
        radio3.select()
        radio3.grid(row=1, column=0, sticky=W, padx=4)
        radio3lb = Label(frame1)
        radio3lb.grid(row=1, column=1)

        radio4 = Radiobutton(frame1, text='tsv', value='pop_tsv', variable=self.select_file_type_pop)
        radio4.grid(row=1, column=2, sticky=W)
        radio4lb = Label(frame1)
        radio4lb.grid(row=1, column=3)

        # --------------- Declare buttons ---------------
        browse_infile_button = Button(frame1, text=" Browse .in file ", command=self.browse_button_in, width=15)
        browse_infile_button.grid(row=0, column=4, sticky=W)

        browse_popfile_button = Button(frame1, text=" Browse pop file ", command=self.browse_button_pop, width=15)
        browse_popfile_button.grid(row=1, column=4, sticky=W)

        # --------------- Declare labels ---------------
        self.infile_label = Label(frame1, fg='dark blue')
        self.infile_label.grid(row=0, column=5, sticky=W, padx=8)

        self.popfile_label = Label(frame1, fg='dark blue')
        self.popfile_label.grid(row=1, column=5, sticky=W, padx=8)

        # ------------------------------------------ Frame 2 ------------------------------------------
        # --------------- Declare labels ---------------
        self.save_dir_msg = Label(frame2, fg='dark blue')
        self.save_dir_msg.grid(row=0, column=1, padx=8)

        # --------------- Declare buttons ---------------
        save_button = Button(frame2, text=" Save as... ", command=self.save, width=15)
        save_button.grid(row=0, column=0, sticky=W, padx=4, pady=2)

        self.confirm_b = Button(frame2, text=" Confirm ", command=self.confirm, width=15)
        self.confirm_b.grid(row=1, column=0, sticky=W, padx=4, pady=2)

        self.run_b = Button(frame2, text=" RUN ", command=self.run, width=15)
        self.run_b.grid(row=2, column=0, sticky=W, padx=4, pady=2)
        # --------------- Declare entries ---------------
        # self.entry_target_zone = Entry(self.frame2, textvariable=self.target_zone_sv)
        # self.entry_target_zone.grid(row=0, column=1)

        # self.entry_seg_num = Entry(self.frame2, textvariable=self.seg_num_sv)
        # self.entry_seg_num.grid(row=1, column=1)

        # self.entry_seg_zone_num = Entry(self.frame2, textvariable=self.seg_zone_num_sv)
        # self.entry_seg_zone_num.grid(row=2, column=1)

        # ------------------------------------------ Frame 3 ------------------------------------------
        # --------------- Declare labels ---------------
        traffic_data_msg = Label(frame3, text=" Read traffic data ")
        traffic_data_msg.grid(row=0, column=0, padx=3, sticky=W)
        self.traffic_data_lb = Label(frame3, width=5)
        self.traffic_data_lb.grid(row=0, column=1, sticky=W)

        pop_data_msg = Label(frame3, text=" Read population data ")
        pop_data_msg.grid(row=0, column=2, padx=3, sticky=W)
        self.pop_data_lb = Label(frame3, width=5)
        self.pop_data_lb.grid(row=0, column=3, sticky=W)

        const_od_msg = Label(frame3, text=" Construct base OD ")
        const_od_msg.grid(row=0, column=4, padx=3, sticky=W)
        self.const_od_lb = Label(frame3, width=5)
        self.const_od_lb.grid(row=0, column=5, sticky=W)

        segmentation_msg = Label(frame3, text=" Segmentation ")
        segmentation_msg.grid(row=1, column=0, padx=3, sticky=W)
        self.segmentation_lb = Label(frame3, width=5)
        self.segmentation_lb.grid(row=1, column=1, sticky=W)

        write_msg = Label(frame3, text=" Write data ")
        write_msg.grid(row=1, column=2, padx=3, sticky=W)
        self.write_lb = Label(frame3, width=5)
        self.write_lb.grid(row=1, column=3, sticky=W)

        # --------------- Declare progress bar ---------------
        self.pbar = Progressbar(frame3, mode='indeterminate')
        self.pbar.grid(row=2, column=0, columnspan=8, sticky=W+E, padx=8)

        # ------------------------------------------ Frame 4 ------------------------------------------
        # --------------- Declare texts ---------------
        self.text_data = scrolledtext.ScrolledText(frame4, height=20, width=60)
        self.text_data.tag_config('error', foreground='red', justify='center')
        self.text_data.grid(padx=8, pady=4)

        help_text = '''
        1. 통행량 in 파일과 세분화 in 파일을 입력
        \n
         - .in, .txt, .csv, .tsv, .zip 파일 선택 가능
           (복수 파일 선택 가능)
        \n
         - 컴마 구분(csv), 띄어쓰기/탭 구분(tsv) 선택
        \n
         - 통행량, 세분화 데이터 경로 출력
        \n
        2. 저장할 경로 선택
        \n
        3. Confirm 클릭
        \n
         - 통행량, 세분화 데이터 입력 결과 출력
        \n
        4. RUN 클릭
        \n
        2022. @github.com/pnchdrnklove
        \n
        '''
        self.text_data.insert(CURRENT, help_text)

    def do_nothing(self):
        print("a")

    def browse_button_in(self):
        try:
            self.filename_in = filedialog.askopenfilenames(title="Select file")
            for file in self.filename_in:
                if file.split('.')[-1] not in ['in', 'txt', 'csv', 'tsv', 'zip']:
                    self.txt_msg_update("\n올바른 파일을 선택해주세요.\n현재 선택한 파일: " + file.split('/')[-1])

            self.txt_msg_update("\n - 선택한 통행량 파일 경로:")
            for file in self.filename_in:
                self.txt_msg_update("  "+file)
            self.txt_msg_update("-----------------------------------------------------------")
            self.infile_label.config(text=[file.split('/')[-1] for file in self.filename_in])
        except Exception as e:
            self.err_msg_update(format_exc())

    def browse_button_pop(self):
        try:
            self.filename_pop = filedialog.askopenfilename(title="Select file")
            self.txt_msg_update("\n - 선택한 세분화 기준 파일 경로:\n  " + self.filename_pop +
                                "\n\n-----------------------------------------------------------")
            self.popfile_label.config(text=self.filename_pop.split('/')[-1])
        except Exception as e:
            self.err_msg_update(format_exc())

    def confirm(self):
        try:
            self.data_traffic = []
            self.data_pop = []

            self.traffic_data_lb.config(text='')
            self.pop_data_lb.config(text='')
            self.const_od_lb.config(text='')
            self.segmentation_lb.config(text='')
            self.write_lb.config(text='')

            self.confirm_b.config(state=DISABLED)
            self.run_b.config(state=NORMAL)
            self.pbar.start()

            data_call = [self.filename_in, self.select_file_type_in.get(),
                         self.filename_pop, self.select_file_type_pop.get()]

            confirm_traffic = Thread(target=queue_confirm, args=(data_call, queue1), daemon=True)
            confirm_traffic.start()

            update_traffic = Thread(target=self.progress_update, args=(queue1, self.data_traffic), daemon=True)
            update_traffic.start()

            confirm_pop = Thread(target=seg_confirm, args=(data_call, queue2), daemon=True)
            confirm_pop.start()

            update_pop = Thread(target=self.progress_update, args=(queue2, self.data_pop), daemon=True)
            update_pop.start()

        except Exception as e:
            self.err_msg_update(format_exc())

    def run(self):
        try:
            data = self.data_traffic
            data_pop = self.data_pop
            dir_name = self.name

            self.const_od_lb.config(text='')
            self.segmentation_lb.config(text='')
            self.write_lb.config(text='')

            self.txt_msg_update(". . . 존 세분화를 시작합니다 . . .")
            self.run_b.config(state=DISABLED)
            self.pbar.start()

            m = Manager()
            data_q = m.Queue()
            stat_q = m.Queue()
            result_list = m.list()

            run = Thread(target=do_run, args=(data, data_pop, dir_name, data_q, stat_q), daemon=True)
            run.start()

            update_run = Thread(target=self.progress_update, args=(data_q, result_list), daemon=True)
            update_run.start()

        except Exception as e:
            self.err_msg_update(format_exc())

    # def popup(self, text):
    #     try:
    #         w=PopUpWindow(self.master)
    #         w.popup(text)
    #         self.run_b["state"] = "disabled"
    #         self.master.wait_window(w.top)
    #         self.run_b["state"] = "normal"
    #     except Exception as e:
    #         self.txt_msg_update(str(e))


    # def show_data(self, data):
    #     try:
    #         if len(data) == 1:
    #             text = "[Head of Data]\n" + data.head().to_string() + "\n\n" +\
    #                    "[Tail of Data]\n" + data.tail().to_string() + "\n\n----------------------------------\n\n"
    #         else:
    #             text = "[Summary of data]\n{}\n\n\n\n----------------------------------\n\n".format(data)
    #         self.text_data.insert(END, text)
    #         self.text_data.see("end")
    #     except Exception as e:
    #         self.txt_msg_update(str(e))

    def save(self):
        try:
            self.name = filedialog.askdirectory()
            self.save_dir_msg.config(text=self.name)
            self.txt_msg_update("\n - 선택한 파일 저장 경로:\n  " + self.name +
                                "\n\n-----------------------------------------------------------")
        except Exception as e:
            self.err_msg_update(format_exc())

    def txt_msg_update(self, txt):
        self.text_data.insert(END, txt+'\n\n')
        self.text_data.see("end")

    def err_msg_update(self, txt):
        self.text_data.insert(END, 'ERROR\n\n', 'error')
        self.text_data.insert(END, txt+'\n\n', 'error')
        self.txt_msg_update('-----------------------------------------------------------')

        self.pbar.stop()
        self.traffic_data_lb.config(text='')
        self.pop_data_lb.config(text='')
        self.const_od_lb.config(text='')
        self.segmentation_lb.config(text='')
        self.write_lb.config(text='')
        self.confirm_b.config(state=NORMAL)
        self.run_b.config(state=NORMAL)

    def progress_update(self, queue, result):
        task_dict = {
            '통행량 데이터 읽기': {
                'label': self.traffic_data_lb,
                'button': self.confirm_b
            },
            '세분화 기준 데이터 읽기': {
                'label': self.pop_data_lb,
                'button': self.confirm_b
            },
            'OD 구축': {
                'label': self.const_od_lb,
                'button': self.run_b
            },
            '세분화 작업': {
                'label': self.segmentation_lb,
                'button': self.run_b
            },
            '결과 파일 내보내기': {
                'label': self.write_lb,
                'button': self.run_b
            }
        }
        while True:
            try:
                data = queue.get()
                if data != None:
                    if type(data) == str:
                        if data in task_dict.keys():
                            task = data
                            label = task_dict[task]['label']
                            button = task_dict[task]['button']
                        elif data == 'start':
                            start_time = perf_counter()
                        elif data == 'done':
                            label.config(text='✅')
                            task_time = perf_counter() - start_time
                            self.txt_msg_update(' - {} 소요 시간: {}s'.format(task, str(round(task_time, 2))))
                            self.txt_msg_update('-----------------------------------------------------------')
                        elif data == 'all done':
                            self.pbar.stop()
                            button.config(state=NORMAL)
                        elif data[:7] == '*ERROR*':
                            self.err_msg_update(data[7:])
                            return
                        else:
                            self.txt_msg_update(data)
                    elif type(data) == float:
                        label.config(text=str(round(data*100, 1))+'%')
                    else:
                        result += data
                else:
                    return
            except Empty:
                pass
            except Exception as e:
                self.err_msg_update(format_exc())

# class PopUpWindow(object):
#     def __init__(self, master):
#         self.master = master
#         self.top = Toplevel(master)
#
#     def popup(self, text):
#         self.lb = Label(self.top, text=text)
#         self.lb.pack()
#         self.b = Button(self.top, text="확인", command=self.clean_up)
#         self.b.pack()
#
#     def clean_up(self):
#         self.top.destroy()

if __name__ == "__main__":
    # Windows에서 Multiprocessing 사용하려면 다음 코드 꼭 입력!!
    # 이전에 다른 코드 있으면 안 됨
    freeze_support()
    main()
