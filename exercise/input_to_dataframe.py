import pandas as pd
import tkinter as tk

df = pd.DataFrame([[1,2,3], [5,6,7], [101,102,103]])

# --- functions ---

def change(event, row, col):
    # get value from Entry
    value = event.widget.get()
    # set value in dataframe
    df.iloc[row,col] = value
    print(df)

# --- main --

root = tk.Tk()

# create entry for every element in dataframe

rows, cols = df.shape

for r in range(rows):
    for c in range(cols):
        e = tk.Entry(root)
        e.insert(0, df.iloc[r,c])
        e.grid(row=r, column=c)
        # ENTER
        e.bind('<Return>', lambda event, y=r, x=c: change(event,y,x))
        # ENTER on keypad
        e.bind('<KP_Enter>', lambda event, y=r, x=c: change(event,y,x))

# start program

root.mainloop()