from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import numpy as np


def donothing():
    print ("a")


def save():
    global name
    name = filedialog.asksaveasfilename(defaultextension=".txt")
    save_dir_msg.config(text=name)


def browse_button_in():
    global filename_in, data
    filename_in = filedialog.askopenfilename(title="Select file")
    if filename_in[-3:] == '.in':
        data = pd.read_csv(filename_in, skiprows=2, header=None,
                           names=['O', 'D', 'Traffic'])
        print("Directory of .in file:", filename_in)
        infile_label.config(text=filename_in)
        show_data(data)
    else:
        raise ValueError('Choose right file')


def browse_button_pop():
    global filename_pop, data_pop
    filename_pop = filedialog.askopenfilename(title="Select file")
    data_pop = pd.read_csv(filename_pop, header=None, delimiter='\t| ',
                           engine='python').values[0]
    print("Directory of pop file:", filename_pop)
    popfile_label.config(text=filename_pop)


def show_data(data):

    text_data.insert(CURRENT, 'Head of Data\n')
    text_data.insert(2.0, data.head().to_string())
    text_data.insert(END, '\n\nTail of Data\n')
    text_data.insert(END, data.tail().to_string())

    # text_data.config(text="Head of Data\n"+data.head().to_string()+"\n\nTail of Data\n"+data.tail().to_string())


def run():
    global data_2, data_3
    global seg_num, target_zone

    col = [int(i) for i in data['D'].unique()]
    row = [int(i) for i in data['O'].unique()]

    data_2 = pd.DataFrame(columns=col, index=row)
    n = 0
    for i in col:
        for j in row:
            data_2[i][j] = data['Traffic'][n]
            n = n + 1

    data_3 = data_2.copy(deep=False)
    # Total sum per column:
    data_3.loc['Total', :] = data_3.sum(axis=0)
    # Total sum per row:
    data_3.loc[:, 'Total'] = data_3.sum(axis=1)
    pop_adj()
    segmentation()


def pop_adj():
    global seg_num_sv, target_zone_sv
    global seg_num, target_zone
    global data_pop

    seg_num = int(seg_num_sv.get())  # get the text from entry
    target_zone = int(target_zone_sv.get())
    print (len(data_pop), seg_num)

    if len(data_pop) != seg_num:
        run_button['state'] = 'disabled'
        err_box()
    print("In pop_adj:", data_pop)


def segmentation():
    global seg_num, target_zone
    seg_zone_pop_ratio = np.divide(data_pop, sum(data_pop))
    for num in range(len(seg_zone_pop_ratio)):
        print("Population ratio for segmenting zone %s" % str(max(data_2.index) + 1 + num),
              ": {:.2%}".format(seg_zone_pop_ratio[num]))

    n = 0
    for i in range(max(data_2.index) + 1, max(data_2.index) + seg_num + 1):
        data_2.loc[i] = data_2.loc[target_zone] * seg_zone_pop_ratio[n]
        data_2.loc[:, i] = data_2.loc[:, target_zone] * seg_zone_pop_ratio[n]
        n = n + 1

    data_2.loc[target_zone] = 0
    data_2.loc[:, target_zone] = 0

    data_4 = data_2.copy(deep=False)
    data_4.loc['Total', :] = data_4.sum(axis=0)
    data_4.loc[:, 'Total'] = data_4.sum(axis=1)
    judge_1 = abs(data_3['Total']['Total'] / data_4['Total']['Total'])
    judge_2 = abs(data_3['Total']['Total'] - data_4['Total']['Total'])
    if 0.9999 < judge_1 < 1 and judge_2 < 0.0001 :
        print("\nZone segmentation is successfully done!")
    else:
        print("\nError...")

    print("- Total of raw data:", data_3['Total']['Total'], "\n- Total of segmented data:", data_4['Total']['Total'])

    file = open(name, 'w', encoding = 'utf8')
    # file = open('D:\\Data\\segmented_zone.txt', 'w', encoding='utf8')
    header = 't matrices\na matrix=mf01 2016auto\n'
    file.write(header)
    for i in data_2.index:
        for j in data_2.columns:
            lines = '%d\t%d\t%f\n' % (i, j, data_2[i][j])
            file.write(lines)


