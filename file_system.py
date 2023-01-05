import tkinter as tk
from tkinter.ttk import Frame, Notebook, Style, Treeview
from tkinter import messagebox, filedialog, scrolledtext
from os.path import getsize

from io import TextIOWrapper
from zipfile import ZipFile
from csv import Sniffer
from pandas import read_csv

import zone_segmentation

class FileSystem(Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.idx = 0
        self.cur_selection = None

        # ----------------------------- Definite Frame Wrapper -----------------------------
        # ----------------------------- Definite wrapper1 -----------------------------
        def file_list(self):
            self.wrapper1 = tk.Frame(self.master , name='file system wrapper1')
            self.wrapper1.grid(row=0, padx=20, pady=10, sticky='we')

            # ----------------------------- Definite Scrollbar -----------------------------
            scrollbar_trv = tk.Scrollbar(self.wrapper1)
            scrollbar_trv.grid(row=1, column=1, padx=(0, 20), pady=10, sticky='ns')

            # ----------------------------- Definite Treeview -----------------------------
            self.trv = Treeview(self.wrapper1, columns=(1, 2, 3), show='tree headings', height=20,
                                yscrollcommand=scrollbar_trv.set)
            self.trv.grid(row=1, column=0, padx=(20, 0), pady=10, sticky='we')

            # Scrollbar 바인딩
            scrollbar_trv['command'] = self.trv.yview

            # Column 설정
            self.trv.column('#0', anchor='w', width=150)
            self.trv.column(1, anchor='w', width=350)
            self.trv.column(2, anchor='e', width=100)
            self.trv.column(3, anchor='e', width=150)

            # 각 Column 이름 설정
            self.trv.heading('#0', text='File name', anchor='w')
            self.trv.heading(1, text='Directory', anchor='w')
            self.trv.heading(2, text='File type', anchor='e')
            self.trv.heading(3, text='Size', anchor='e')

            # 이벤트 바인딩
            self.trv.bind('<ButtonRelease-1>', self.mouse_click)
            self.trv.bind('<Double-Button-1>', self.double_click)
            self.trv.bind('<Control-a>', self.select_all)

            # ----------------------------- Definite interaction wrapper -----------------------------
            wrapper1_interaction_frame = Frame(self.wrapper1)
            wrapper1_interaction_frame.grid(row=0, padx=20, pady=(10, 0), sticky='w')

            # ----------------------------- Definite Button -------------------------------------
            # file browse 버튼 설정
            browse_infile_button = tk.Button(wrapper1_interaction_frame, text=" + ", command=self.browse_button_in, width=2)
            browse_infile_button.grid(row=0, column=0)

            # delete 버튼 설정
            delete_infile_button = tk.Button(wrapper1_interaction_frame, text=" - ", command=self.delete_button_in, width=2)
            delete_infile_button.grid(row=0, column=1)

            zone_seg_button = tk.Button(wrapper1_interaction_frame, text=" RUN ",
                                        command=lambda: self.call_popup(self), width=3)
            zone_seg_button.grid(row=0, column=5)

            # ----------------------------- Definite Label -------------------------------------
            self.file_num_label = tk.Label(wrapper1_interaction_frame, text='')
            self.file_num_label.grid(row=0, column=3, padx=(10, 0))

            self.file_sel_label = tk.Label(wrapper1_interaction_frame, text='')
            self.file_sel_label.grid(row=0, column=4, padx=(10, 0))

            # ----------------------------------------------------------------------------
        def file_data(self):
            # ----------------------------- Definite wrapper2 -----------------------------
            self.wrapper2 = tk.Frame(self.master, name='file system wrapper2')

            # ----------------------------- Definite scrolled text -----------------------------
            self.text_data = scrolledtext.ScrolledText(self.wrapper2, height=20, width=85, name='hi')
            self.text_data.grid(padx=20, pady=10)

    def call_popup(self, master):
        self.master.update()
        popup = zone_segmentation.main(self.master)

    def do_nothing(self):
        print("a")

    def mouse_click(self, event):
        self.cur_selection = self.trv.selection()

        x, y, widget = event.x, event.y, event.widget
        region = widget.identify_region(x, y)
        if region == 'nothing':
            pass

        self.file_sel_label.config(text=f'selected files: {len(self.cur_selection)}')

    def double_click(self, event):
        self.cur_selection = self.trv.selection()
        self.show_data(self.cur_selection)

    def select_all(self, event):
        all = self.trv.get_children()
        self.cur_selection = all
        # 선택(블록) 실행
        self.trv.selection_add(all)
        self.file_sel_label.config(text=f'selected files: {len(self.cur_selection)}')

    def browse_button_in(self):
        filename_in = filedialog.askopenfilenames(title="Select file")
        if filename_in != '':
            self.idx = int(self.trv.get_children()[-1].replace('번','-').split('-')[0]) if self.trv.get_children() else 0

            for i, file in enumerate(filename_in):
                file_name = file.split('/')[-1]
                file_dir = file.split('/')[:-1]
                file_ext = file.split('.')[-1]
                file_size = '%.2f MB' % (getsize(file) / (1024.0 * 1024.0))

                if file_ext in ['in', 'txt', 'csv', 'tsv', 'zip']:
                    iid = self.idx + i + 1
                    trv_value = ('/'.join(file_dir), f'{file_ext.upper()} File', file_size)

                    if file_ext == 'zip':
                        top = self.trv.insert('', 'end', text=file_name, values=trv_value, iid=str(iid) + '번', open=True)

                        zf = ZipFile(file, 'r')
                        namelist_in_zip = zf.namelist()
                        infolist_in_zip = zf.infolist()

                        for j, name in enumerate(namelist_in_zip):
                            iid_j = str(iid)+'-'+str(j+1)
                            file_ext_in_zip = name.split('.')[-1]
                            file_size_in_zip = '%.2f MB' % (infolist_in_zip[j].file_size / (1024.0 * 1024.0))
                            trv_value_in_zip = ('', f'{file_ext_in_zip.upper()} File', file_size_in_zip)
                            self.trv.insert(top, 'end', text=name, values=trv_value_in_zip, iid=iid_j+'번')

                    else:
                        self.trv.insert('', 'end', text=file_name, values=trv_value, iid=str(iid)+'번')
                else: print("올바른 파일을 선택해주세요.\n현재 선택한 파일: " + file_name)

            self.idx += i + 1
            self.auto_show_data()
        else: self.text_data.delete(1.0, tk.END)

    def delete_button_in(self):
        if self.cur_selection != None:
            confirm = messagebox.askyesno('Confirmation', f'{len(self.cur_selection)}개 파일을 삭제하시겠습니까?')
            if confirm:
                for cur_focus in self.cur_selection:
                    self.trv.delete(cur_focus)
                if len(self.trv.get_children()) != 0:
                    self.auto_show_data()
                else: self.text_data.delete(1.0, tk.END)
            else: return
        else: return

    def show_data(self, cur_selection):
        try:
            if len(cur_selection) == 1:
                if '-' not in cur_selection[0]:
                    cur_item = self.trv.item(cur_selection)
                else:
                    cur_item = self.trv.item(self.trv.parent(cur_selection))
                    cur_item_in_zip = self.trv.item(cur_selection)
                filepath = cur_item['values'][0]+'/'+cur_item['text']
                dtype = {'O': int, 'D': int, 'Traffic': float}
                header = []

                if filepath.split('.')[-1] != 'zip':
                    file = open(filepath, 'r', encoding='utf8')

                else:
                    zf = ZipFile(filepath, 'r')
                    item = zf.open(cur_item_in_zip['text'])
                    file = TextIOWrapper(item, encoding='utf-8', newline='')

                for skip_index, line in enumerate(file):
                    if line[0].isdigit():
                        sep = Sniffer().sniff(line).delimiter
                        break
                    header.append(line.replace('\r', ''))
                file.seek(0)
                data_chunk = read_csv(file, skiprows=skip_index, sep=sep, header=None, names=['O', 'D', 'Traffic'],
                                      dtype=dtype)

                self.text_data.delete(1.0, tk.END)
                for item in header:
                    self.text_data.insert(tk.END, item)
                self.text_data.insert(tk.END, '\n[Head of data]\n')
                self.text_data.insert(tk.END, data_chunk.head())
                self.text_data.insert(tk.END, '\n\n[Tail of data]\n')
                self.text_data.insert(tk.END, data_chunk.tail())
                self.text_data.insert(tk.END, '\n\n')
                self.text_data.see(tk.END)
            else: return

        except UnboundLocalError:
            pass

    # 파일 추가 시 가장 마지막 열로 이동/선택, 데이터 요약 출력
    def auto_show_data(self):
        if len(self.trv.get_children()) > 0:
            last = self.trv.get_children()[-1]
            self.trv.see(last)
            self.trv.selection_set(last)
            self.cur_selection = (last, )

            self.file_num_label.config(text=f'all files: {len(self.trv.get_children())}')
            self.file_sel_label.config(text=f'selected files: {len(self.cur_selection)}')

            self.show_data(self.cur_selection)
        else:
            self.file_num_label.config(text='all files: 0')
            self.file_sel_label.config(text='selected files: 0')