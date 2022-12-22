from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext

from os import listdir, getpid
from zipfile import ZipFile
from pandas import read_csv, pivot_table

from threading import Thread
from multiprocessing import Queue, cpu_count, Process, Pool, Manager
from queue import Empty
from functools import partial

from time import perf_counter

queue1 = Queue()
queue2 = Queue()


def main():
    root = Tk()
    m = MainWindow(root)
    root.mainloop()


def generic_caller(args):
    if 'confirm' in args['method']:
        return queue_confirm(args['queue'], args['data'])


def queue_confirm(queue, data):
    data_list = []
    read_time = perf_counter()
    filename_in, select_file_type_in, _, _ = data
    sep = ',' if select_file_type_in == 'in_csv' else '\s'

    # 단일 파일 통행량 정보 추출
    if filename_in.split('.')[-1] in ['in', 'txt', 'csv', 'tsv']:
        data_list = read_data([filename_in], sep, queue)

    # 압축 파일 통행량 정보 추출
    elif filename_in.split('.')[-1] == 'zip':
        directory_to_extract_to = './odod'
        with ZipFile(filename_in, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)
        filename_list = listdir(directory_to_extract_to)
        filepath_list = [directory_to_extract_to+'/'+file for file in filename_list]
        data_list = read_data(filepath_list, sep, queue)

    else:
        queue.put("올바른 파일을 선택해주세요.\n현재 선택한 파일: " + filename_in)

    queue.put(data_list)
    queue.put(". . . 통행량 파일 읽기 작업 완료 . . .\n - {}개 파일\n - 소요시간: {}s"
              .format(len(data_list), str(round(perf_counter() - read_time, 2))))
    queue.put(" Check input data finished. Please run segmentation! ")
    queue.put('done')


def read_data(filepath_list, sep, queue):
    data_list = []
    i = 0
    for filepath in filepath_list:
        file = open(filepath, 'r', encoding='utf8')

        header = [line for line in file.readlines() if not line[0].isdigit()]
        data_chunk = read_csv(filepath, skiprows=2, sep=sep, header=None, names=['O', 'D', 'Traffic'])
        # data_OD = pivot_table(data_chunk, index='O', columns='D', values='Traffic')
        data_title = filepath.split('/')[-1]

        data_list.append({'header': header, 'data': data_chunk, 'data_title': data_title})
        i += 1
        queue.put(i / len(filepath_list))

    return data_list


def seg_confirm(queue, data):
    seg_read_time = perf_counter()
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
    queue.put(". . . 세분화 파일 읽기 작업 완료 . . .\n - 소요시간: " + str(round(perf_counter() - seg_read_time, 2)) + 's')
    queue.put("세분화 전 존 번호:" + str(target_zone) + "\n\n----------------------------------")
    queue.put("세분화 후 존 번호:" + str(seg_zone) + "\n\n----------------------------------")
    queue.put("세분화 기준 데이터:" + str(pop_ratio) + "\n\n----------------------------------")
    queue.put('done')


def constOD(data, data_pop, dir_name, queue, result_list):
    '''
    퍼센티지 표현 업데이트 필요!!
    '''
    queue.put('constOD')
    constOD_time = perf_counter()
    # queue.put(". . . OD 구축 시작 . . .")

    data['data'] = pivot_table(data['data'], index='O', columns='D', values='Traffic')
    segmentation(data, data_pop, dir_name)

    tot_constOD_time = str(round(perf_counter() - constOD_time, 2))
    queue.put('Process {} const OD time: {}'.format(getpid(), tot_constOD_time))