def err_box():
    top = Toplevel(window)
    l = Label(top, text="입력한 희망 존 세분화 개수와 선택한 세분화 기준 파일의 내용이 다릅니다.")
    l.pack()
    e = Entry(top)
    e.pack()
    b = Button(top, text="확인", command=get_value(e))
    b.pack()
    print("In err_box:", data_pop)


def get_value(entry):
    global data_pop
    data_pop = (str(entry.get()))
    print ("In get_value:", (str(entry.get())))


window = Tk()

data_2 = pd.DataFrame
data_3 = pd.DataFrame
seg_num_sv = StringVar()
target_zone_sv = StringVar()
frame0 = Frame(window)
frame0.pack()

frame1 = Frame(frame0, relief="solid", bd=1, height=80, width=480)
# frame1.pack(side="left", fill="both", expand=False)
frame1.grid(row=0, column=0, sticky=W)
frame1.grid_propagate(0)

frame2 = Frame(frame0, relief="solid", bd=1, height=80, width=480)
# frame2.pack(side="left", fill="both", expand=False)
frame2.grid(row=1, column=0, sticky=W)
frame2.grid_propagate(0)

frame3 = Frame(frame0, relief="solid", bd=1, height=80, width=480)
# frame3.pack(side="left", fill="both", expand=False)
frame3.grid(row=2, column=0, sticky=W)
frame3.grid_propagate(0)

frame4 = Frame(frame0, relief="solid", bd=1, height=240, width=480)
# frame4.pack(side="right", fill="both", expand=False)
frame4.grid(row=0, rowspan=3, column=1, sticky=E)
frame4.grid_propagate(0)

# ------------------------------------------ Frame 1 ------------------------------------------

browse_infile_button = Button(frame1, text="Browse .in file", command=browse_button_in)
# browse_infile_button.pack()
browse_infile_button.grid(sticky=W)

infile_label = Label(frame1)
# infile_label.pack()
infile_label.grid(row=0, column=1)

browse_popfile_button = Button(frame1, text="Browse pop file", command=browse_button_pop)
# browse_popfile_button.pack()
browse_popfile_button.grid(sticky=W)

popfile_label = Label(frame1)
# popfile_label.pack()
popfile_label.grid(row=1, column=1)

# ------------------------------------------ Frame 2 ------------------------------------------

target_zone_msg = Label(frame2, text="Input Target zone")
# target_zone_msg.pack()
target_zone_msg.grid(row=0, column=0, sticky=W)

entry_target_zone = Entry(frame2, textvariable=target_zone_sv)
# entry_target_zone.pack()
entry_target_zone.grid(row=0, column=1)

seg_num_msg = Label(frame2, text="Input Expected segmentation")
# seg_num_msg.pack()
seg_num_msg.grid(row=1, column=0, sticky=W)

entry_seg_num = Entry(frame2, textvariable=seg_num_sv)
# entry_seg_num.pack()
entry_seg_num.grid(row=1, column=1)


# ------------------------------------------ Frame 3 ------------------------------------------

save_button = Button(frame3, text="Save as...", command=save)
# save_button.pack()
save_button.grid(row=0, column=0, sticky=W)

save_dir_msg = Label(frame3)
# save_dir_msg.pack()
save_dir_msg.grid(row=0, column=1)

run_button = Button(frame3, text="RUN", command=run)
# run_button.pack()
run_button.grid(row=1, column=0, sticky=W)

# ------------------------------------------ Frame 4 ------------------------------------------

# text_data = Label(frame4)
text_data = Text(frame4)
# text_data.pack()
text_data.grid()

'''
menubar = Menu(window)
filemenu=Menu(menubar,tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=donothing)
filemenu.add_command(label="Save", command=file_save)
filemenu.add_command(label="Save as...", command=donothing)
filemenu.add_command(label="Close", command=donothing)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

editmenu=Menu(menubar,tearoff=0)
editmenu.add_command(label="Undo", command=donothing)
editmenu.add_command(label="Copy", command=donothing)
editmenu.add_command(label="Paste", command=donothing)
menubar.add_cascade(label="Edit", menu=editmenu)

helpmenu=Menu(menubar,tearoff=0)
helpmenu.add_command(label="Help",command=donothing)
menubar.add_cascade(label="Help",menu=helpmenu)

root.config(menu=menubar)
'''
window.title("Zone Segmentation")
window.geometry("960x240+100+100")
window.grid_propagate(0)
mainloop()