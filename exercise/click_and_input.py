from tkinter import *
from tkinter import ttk  # also import the themed tkinter for good looking widgets (not obligatory)


class Widget:
    def __init__(self):
        window = Tk()
        window.title("Repeat")
        window.resizable(0, 0)  # prohibit resizing the window

        text = ttk.Label(window, text='Text:')
        text.grid(row=0, column=0, sticky=W)
        label_result = ttk.Label(window, text='Result:')
        label_result.grid(row=1, column=0, sticky=W)
        self.label = StringVar()  # create an id for the invisible label where will be displayed the text in the box
        invisible_label = ttk.Label(window, text='', textvariable=self.label)  # create the invisible label
        invisible_label.grid(row=1, column=1, sticky=E)

        self.entry_id = StringVar()  # create an id for your entry, this helps getting the text
        entry = ttk.Entry(window, textvariable=self.entry_id, justify=RIGHT)
        entry.grid(row=0, column=1, sticky=E)

        button = ttk.Button(window, text='Click me', command=self.clicked)
        button.grid(row=2, column=1, sticky=E)
        window.bind("<Return>", self.clicked)  # handle the enter key event of your keyboard
        button.bind("<Button-1>",
                    self.clicked)  # bind the action of the left button of your mouse to the button assuming your primary click button is the left one.

        window.mainloop()  # call the mainloop function so the window won't fade after the first execution

    def clicked(self, event):
        text = self.entry_id.get()  # get the text from entry
        reply = self.label.set(format(text))  # format the text on the invisible label you created above
        print(text)
        return reply


Widget()