def segmentation(data, data_pop, dir_name):
    # ----------------------------------------- 변수 선언 -----------------------------------------
    header, data_OD, data_title = data.values()
    target_zone, seg_zone, pop_ratio = data_pop

    # ----------------------------------------- 세분화 작업 -----------------------------------------
    seg_time = perf_counter()
    # queue.put(". . . 세분화 작업 시작 . . .")

    # Total 판별용 매트릭스 생성(data_judge_be / deep copy X)
    data_judge_be = data_OD.copy(deep=False)
    data_judge_be.loc['Total'] = data_judge_be.sum(axis=0)  # Total sum per column:
    data_judge_be.loc[:, 'Total'] = data_judge_be.sum(axis=1)  # Total sum per row:

    for target_zone_num, seg_zone_list, pop_list in zip(target_zone, seg_zone, pop_ratio):
        for index, seg_zone_num in enumerate(seg_zone_list):
            data_OD.loc[seg_zone_num] = (data_OD.loc[target_zone_num] * pop_list[index]).round(2)
            data_OD.loc[:, seg_zone_num] = (data_OD.loc[:, target_zone_num] * pop_list[index]).round(2)

    tot_seg_time = round(perf_counter() - seg_time, 2)
    # queue.put(". . . 세분화 작업 완료 . . .\n - 소요시간: {}s".format(str(round(perf_counter() - seg_time, 2))))

    # ----------------------------------------- 기존 존 삭제 -----------------------------------------
    delete_time = perf_counter()
    # queue.put(". . . 기존 존 삭제 작업 시작 . . .")

    for i in target_zone:
        data_OD = data_OD.drop([i], axis=0).drop([i], axis=1)

    tot_delete_time = round(perf_counter() - delete_time, 2)
    # queue.put(". . . 기존 존 삭제 작업 완료 . . .\n - 소요시간: {}s".format(str(round(perf_counter() - delete_time, 2))))
    # data_OD = data_OD.astype('float64').round(2)

    # ----------------------------------------- 판별 작업 -----------------------------------------
    judge_time = perf_counter()
    # queue.put(". . . 판별 작업 시작 . . .")

    # 세분화 후 Total 판별용 매트릭스 생성(data_judge_af)
    data_judge_af = data_OD.copy(deep=False)
    data_judge_af.loc['Total'] = data_judge_af.sum(axis=0)
    data_judge_af.loc[:, 'Total'] = data_judge_af.sum(axis=1)
    judge = abs(data_judge_be['Total']['Total'] / data_judge_af['Total']['Total'])

    if 0.9999 < judge < 1.0001:
        pass
        # queue.put("존 세분화를 성공적으로 완료하였습니다!")
    else:
        print("\nError...")
        # queue.put(" 오류 . . . ")

    # queue.put(" - 기존 O/D 총량  :" + str(data_judge_be['Total']['Total']))
    # queue.put(" - 세분화 O/D 총량:" + str(data_judge_af['Total']['Total']))
    # queue.put(" - 일치도: {}".format(str(judge)))

    tot_judge_time = round(perf_counter() - judge_time, 2)
    # queue.put(". . . 판별 작업 완료 . . .\n - 소요시간: {}s".format(str(round(perf_counter() - judge_time, 2))))

    # ----------------------------------------- 세분화 종료 / 파일 쓰기 시작 -----------------------------------------
    data['data'] = data_OD
    after_write(data, dir_name)


def after_write(data, dir_name):
    # ----------------------------------------- 변수 선언 -----------------------------------------
    header, data_OD, data_title = data.values()

    # ----------------------------------------- 파일 쓰기 작업 -----------------------------------------
    write_time = perf_counter()
    # queue.put(". . . 파일 쓰기 작업 시작 . . .")

    save_name = dir_name + '/' + data_title.split('.')[0] + '_after.csv'
    file = open(save_name, 'w', encoding='utf8')
    file.write(''.join(header))
    data_OD.T.unstack().dropna(axis=0).to_csv(file, header=False, line_terminator='\n')
    file.close()

    # queue.put(". . . 파일 쓰기 작업 완료 . . .\n\n - 소요시간: " + str(round(perf_counter() - write_time, 2)))
    # queue.put(" 지정한 경로에 저장하였습니다: {} ".format(save_name))

    tot_write_time = round(perf_counter() - write_time, 2)
    print('process id: {}, write time: {}'.format(getpid(), str(tot_write_time)))


