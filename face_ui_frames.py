# coding=utf-8
import Tkinter as tk
import tkFont


class AlertPopup(tk.Toplevel):

    def __init__(self, top, left):
        tk.Toplevel.__init__(self)
        self.geometry('900x150+{0}+{1}'.format(left, top))
        self.overrideredirect(True)

        container = tk.Frame(self, bg='white', bd=1, padx=1, pady=1)
        container.pack(expand=tk.YES, fill=tk.BOTH)

        container = tk.Frame(container, bg='black', bd=1, padx=10, pady=10)
        container.pack(expand=tk.YES, fill=tk.BOTH)

        container = tk.Frame(container, bg='red', bd=0, padx=10, pady=10)
        container.pack(expand=tk.YES, fill=tk.BOTH)

        container = tk.Frame(container, bg='black', bd=0, padx=10, pady=10)
        self.fontFamily = 'System'
        labelFont = tkFont.Font(family=self.fontFamily, size=45)
        tk.Label(container, text='SUJETO NO RECONOCIDO', bg='black', fg='red', font=labelFont).pack()
        container.pack(expand=tk.YES, fill=tk.BOTH)