def do_run(data: dict, data_pop, dir_name, queue, result_list):
    pool = Pool(cpu_count())
    # func = partial(constOD, data_pop, dir_name, queue)

    # pool.map(func, data)
    pool.starmap(constOD, [(data_chunk, data_pop, dir_name, queue, result_list) for data_chunk in data])
    pool.close()


class MainWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, name="frame")

        self.master = master
        self.result = []
        self.data_traffic = []
        self.data_pop = []

        self.initUI()

    def initUI(self):

        # ----------------------------- Definite Main Window -----------------------------
        self.master.title("EMME Helper")
        self.master.geometry("1000x350+100+100")
        self.master.grid_propagate(0)
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
        tab_control = ttk.Notebook(self.master)
        tab1 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Zone Segmentation')
        tab_control.pack(expand=1, fill="both")

        # ----------------------------- Declare Frames -----------------------------
        frame0 = Frame(tab1)
        frame0.pack()

        frame1 = LabelFrame(frame0, text=" Input Files ", height=80, width=480)
        frame1.grid(row=0, column=0, padx=8, pady=4)
        frame1.grid_propagate(0)

        frame2 = LabelFrame(frame0, text=" Configurations ", height=130, width=480)
        frame2.grid(row=1, column=0, padx=8, pady=4)
        frame2.grid_propagate(0)

        frame3 = LabelFrame(frame0, text=" Progress ", height=80, width=480)
        frame3.grid(row=2, column=0, padx=8, pady=4)
        frame3.grid_propagate(0)

        frame4 = LabelFrame(frame0, text=" Messages ", height=300, width=480)
        frame4.grid(row=0, rowspan=3, column=1, padx=8, pady=4)
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
        radio1.grid(row=0, column=0, sticky=W)
        radio1lb = Label(frame1)
        radio1lb.grid(row=0, column=1)

        radio2 = Radiobutton(frame1, text='tsv', value='in_tsv', variable=self.select_file_type_in)
        radio2.grid(row=0, column=2, sticky=W)
        radio2lb = Label(frame1)
        radio2lb.grid(row=0, column=3)

        radio3 = Radiobutton(frame1, text='csv', value='pop_csv', variable=self.select_file_type_pop)
        radio3.select()
        radio3.grid(row=1, column=0, sticky=W)
        radio3lb = Label(frame1)
        radio3lb.grid(row=1, column=1)

        radio4 = Radiobutton(frame1, text='tsv', value='pop_tsv', variable=self.select_file_type_pop)
        radio4.grid(row=1, column=2, sticky=W)
        radio4lb = Label(frame1)
        radio4lb.grid(row=1, column=3)

        # --------------- Declare buttons ---------------
        browse_infile_button = Button(frame1, text=" Browse .in file ", command=self.browse_button_in)
        browse_infile_button.grid(row=0, column=4, sticky=W)

        browse_popfile_button = Button(frame1, text=" Browse pop file ", command=self.browse_button_pop)
        browse_popfile_button.grid(row=1, column=4, sticky=W)

        # --------------- Declare labels ---------------
        self.infile_label = Label(frame1)
        self.infile_label.grid(row=0, column=5)

        self.popfile_label = Label(frame1)
        self.popfile_label.grid(row=1, column=5)

        # ------------------------------------------ Frame 2 ------------------------------------------
        # --------------- Declare labels ---------------
        self.save_dir_msg = Label(frame2)
        self.save_dir_msg.grid(row=0, column=1)

        # --------------- Declare buttons ---------------
        save_button = Button(frame2, text=" Save as... ", command=self.save)
        save_button.grid(row=0, column=0, sticky=W)

        self.confirm_b = Button(frame2, text=" Confirm ", command=self.confirm)
        self.confirm_b.grid(row=1, column=0, sticky=W)

        self.run_button = Button(frame2, text=" RUN ", command=self.run)
        self.run_button.grid(row=2, column=0, sticky=W)
        # --------------- Declare entries ---------------
        # self.entry_target_zone = Entry(self.frame2, textvariable=self.target_zone_sv)
        # self.entry_target_zone.grid(row=0, column=1)

        # self.entry_seg_num = Entry(self.frame2, textvariable=self.seg_num_sv)
        # self.entry_seg_num.grid(row=1, column=1)

        # self.entry_seg_zone_num = Entry(self.frame2, textvariable=self.seg_zone_num_sv)
        # self.entry_seg_zone_num.grid(row=2, column=1)

        # ------------------------------------------ Frame 3 ------------------------------------------
        # --------------- Declare labels ---------------
        traffic_data_msg = Label(frame3, text=" Input traffic data ")
        traffic_data_msg.grid(row=0, column=0, padx=3, sticky=W)
        self.traffic_data_lb = Label(frame3)
        self.traffic_data_lb.grid(row=0, column=1, sticky=W)

        pop_data_msg = Label(frame3, text=" Input population data ")
        pop_data_msg.grid(row=0, column=2, padx=3, sticky=W)
        self.pop_data_lb = Label(frame3)
        self.pop_data_lb.grid(row=0, column=3, sticky=W)

        segmentation_msg = Label(frame3, text=" Segmentation ")
        segmentation_msg.grid(row=1, column=0, padx=3, sticky=W)
        self.segmentation_lb = Label(frame3)
        self.segmentation_lb.grid(row=1, column=1, sticky=W)

        write_msg = Label(frame3, text=" Write data ")
        write_msg.grid(row=1, column=2, padx=3, sticky=W)
        self.write_lb = Label(frame3)
        self.write_lb.grid(row=1, column=3, sticky=W)

        # --------------- Declare progress bar ---------------
        self.pbar = ttk.Progressbar(frame3, mode='indeterminate')
        self.pbar.grid(row=2, column=0, columnspan=4, sticky=W+E)

        # ------------------------------------------ Frame 4 ------------------------------------------
        # --------------- Declare texts ---------------
        self.text_data = scrolledtext.ScrolledText(frame4, height=20, width=60)
        self.text_data.grid(padx=8, pady=4)
        help_text = '''
        1. 통행량 in 파일과 세분화 in 파일을 입력
        \n
         - 컴마 구분(csv), 띄어쓰기/탭 구분(tsv) 선택
        \n
         - 통행량 데이터 간략히 출력
        \n
        2. Confirm 클릭
        \n
         - 세분화 데이터 간략히 출력
        \n
        3. 저장할 파일 선택
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
            self.filename_in = filedialog.askopenfilename(title="Select file", initialfile="odod.zip")
            self.text_data.insert(END,
                                  "\n선택한 통행량 파일 경로:" + self.filename_in + "\n\n----------------------------------\n\n")
            self.infile_label.config(text=self.filename_in.split('/')[-1])
            self.text_data.see("end")
        except Exception as e:
            self.text_data.insert(END, str(e))
            print(e)

    def browse_button_pop(self):
        try:
            self.filename_pop = filedialog.askopenfilename(title="Select file", initialfile="pop.in")
            self.text_data.insert(END,
                                  "선택한 세분화 기준 파일 경로:" + self.filename_pop + "\n\n----------------------------------\n\n")
            self.popfile_label.config(text=self.filename_pop.split('/')[-1])
            self.text_data.see("end")
        except Exception as e:
            self.text_data.insert(END, str(e))
            print(e)

    def confirm(self):
        try:
            self.confirm_b.config(state=DISABLED)
            self.pbar.start()

            data_call = {'method': 'confirm',
                         'queue1': queue1,
                         'queue2': queue2,
                         'data': [self.filename_in, self.select_file_type_in.get(),
                                  self.filename_pop, self.select_file_type_pop.get()]}

            confirm_traffic = Thread(target=queue_confirm, args=(data_call['queue1'], data_call['data'],), daemon=True)
            confirm_traffic.start()

            update_traffic = Thread(target=self.progress_update, args=(queue1, self.traffic_data_lb, self.data_traffic),
                                    kwargs={'control': True}, daemon=True)
            update_traffic.start()

            confirm_pop = Thread(target=seg_confirm, args=(data_call['queue2'], data_call['data']), daemon=True)
            confirm_pop.start()

            update_pop = Thread(target=self.progress_update, args=(queue2, self.pop_data_lb, self.data_pop),
                                kwargs={'control': False}, daemon=True)
            update_pop.start()

        except Exception as e:
            self.text_data.insert(END, str(e))
            print(e)

    def run(self):
        # try:
        data = self.data_traffic
        data_pop = self.data_pop
        dir_name = self.name
        run_time = perf_counter()
        self.txt_msg_update(". . . 존 세분화를 시작합니다 . . .")

        m = Manager()
        q = m.Queue()
        result_list = m.list()

        run = Thread(target=do_run, args=(data, data_pop, dir_name, q, result_list), daemon=True)
        run.start()

        update_run = Thread(target=self.progress_update, args=(q, self.segmentation_lb, result_list),
                            kwargs={'control': True}, daemon=True)
        update_run.start()

        # 세분화 시작
        self.text_data.insert(END, ". . . 존 세분화가 완료되었습니다 . . .\n\n")
        self.text_data.insert(END, " - 전체 소요시간: " + str(perf_counter() - run_time) + "\n\n")
        # except Exception as e:
        #     self.text_data.insert(END, e)
        #     print(e)

    # def segmentation(self, data_OD_list, target_zone, seg_zone, pop_ratio):
    #     try:
    #         # Total 판별용 매트릭스 생성(data_judge_be / deep copy X)
    #         for data_OD in data_OD_list:
    #             data_judge_be = data_OD.copy(deep=False)
    #             data_judge_be.loc['Total'] = data_judge_be.sum(axis=0) # Total sum per column:
    #             data_judge_be.loc[:, 'Total'] = data_judge_be.sum(axis=1) # Total sum per row:
    #
    #             start_seg_time = process_time()
    #             self.text_data.insert(END, ". . . 세분화 작업 시작 . . .\n\n")
    #             for target_zone_num, seg_zone_list, pop_list in zip(target_zone, seg_zone, pop_ratio):
    #                 for index, seg_zone_num in enumerate(seg_zone_list):
    #                     data_OD.loc[seg_zone_num] = data_OD.loc[target_zone_num] * pop_list[index]
    #                     data_OD.loc[:, seg_zone_num] = data_OD.loc[:, target_zone_num] * pop_list[index]
    #             self.text_data.insert(END, ". . . 세분화 작업 완료 . . .\n\n")
    #             self.text_data.insert(END, " - 소요시간: " + str(process_time() - start_seg_time) + "\n\n")
    #
    #             delete_time = process_time()
    #             self.text_data.insert(END, ". . . 기존 존 삭제 작업 시작 . . .\n\n")
    #             for i in target_zone:
    #                 data_OD = data_OD.drop([i], axis=0).drop([i], axis=1)
    #             self.text_data.insert(END, ". . . 기존 존 삭제 작업 완료 . . .\n\n")
    #             self.text_data.insert(END, " - 소요시간: " + str(process_time() - delete_time) + "\n\n")
    #
    #             data_OD = data_OD.astype('float64').round(2)
    #
    #             judge_time = process_time()
    #             self.text_data.insert(END, ". . . 판별 작업 시작 . . .\n\n")
    #             # 세분화 후 Total 판별용 매트릭스 생성(data_judge_af)
    #             data_judge_af = data_OD.copy(deep=False)
    #             data_judge_af.loc['Total'] = data_judge_af.sum(axis=0)
    #             data_judge_af.loc[:, 'Total'] = data_judge_af.sum(axis=1)
    #             judge = abs(data_judge_be['Total']['Total'] / data_judge_af['Total']['Total'])
    #             self.text_data.insert(END, " - 일치도: " + str(judge) + "\n\n")
    #             self.text_data.insert(END, ". . . 판별 작업 완료 . . .\n\n")
    #             self.text_data.insert(END, " - 소요시간: " + str(process_time() - judge_time) + "\n\n")
    #
    #             if 0.9999 < judge < 1.0001:
    #                 self.text_data.insert(END, "\n존 세분화를 성공적으로 완료하였습니다!\n\n")
    #                 self.text_data.see("end")
    #             else:
    #                 print("\nError...")
    #                 self.text_data.insert(END, " 오류 . . .\n")
    #                 self.text_data.insert(END, str(judge)+"\n\n")
    #                 self.text_data.see("end")
    #
    #             self.text_data.insert(END, ". . . 파일 쓰기 작업 시작 . . .\n\n")
    #             write_time = process_time()
    #             save_name = self.name + '/' + self.filename_in.split('/')[-1].split('.')[0] + '_after.csv'
    #             file = open(save_name, 'w', encoding='utf8')
    #             file.write(''.join(self.header))
    #             data_OD.T.unstack().dropna(axis=0).to_csv(file, header=False, line_terminator='\n')
    #             file.close()
    #
    #             self.text_data.insert(END, ". . . 파일 쓰기 작업 완료 . . .\n\n")
    #             self.text_data.insert(END, " - 소요시간: " + str(process_time() - write_time) + "\n\n")
    #
    #             self.text_data.insert(END, " - 기존 O/D 총량  :"+str(data_judge_be['Total']['Total'])+"\n")
    #             self.text_data.see("end")
    #             self.text_data.insert(END, " - 세분화 O/D 총량:"+str(data_judge_af['Total']['Total'])+"\n\n")
    #             self.text_data.see("end")
    #             self.text_data.insert(END, "지정한 경로에 저장하였습니다:"+save_name+"\n\n")
    #             self.text_data.see("end")
    #     except Exception as e:
    #         self.text_data.insert(END, e)
    #         print(e)

    def popup(self, text):
        try:
            w=PopUpWindow(self.master)
            w.popup(text)
            self.run_button["state"] = "disabled"
            self.master.wait_window(w.top)
            self.run_button["state"] = "normal"
        except Exception as e:
            self.text_data.insert(END, str(e))
            print(e)

    def show_data(self, data):
        try:
            if len(data) == 1:
                text = "[Head of Data]\n" + data.head().to_string() + "\n\n" +\
                       "[Tail of Data]\n" + data.tail().to_string() + "\n\n----------------------------------\n\n"
            else:
                text = "[Summary of data]\n{}\n\n\n\n----------------------------------\n\n".format(data)
            self.text_data.insert(END, text)
            self.text_data.see("end")
        except Exception as e:
            self.text_data.insert(END, str(e))
            print(e)

    def save(self):
        try:
            # self.name = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="wow.txt")
            self.name = filedialog.askdirectory()
            self.save_dir_msg.config(text=self.name)
        except Exception as e:
            self.text_data.insert(END, str(e))
            print(e)

    def txt_msg_update(self, txt):
        self.text_data.insert(END, txt+'\n\n')
        self.text_data.see("end")

    def progress_update(self, queue, label, result, **control):
        while True:
            try:
                data = queue.get()
                if data == 'constOD':
                    label = self.segmentation_lb
                    pass
                if type(data) == float:
                    label.config(text=str(round(data*100, 1))+'%')
                elif type(data) == str and data == 'done':
                    label.config(text='✅')
                    if control['control']:
                        print(label, control)
                        self.pbar.stop()
                        self.confirm_b.config(state=NORMAL)
                    return result
                elif type(data) == str:
                    self.txt_msg_update(data)
                else:
                    result += data
            except Empty:
                pass


class PopUpWindow(object):
    def __init__(self, master):
        self.master = master
        self.top = Toplevel(master)

    def popup(self, text):
        self.lb = Label(self.top, text=text)
        self.lb.pack()
        self.b = Button(self.top, text="확인", command=self.clean_up)
        self.b.pack()

    def clean_up(self):
        self.top.destroy()


if __name__ == "__main__":
    main()
