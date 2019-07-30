#!/usr/bin/env python3

# This script is part of the WhiteboxTools geospatial analysis library.
# Authors: Dr. John Lindsay
# Created: November 28, 2017
# Last Modified: November 28, 2017
# License: MIT

import __future__
import sys
# if sys.version_info[0] < 3:
#     raise Exception("Must be using Python 3")
import json
import os
from os import path
# from __future__ import print_function
# from enum import Enum
import platform
from pathlib import Path
import glob
from sys import platform as _platform
import shlex
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import messagebox
from tkinter import PhotoImage
import webbrowser
from WBT.whitebox_tools import WhiteboxTools, to_camelcase

wbt = WhiteboxTools()


class FileSelector(tk.Frame):
    def __init__(self, json_str, runner, master=None):
        # first make sure that the json data has the correct fields
        j = json.loads(json_str)
        self.name = j['name']
        self.description = j['description']
        self.flag = j['flags'][len(j['flags']) - 1]
        self.parameter_type = j['parameter_type']
        self.file_type = ""
        if "ExistingFile" in self.parameter_type:
            self.file_type = j['parameter_type']['ExistingFile']
        elif "NewFile" in self.parameter_type:
            self.file_type = j['parameter_type']['NewFile']
        self.optional = j['optional']
        default_value = j['default_value']

        self.runner = runner

        ttk.Frame.__init__(self, master, padding='0.1i')
        self.grid()

        self.label = ttk.Label(self, text=self.name, justify=tk.LEFT)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.label.columnconfigure(0, weight=1)

        if not self.optional:
            self.label['text'] = self.label['text'] + "*"

        fs_frame = ttk.Frame(self, padding='0.0i')
        self.value = tk.StringVar()
        self.entry = ttk.Entry(
            fs_frame, width=45, justify=tk.LEFT, textvariable=self.value)
        self.entry.grid(row=0, column=0, sticky=tk.NSEW)
        self.entry.columnconfigure(0, weight=1)
        if default_value:
            self.value.set(default_value)

        # self.img = tk.PhotoImage(file=script_dir + "/img/open.gif")
        # self.open_button = ttk.Button(fs_frame, width=55, image=self.img, command=self.select_dir)
        self.open_button = ttk.Button(
            fs_frame, width=4, text="...", command=self.select_file)
        self.open_button.grid(row=0, column=1, sticky=tk.E)
        self.open_button.columnconfigure(0, weight=1)
        fs_frame.grid(row=1, column=0, sticky=tk.NSEW)
        fs_frame.columnconfigure(0, weight=10)
        fs_frame.columnconfigure(1, weight=1)
        # self.pack(fill=tk.BOTH, expand=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Add the bindings
        if _platform == "darwin":
            self.entry.bind("<Command-Key-a>", self.select_all)
        else:
            self.entry.bind("<Control-Key-a>", self.select_all)

    def select_file(self):
        try:
            result = self.value.get()
            if self.parameter_type == "Directory":
                result = filedialog.askdirectory()
            elif "ExistingFile" in self.parameter_type:
                ftypes = [('All files', '*.*')]
                if 'RasterAndVector' in self.file_type:
                    ftypes = [("Shapefiles", "*.shp"), ('Raster files', ('*.dep', '*.tif',
                                                '*.tiff', '*.flt',
                                                '*.sdat', '*.rdc',
                                                '*.asc'))]
                elif 'Raster' in self.file_type:
                    ftypes = [('Raster files', ('*.dep', '*.tif',
                                                '*.tiff', '*.flt',
                                                '*.sdat', '*.rdc',
                                                '*.asc'))]
                elif 'Lidar' in self.file_type:
                    ftypes = [("LiDAR files", ('*.las', '*.zip'))]
                elif 'Vector' in self.file_type:
                    ftypes = [("Shapefiles", "*.shp")]
                elif 'Text' in self.file_type:
                    ftypes = [("Text files", "*.txt"), ("all files", "*.*")]
                elif 'Csv' in self.file_type:
                    ftypes = [("CSC files", "*.csv"), ("all files", "*.*")]
                elif 'Html' in self.file_type:
                    ftypes = [("HTML files", "*.html")]

                result = filedialog.askopenfilename(
                    initialdir=self.runner.working_dir, title="Select file", filetypes=ftypes)

            elif "NewFile" in self.parameter_type:
                result = filedialog.asksaveasfilename()

            self.value.set(result)
            # update the working directory
            self.runner.working_dir = os.path.dirname(result)

        except:
            t = "file"
            if self.parameter_type == "Directory":
                t = "directory"
            messagebox.showinfo("Warning", "Could not find {}".format(t))

    def get_value(self):
        if self.value.get():
            v = self.value.get()
            # Do some quality assurance here.
            # Is there a directory included?
            if not path.dirname(v):
                v = path.join(self.runner.working_dir, v)

            # What about a file extension?
            ext = os.path.splitext(v)[-1].lower().strip()
            if not ext:
                ext = ""
                if 'RasterAndVector' in self.file_type:
                    ext = '.tif'
                elif 'Raster' in self.file_type:
                    ext = '.tif'
                elif 'Lidar' in self.file_type:
                    ext = '.las'
                elif 'Vector' in self.file_type:
                    ext = '.shp'
                elif 'Text' in self.file_type:
                    ext = '.txt'
                elif 'Csv' in self.file_type:
                    ext = '.csv'
                elif 'Html' in self.file_type:
                    ext = '.html'

                v += ext

            v = path.normpath(v)

            return "{}='{}'".format(self.flag, v)
        else:
            t = "file"
            if self.parameter_type == "Directory":
                t = "directory"
            if not self.optional:
                messagebox.showinfo(
                    "Error", "Unspecified {} parameter {}.".format(t, self.flag))

        return None

    def select_all(self, event):
        self.entry.select_range(0, tk.END)
        return 'break'


class FileOrFloat(tk.Frame):
    def __init__(self, json_str, runner, master=None):
        # first make sure that the json data has the correct fields
        j = json.loads(json_str)
        self.name = j['name']
        self.description = j['description']
        self.flag = j['flags'][len(j['flags']) - 1]
        self.parameter_type = j['parameter_type']
        self.file_type = j['parameter_type']['ExistingFileOrFloat']
        self.optional = j['optional']
        default_value = j['default_value']

        self.runner = runner

        ttk.Frame.__init__(self, master)
        self.grid()
        self['padding'] = '0.1i'

        self.label = ttk.Label(self, text=self.name, justify=tk.LEFT)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.label.columnconfigure(0, weight=1)

        if not self.optional:
            self.label['text'] = self.label['text'] + "*"

        fs_frame = ttk.Frame(self, padding='0.0i')
        self.value = tk.StringVar()
        self.entry = ttk.Entry(
            fs_frame, width=35, justify=tk.LEFT, textvariable=self.value)
        self.entry.grid(row=0, column=0, sticky=tk.NSEW)
        self.entry.columnconfigure(0, weight=1)
        if default_value:
            self.value.set(default_value)

        # self.img = tk.PhotoImage(file=script_dir + "/img/open.gif")
        # self.open_button = ttk.Button(fs_frame, width=55, image=self.img, command=self.select_dir)
        self.open_button = ttk.Button(
            fs_frame, width=4, text="...", command=self.select_file)
        self.open_button.grid(row=0, column=1, sticky=tk.E)
        # self.open_button.columnconfigure(0, weight=1)

        self.label = ttk.Label(fs_frame, text='OR', justify=tk.LEFT)
        self.label.grid(row=0, column=2, sticky=tk.W)
        # self.label.columnconfigure(0, weight=1)

        self.value2 = tk.StringVar()
        self.entry2 = ttk.Entry(
            fs_frame, width=10, justify=tk.LEFT, textvariable=self.value2)
        self.entry2.grid(row=0, column=3, sticky=tk.NSEW)
        self.entry2.columnconfigure(0, weight=1)
        self.entry2['justify'] = 'right'

        fs_frame.grid(row=1, column=0, sticky=tk.NSEW)
        fs_frame.columnconfigure(0, weight=10)
        fs_frame.columnconfigure(1, weight=1)
        # self.pack(fill=tk.BOTH, expand=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Add the bindings
        if _platform == "darwin":
            self.entry.bind("<Command-Key-a>", self.select_all)
        else:
            self.entry.bind("<Control-Key-a>", self.select_all)

    def select_file(self):
        try:
            result = self.value.get()
            ftypes = [('All files', '*.*')]
            if 'RasterAndVector' in self.file_type:
                    ftypes = [("Shapefiles", "*.shp"), ('Raster files', ('*.dep', '*.tif',
                                                '*.tiff', '*.flt',
                                                '*.sdat', '*.rdc',
                                                '*.asc'))]
            elif 'Raster' in self.file_type:
                ftypes = [('Raster files', ('*.dep', '*.tif',
                                            '*.tiff', '*.flt',
                                            '*.sdat', '*.rdc',
                                            '*.asc'))]
            elif 'Lidar' in self.file_type:
                ftypes = [("LiDAR files", ('*.las', '*.zip'))]
            elif 'Vector' in self.file_type:
                ftypes = [("Shapefiles", "*.shp")]
            elif 'Text' in self.file_type:
                ftypes = [("Text files", "*.txt"), ("all files", "*.*")]
            elif 'Csv' in self.file_type:
                ftypes = [("CSC files", "*.csv"), ("all files", "*.*")]
            elif 'Html' in self.file_type:
                ftypes = [("HTML files", "*.html")]

            result = filedialog.askopenfilename(
                initialdir=self.runner.working_dir, title="Select file", filetypes=ftypes)

            self.value.set(result)
            # update the working directory
            self.runner.working_dir = os.path.dirname(result)

        except:
            t = "file"
            if self.parameter_type == "Directory":
                t = "directory"
            messagebox.showinfo("Warning", "Could not find {}".format(t))

    def RepresentsFloat(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def get_value(self):
        if self.value.get():
            v = self.value.get()
            # Do some quality assurance here.
            # Is there a directory included?
            if not path.dirname(v):
                v = path.join(self.runner.working_dir, v)

            # What about a file extension?
            ext = os.path.splitext(v)[-1].lower()
            if not ext:
                ext = ""
                if 'RasterAndVector' in self.file_type:
                    ext = '.tif'
                elif 'Raster' in self.file_type:
                    ext = '.tif'
                elif 'Lidar' in self.file_type:
                    ext = '.las'
                elif 'Vector' in self.file_type:
                    ext = '.shp'
                elif 'Text' in self.file_type:
                    ext = '.txt'
                elif 'Csv' in self.file_type:
                    ext = '.csv'
                elif 'Html' in self.file_type:
                    ext = '.html'

                v = v + ext

            v = path.normpath(v)

            return "{}='{}'".format(self.flag, v)
        elif self.value2.get():
            v = self.value2.get()
            if self.RepresentsFloat(v):
                return "{}={}".format(self.flag, v)
            else:
                messagebox.showinfo(
                    "Error", "Error converting parameter {} to type Float.".format(self.flag))
        else:
            if not self.optional:
                messagebox.showinfo(
                    "Error", "Unspecified file/numeric parameter {}.".format(self.flag))

        return None

    def select_all(self, event):
        self.entry.select_range(0, tk.END)
        return 'break'


class MultifileSelector(tk.Frame):
    def __init__(self, json_str, runner, master=None):
        # first make sure that the json data has the correct fields
        j = json.loads(json_str)
        self.name = j['name']
        self.description = j['description']
        self.flag = j['flags'][len(j['flags']) - 1]
        self.parameter_type = j['parameter_type']
        self.file_type = ""
        self.file_type = j['parameter_type']['FileList']
        self.optional = j['optional']
        default_value = j['default_value']

        self.runner = runner

        ttk.Frame.__init__(self, master)
        self.grid()
        self['padding'] = '0.1i'

        self.label = ttk.Label(self, text=self.name, justify=tk.LEFT)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.label.columnconfigure(0, weight=1)

        if not self.optional:
            self.label['text'] = self.label['text'] + "*"

        fs_frame = ttk.Frame(self, padding='0.0i')
        # , variable=self.value)
        self.opt = tk.Listbox(fs_frame, width=44, height=4)
        self.opt.grid(row=0, column=0, sticky=tk.NSEW)
        s = ttk.Scrollbar(fs_frame, orient=tk.VERTICAL, command=self.opt.yview)
        s.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.opt['yscrollcommand'] = s.set

        btn_frame = ttk.Frame(fs_frame, padding='0.0i')
        self.open_button = ttk.Button(
            btn_frame, width=4, text="...", command=self.select_file)
        self.open_button.grid(row=0, column=0, sticky=tk.NE)
        self.open_button.columnconfigure(0, weight=1)
        self.open_button.rowconfigure(0, weight=1)

        self.delete_button = ttk.Button(
            btn_frame, width=4, text="del", command=self.delete_entry)
        self.delete_button.grid(row=1, column=0, sticky=tk.NE)
        self.delete_button.columnconfigure(0, weight=1)
        self.delete_button.rowconfigure(1, weight=1)

        btn_frame.grid(row=0, column=2, sticky=tk.NE)

        fs_frame.grid(row=1, column=0, sticky=tk.NSEW)
        fs_frame.columnconfigure(0, weight=10)
        fs_frame.columnconfigure(1, weight=1)
        fs_frame.columnconfigure(2, weight=1)
        # self.pack(fill=tk.BOTH, expand=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def select_file(self):
        try:
            #result = self.value.get()
            init_dir = self.runner.working_dir
            ftypes = [('All files', '*.*')]
            if 'RasterAndVector' in self.file_type:
                    ftypes = [("Shapefiles", "*.shp"), ('Raster files', ('*.dep', '*.tif',
                                                '*.tiff', '*.flt',
                                                '*.sdat', '*.rdc',
                                                '*.asc'))]
            elif 'Raster' in self.file_type:
                ftypes = [('Raster files', ('*.dep', '*.tif',
                                            '*.tiff', '*.flt',
                                            '*.sdat', '*.rdc',
                                            '*.asc'))]
            elif 'Lidar' in self.file_type:
                ftypes = [("LiDAR files", ('*.las', '*.zip'))]
            elif 'Vector' in self.file_type:
                ftypes = [("Shapefiles", "*.shp")]
            elif 'Text' in self.file_type:
                ftypes = [("Text files", "*.txt"), ("all files", "*.*")]
            elif 'Csv' in self.file_type:
                ftypes = [("CSC files", "*.csv"), ("all files", "*.*")]
            elif 'Html' in self.file_type:
                ftypes = [("HTML files", "*.html")]

            result = filedialog.askopenfilenames(
                initialdir=init_dir, title="Select files", filetypes=ftypes)
            if result:
                for v in result:
                    self.opt.insert(tk.END, v)

                # update the working directory
                self.runner.working_dir = os.path.dirname(result[0])

        except:
            messagebox.showinfo("Warning", "Could not find file")

    def delete_entry(self):
        self.opt.delete(tk.ANCHOR)

    def get_value(self):
        try:
            l = self.opt.get(0, tk.END)
            if l:
                s = ""
                for i in range(0, len(l)):
                    v = l[i]
                    if not path.dirname(v):
                        v = path.join(self.runner.working_dir, v)
                    v = path.normpath(v)
                    if i < len(l) - 1:
                        s += "{};".format(v)
                    else:
                        s += "{}".format(v)

                return "{}='{}'".format(self.flag, s)
            else:
                if not self.optional:
                    messagebox.showinfo(
                        "Error", "Unspecified non-optional parameter {}.".format(self.flag))

        except:
            messagebox.showinfo(
                "Error", "Error formating files for parameter {}".format(self.flag))

        return None


class BooleanInput(tk.Frame):
    def __init__(self, json_str, master=None):
        # first make sure that the json data has the correct fields
        j = json.loads(json_str)
        self.name = j['name']
        self.description = j['description']
        self.flag = j['flags'][len(j['flags']) - 1]
        self.parameter_type = j['parameter_type']
        # just for quality control. BooleanInputs are always optional.
        self.optional = True
        default_value = j['default_value']

        ttk.Frame.__init__(self, master)
        self.grid()
        self['padding'] = '0.1i'

        frame = ttk.Frame(self, padding='0.0i')

        self.value = tk.IntVar()
        c = ttk.Checkbutton(frame, text=self.name,
                            width=55, variable=self.value)
        c.grid(row=0, column=0, sticky=tk.W)

        # set the default value
        if j['default_value'] != None and j['default_value'] != 'false':
            self.value.set(1)
        else:
            self.value.set(0)

        frame.grid(row=1, column=0, sticky=tk.W)
        frame.columnconfigure(0, weight=1)

        # self.pack(fill=tk.BOTH, expand=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def get_value(self):
        if self.value.get() == 1:
            return self.flag
        else:
            return None


class OptionsInput(tk.Frame):
    def __init__(self, json_str, master=None):
        # first make sure that the json data has the correct fields
        j = json.loads(json_str)
        self.name = j['name']
        self.description = j['description']
        self.flag = j['flags'][len(j['flags']) - 1]
        self.parameter_type = j['parameter_type']
        self.optional = j['optional']
        default_value = j['default_value']

        ttk.Frame.__init__(self, master)
        self.grid()
        self['padding'] = '0.1i'

        frame = ttk.Frame(self, padding='0.0i')

        self.label = ttk.Label(self, text=self.name, justify=tk.LEFT)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.label.columnconfigure(0, weight=1)

        frame2 = ttk.Frame(frame, padding='0.0i')
        opt = ttk.Combobox(frame2, width=40)
        opt.grid(row=0, column=0, sticky=tk.NSEW)

        self.value = None  # initialize in event of no default and no selection
        i = 1
        default_index = -1
        list = j['parameter_type']['OptionList']
        values = ()
        for v in list:
            values += (v,)
            # opt.insert(tk.END, v)
            if v == default_value:
                default_index = i - 1
            i = i + 1

        opt['values'] = values

        # opt.bind("<<ComboboxSelect>>", self.select)
        opt.bind("<<ComboboxSelected>>", self.select)
        if default_index >= 0:
            opt.current(default_index)
            opt.event_generate("<<ComboboxSelected>>")
            # opt.see(default_index)

        frame2.grid(row=0, column=0, sticky=tk.W)
        frame.grid(row=1, column=0, sticky=tk.W)
        frame.columnconfigure(0, weight=1)

        # self.pack(fill=tk.BOTH, expand=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # # first make sure that the json data has the correct fields
        # j = json.loads(json_str)
        # self.name = j['name']
        # self.description = j['description']
        # self.flag = j['flags'][len(j['flags']) - 1]
        # self.parameter_type = j['parameter_type']
        # self.optional = j['optional']
        # default_value = j['default_value']

        # ttk.Frame.__init__(self, master)
        # self.grid()
        # self['padding'] = '0.1i'

        # frame = ttk.Frame(self, padding='0.0i')

        # self.label = ttk.Label(self, text=self.name, justify=tk.LEFT)
        # self.label.grid(row=0, column=0, sticky=tk.W)
        # self.label.columnconfigure(0, weight=1)

        # frame2 = ttk.Frame(frame, padding='0.0i')
        # opt = tk.Listbox(frame2, width=40)  # , variable=self.value)
        # opt.grid(row=0, column=0, sticky=tk.NSEW)
        # s = ttk.Scrollbar(frame2, orient=tk.VERTICAL, command=opt.yview)
        # s.grid(row=0, column=1, sticky=(tk.N, tk.S))
        # opt['yscrollcommand'] = s.set

        # self.value = None  # initialize in event of no default and no selection
        # i = 1
        # default_index = -1
        # list = j['parameter_type']['OptionList']
        # for v in list:
        #     #opt.insert(i, v)
        #     opt.insert(tk.END, v)
        #     if v == default_value:
        #         default_index = i - 1
        #     i = i + 1

        # if i - 1 < 4:
        #     opt['height'] = i - 1
        # else:
        #     opt['height'] = 3

        # opt.bind("<<ListboxSelect>>", self.select)
        # if default_index >= 0:
        #     opt.select_set(default_index)
        #     opt.event_generate("<<ListboxSelect>>")
        #     opt.see(default_index)

        # frame2.grid(row=0, column=0, sticky=tk.W)
        # frame.grid(row=1, column=0, sticky=tk.W)
        # frame.columnconfigure(0, weight=1)

        # # self.pack(fill=tk.BOTH, expand=1)
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

    def get_value(self):
        if self.value:
            return "{}='{}'".format(self.flag, self.value)
        else:
            if not self.optional:
                messagebox.showinfo(
                    "Error", "Unspecified non-optional parameter {}.".format(self.flag))

        return None

    def select(self, event):
        widget = event.widget
        # selection = widget.curselection()
        self.value = widget.get()  # selection[0])


class DataInput(tk.Frame):
    def __init__(self, json_str, master=None):
        # first make sure that the json data has the correct fields
        j = json.loads(json_str)
        self.name = j['name']
        self.description = j['description']
        self.flag = j['flags'][len(j['flags']) - 1]
        self.parameter_type = j['parameter_type']
        self.optional = j['optional']
        default_value = j['default_value']

        ttk.Frame.__init__(self, master)
        self.grid()
        self['padding'] = '0.1i'

        self.label = ttk.Label(self, text=self.name, justify=tk.LEFT)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.label.columnconfigure(0, weight=1)

        self.value = tk.StringVar()
        if default_value:
            self.value.set(default_value)
        else:
            self.value.set("")

        self.entry = ttk.Entry(self, justify=tk.LEFT, textvariable=self.value)
        self.entry.grid(row=0, column=1, sticky=tk.NSEW)
        self.entry.columnconfigure(1, weight=10)

        if not self.optional:
            self.label['text'] = self.label['text'] + "*"

        if ("Integer" in self.parameter_type or
            "Float" in self.parameter_type or
                "Double" in self.parameter_type):
            self.entry['justify'] = 'right'

        # Add the bindings
        if _platform == "darwin":
            self.entry.bind("<Command-Key-a>", self.select_all)
        else:
            self.entry.bind("<Control-Key-a>", self.select_all)

        # self.pack(fill=tk.BOTH, expand=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.rowconfigure(0, weight=1)

    def RepresentsInt(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def RepresentsFloat(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def get_value(self):
        v = self.value.get()
        if v:
            if "Integer" in self.parameter_type:
                if self.RepresentsInt(self.value.get()):
                    return "{}={}".format(self.flag, self.value.get())
                else:
                    messagebox.showinfo(
                        "Error", "Error converting parameter {} to type Integer.".format(self.flag))
            elif "Float" in self.parameter_type:
                if self.RepresentsFloat(self.value.get()):
                    return "{}={}".format(self.flag, self.value.get())
                else:
                    messagebox.showinfo(
                        "Error", "Error converting parameter {} to type Float.".format(self.flag))
            elif "Double" in self.parameter_type:
                if self.RepresentsFloat(self.value.get()):
                    return "{}={}".format(self.flag, self.value.get())
                else:
                    messagebox.showinfo(
                        "Error", "Error converting parameter {} to type Double.".format(self.flag))
            else:  # String or StringOrNumber types
                return "{}='{}'".format(self.flag, self.value.get())
        else:
            if not self.optional:
                messagebox.showinfo(
                    "Error", "Unspecified non-optional parameter {}.".format(self.flag))

        return None

    def select_all(self, event):
        self.entry.select_range(0, tk.END)
        return 'break'


class WbRunner(tk.Frame):
    def __init__(self, tool_name=None, master=None):
        if platform.system() == 'Windows':
            self.ext = '.exe'
        else:
            self.ext = ''

        exe_name = "whitebox_tools{}".format(self.ext)

        self.exe_path = path.dirname(path.abspath(__file__))
        os.chdir(self.exe_path)
        for filename in glob.iglob('**/*', recursive=True):
            if filename.endswith(exe_name):
                self.exe_path = path.dirname(path.abspath(filename))
                break

        wbt.set_whitebox_dir(self.exe_path)

        ttk.Frame.__init__(self, master)
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.grid()
        self.tool_name = tool_name
        self.master.title("WhiteboxTools Runner")
        if _platform == "darwin":
            os.system(
                '''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        self.create_widgets()
        self.working_dir = str(Path.home())

    def create_widgets(self):

    #########################################################
    #              Overall/Top level Frame                  #
    #########################################################
        toplevel_frame = ttk.Frame(self, padding='0.1i')
        overall_frame = ttk.Frame(self, padding='0.1i')

        overall_frame.grid(row=0, rowspan = 2, column=1, sticky=tk.NSEW)
        toplevel_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # overall_frame.columnconfigure(0, weight=1)
        # toplevel_frame.columnconfigure(0, weight=1)

        # toplevel_frame.rowconfigure(0, weight = 10)
        # toplevel_frame.rowconfigure(1, weight = 4)

        # toplevel_frame.columnconfigure(1, weight=4)
        # self.pack(fill=tk.BOTH, expand=1)
        # toplevel_frame.columnconfigure(0, weight=1)
        # toplevel_frame.rowconfigure(0, weight=1)
      
        
    #########################################################
    #                  Calling basics                       #
    #########################################################
        self.toolbox_list = self.get_toolboxes()
        # print("self.toolbox_list: " + str(self.toolbox_list))
        self.sort_toolboxes()
        # print("self.upper_toolboxes: " + str(self.upper_toolboxes))
        # print("self.lower_toolboxes: " + str(self.lower_toolboxes))
        self.tools_and_toolboxes = wbt.toolbox('')
        # print("self.tools_and_toolboxes: " + str(self.tools_and_toolboxes))
        self.sort_tools_by_toolbox()
        # print("self.sorted_tools: " + str(self.sorted_tools))
        
        (self.toolslist, selected_item) = self.get_tools_list()               #not sure why this is needed????
        self.tool_name = self.toolslist[selected_item]

        self.tool_icon = tk.PhotoImage(file = 'C://Users//rbroders//Documents//scripts//tool.png')
        self.open_toolbox_icon = tk.PhotoImage(file = 'C://Users//rbroders//Documents//scripts//opentools.png')
        self.closed_toolbox_icon = tk.PhotoImage(file = 'C://Users//rbroders//Documents//scripts//closedToolbox.png')
    #########################################################
    #                  Toolboxes Frame                      #
    #########################################################
        self.tools_frame = ttk.LabelFrame(toplevel_frame, text="{} Available Tools".format(
            len(self.toolslist)), padding='0.1i')
        
        self.tool_tree = ttk.Treeview(self.tools_frame, height = 21)
        index = 0
        print("self.lower_toolboxes: " + str(self.lower_toolboxes))
        for toolbox in self.lower_toolboxes:
            if toolbox.find('/') != (-1):      
                self.tool_tree.insert(toolbox[:toolbox.find('/')], 0, iid = toolbox[toolbox.find('/') + 1:], text = toolbox[toolbox.find('/') + 1:], tags = 'toolbox', image = self.closed_toolbox_icon)
                for tool in self.sorted_tools[index]:
                    self.tool_tree.insert(toolbox[toolbox.find('/') + 1:], 'end', iid = tool, text = tool, tags = 'tool', image = self.tool_icon)       
            else:
                self.tool_tree.insert('', 'end', iid = toolbox, text = toolbox, tags = 'toolbox', image = self.closed_toolbox_icon)                         
                for tool in self.sorted_tools[index]:
                    self.tool_tree.insert(toolbox, 'end', iid = tool, text = tool, tags = 'tool', image = self.tool_icon) 
            index = index + 1 


        self.tool_tree.tag_bind('tool', "<<TreeviewSelect>>", self.update_tool_help)
        self.tool_tree.tag_bind('toolbox', "<<TreeviewSelect>>", self.update_toolbox_icon)

        self.tool_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.tool_tree.columnconfigure(0, weight=10)
        self.tool_tree.rowconfigure(0, weight=1)
        s = ttk.Scrollbar(self.tools_frame, orient=tk.VERTICAL,
                          command=self.tool_tree.yview)
        s.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tool_tree['yscrollcommand'] = s.set
        self.tools_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.tools_frame.columnconfigure(0, weight=10)
        self.tools_frame.columnconfigure(1, weight=1)
        self.tools_frame.rowconfigure(0, weight=10)
        print("799")

    #########################################################
    #                     Search Bar                        #
    #########################################################
        self.search_frame = ttk.LabelFrame(toplevel_frame, padding='0.1i')

        self.search_label = ttk.Label(self.search_frame, text = "Search: ")
        self.search_label.grid(row = 0, column = 0, sticky=tk.NW)
        
        self.search_text = tk.StringVar()
        self.search_bar = ttk.Entry(self.search_frame, width = 30, textvariable = self.search_text)
        self.search_bar.grid(row = 0, column = 1, sticky=tk.NE)
        
        self.search_results_listbox = tk.Listbox(self.search_frame, height=8) #add listvariable
        self.search_results_listbox.grid(row = 1, column = 0, columnspan = 2, sticky=tk.NSEW, pady = 5)
        self.search_results_listbox.bind("<<ListboxSelect>>", self.search_update_tool_help)

        self.search_scroll = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL, command=self.search_results_listbox.yview)
        self.search_scroll.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.search_results_listbox['yscrollcommand'] = self.search_scroll.set
        
        self.search_bar.bind('<Return>', self.update_search)
        self.search_frame.grid(row = 1, column = 0, sticky=tk.NSEW)
        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.columnconfigure(1, weight=10)
        self.search_frame.columnconfigure(1, weight=1)
        self.search_frame.rowconfigure(0, weight=1)
        self.search_frame.rowconfigure(1, weight = 10)

    #########################################################
    #                 Current Tool Frame                    #
    #########################################################

        current_tool_frame = ttk.Frame(overall_frame, padding='0.2i')
        self.current_tool_lbl = ttk.Label(current_tool_frame, text="Current Tool: {}".format(
            self.tool_name), justify=tk.LEFT)  # , font=("Helvetica", 12, "bold")
        self.current_tool_lbl.grid(row=0, column=0, sticky=tk.W)
        self.view_code_button = ttk.Button(
            current_tool_frame, text="View Code", width=12, command=self.view_code)
        self.view_code_button.grid(row=0, column=1, sticky=tk.E)
        current_tool_frame.grid(row=1, column=0, sticky=tk.NSEW)
        current_tool_frame.columnconfigure(0, weight=1)
        current_tool_frame.columnconfigure(1, weight=1)

    #########################################################
    #                     Args Frame                        #
    #########################################################
        print("811")
        self.tool_args_frame = ttk.Frame(overall_frame, padding='0.02i')
        self.tool_args_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.tool_args_frame.columnconfigure(0, weight=1)
        # sb = ttk.Scrollbar(tool_args_frame, orient=tk.VERTICAL)                 #effort to make scrollbar over arguments
        # sb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        print("816")

    #########################################################
    #                   Buttons Frame                       #
    #########################################################
        print("841")
        buttonsFrame = ttk.Frame(overall_frame, padding='0.2i')
        self.run_button = ttk.Button(
            buttonsFrame, text="Run", width=8, command=self.run_tool)
        # self.run_button.pack(pady=10, padx=10)
        self.run_button.grid(row=0, column=0)
        self.quitButton = ttk.Button(
            buttonsFrame, text="Cancel", width=8, command=self.cancel_operation)
        self.quitButton.grid(row=0, column=1)
        buttonsFrame.grid(row=3, column=0, sticky=tk.E)
        
    #########################################################
    #                  Output Frame                      #
    #########################################################                
        print("851")
        output_frame = ttk.Frame(overall_frame, padding='0.2i')
        outlabel = ttk.Label(output_frame, text="Output:", justify=tk.LEFT)
        outlabel.grid(row=0, column=0, sticky=tk.NW)
        k = wbt.tool_help(self.tool_name)
        self.out_text = ScrolledText(
            output_frame, width=63, height=15, wrap=tk.NONE, padx=7, pady=7)
        self.out_text.insert(tk.END, k)
        self.out_text.grid(row=1, column=0, sticky=tk.NSEW)
        self.out_text.columnconfigure(0, weight=1)
        output_frame.grid(row=4, column=0, sticky=tk.NSEW)
        output_frame.columnconfigure(0, weight=1)
        print("863")

    #########################################################
    #                      Binding                          #
    #########################################################
        # Add the binding
        if _platform == "darwin":
            self.out_text.bind("<Command-Key-a>", self.select_all)
            # self.out_text.bind("<Command-Key-A>", self.select_all)
        else:
            self.out_text.bind("<Control-Key-a>", self.select_all)
        print("870")

    #########################################################
    #                  Progress Frame                       #
    #########################################################        
        progress_frame = ttk.Frame(overall_frame, padding='0.2i')
        self.progress_label = ttk.Label(
            progress_frame, text="Progress:", justify=tk.LEFT)
        self.progress_label.grid(row=0, column=0, sticky=tk.E, padx=5)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            progress_frame, orient="horizontal", variable=self.progress_var, length=200, maximum=100)
        self.progress.grid(row=0, column=1, sticky=tk.E)
        progress_frame.grid(row=5, column=0, sticky=tk.E)
        print("880")
        
    #########################################################
    #                  Tool Selection                       #
    #########################################################        
        print("891")
        # Select the appropriate tool, if specified, otherwise the first tool
        print("display tool selection, self.tool_index: " + str(selected_item))
        self.tool_tree.focus(self.tool_name)
        self.tool_tree.selection_set(self.tool_name)
        print("895")                             
        self.tool_tree.event_generate("<<TreeviewSelect>>")
        print("897")
        
    #########################################################
    #                       Menus                           #
    #########################################################        
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Set Working Directory",
                             command=self.set_directory)
        filemenu.add_command(
            label="Locate WhiteboxTools exe", command=self.select_exe)
        filemenu.add_command(label="Refresh Tools", command=self.refresh_tools)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(
            label="Cut", command=lambda: self.focus_get().event_generate("<<Cut>>"))
        editmenu.add_command(
            label="Copy", command=lambda: self.focus_get().event_generate("<<Copy>>"))
        editmenu.add_command(
            label="Paste", command=lambda: self.focus_get().event_generate("<<Paste>>"))

        menubar.add_cascade(label="Edit ", menu=editmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(
            label="About", command=self.help)

        helpmenu.add_command(
            label="License", command=self.license)

        menubar.add_cascade(label="Help ", menu=helpmenu)

        self.master.config(menu=menubar)
        print("928")
        
    #########################################################
    #                       Icons                           #
    #########################################################
        


    def help(self):
        print("help")
        self.print_to_output(wbt.version())

    def license(self):
        print("liscense")
        self.print_to_output(wbt.license())

    def set_directory(self):
        print("set_directory")
        try:
            self.working_dir = filedialog.askdirectory(
                initialdir=self.exe_path)
            wbt.set_working_dir(self.working_dir)
        except:
            messagebox.showinfo(
                "Warning", "Could not find WhiteboxTools executable file.")

    def select_exe(self):
        print('select_exe')
        try:
            filename = filedialog.askopenfilename(initialdir=self.exe_path)
            self.exe_path = path.dirname(path.abspath(filename))
            wbt.set_whitebox_dir(self.exe_path)
            self.refresh_tools()
        except:
            messagebox.showinfo(
                "Warning", "Could not find WhiteboxTools executable file.")

    def run_tool(self):
        print("run_tool")
        # wd_str = self.wd.get_value()
        wbt.set_working_dir(self.working_dir)
        # args = shlex.split(self.args_value.get())

        args = []
        for widget in self.tool_args_frame.winfo_children():
            v = widget.get_value()
            if v:
                args.append(v)
            elif not widget.optional:
                messagebox.showinfo(
                    "Error", "Non-optional tool parameter not specified.")
                return

        self.print_line_to_output("")
        # self.print_line_to_output("Tool arguments:{}".format(args))
        # self.print_line_to_output("")
        # Run the tool and check the return value for an error
        if wbt.run_tool(self.tool_name, args, self.custom_callback) == 1:
            print("Error running {}".format(self.tool_name))

        else:
            self.run_button["text"] = "Run"
            self.progress_var.set(0)
            self.progress_label['text'] = "Progress:"
            self.progress.update_idletasks()

    def print_to_output(self, value):
        print("print_to_output")
        self.out_text.insert(tk.END, value)
        self.out_text.see(tk.END)

    def print_line_to_output(self, value):
        print("print_line_to_output")
        self.out_text.insert(tk.END, value + "\n")
        self.out_text.see(tk.END)

    def cancel_operation(self):
        print("cancel_operation")
        wbt.cancel_op = True
        self.print_line_to_output("Cancelling operation...")
        self.progress.update_idletasks()

    def view_code(self):
        print("view_code")
        webbrowser.open_new_tab(wbt.view_code(self.tool_name).strip())
    
    # Added 'update_search' -RACHEL
    def update_search(self, event):
        print("+++++++++++++++++++++++++update_search")
        self.search_string = self.search_text.get()
        self.search_string = self.search_string.lower()
        # print("self.search_string: " + str(self.search_string))
        search_list = []
        self.search_results_listbox.delete(0, 'end')
        num_results = 0
        for tool in self.toolslist:                                     #search tool names
            toolLower = tool.lower()
            if toolLower.find(self.search_string) != (-1):
                num_results = num_results + 1
                self.search_results_listbox.insert(num_results, tool)
                search_list.append(tool)
                # print("tool name addition: " + str(tool))
        index = 0
        self.get_descriptions()
        for description in self.descriptionList:                        #search tool descriptions
            descriptionLower = description.lower()
            if descriptionLower.find(self.search_string) != (-1):
                found = 0
                for item in search_list: # check if this tool is already in the listbox
                    if self.toolslist[index] == item:
                        found = 1
                if found == 0:  # add to listbox
                    num_results = num_results + 1
                    self.search_results_listbox.insert(num_results, self.toolslist[index])
                    # print("description addition: " + str(self.toolslist[index]))
            index = index + 1
    
    # Added 'get_descriptions' -RACHEL
    def get_descriptions(self):
        print("get_descriptions")
        self.descriptionList = []
        tools = wbt.list_tools()
        toolsItems = tools.items()
        for t in toolsItems:
            self.descriptionList.append(t[1])
        # print("self.descriptionList: " + str(self.descriptionList))
    
    # Added 'update_toolbox_icon' -RACHEL
    def update_toolbox_icon(self, event):
        print("update_toolbox_icon")
        curItem = self.tool_tree.focus()
        dict = self.tool_tree.item(curItem)
        print("*********************dict: " + str(dict))
        self.toolbox_name = dict.get('text')
        print("*********************self.toolbox_name: " + self.toolbox_name)
        self.toolbox_open = dict.get('open')
        print("*********************self.toolbox_open: " + str(self.toolbox_open))
        if self.toolbox_open == True:
            self.tool_tree.item(self.toolbox_name, image = self.open_toolbox_icon)
        else:
            self.tool_tree.item(self.toolbox_name, image = self.closed_toolbox_icon)
    # Added 'search_update_tool_help' -RACHEL
    def search_update_tool_help(self, event):
        print("search_update_tool_help")

        selection = self.search_results_listbox.curselection()
        self.tool_name = self.search_results_listbox.get(selection[0])
        # print("*********************temp: " + str(temp))
        print("*********************self.tool_name: " + self.tool_name)

        self.out_text.delete('1.0', tk.END)
        for widget in self.tool_args_frame.winfo_children():
            widget.destroy()

        k = wbt.tool_help(self.tool_name)
        self.print_to_output(k)

        j = json.loads(wbt.tool_parameters(self.tool_name))
        param_num = 0
        for p in j['parameters']:
            json_str = json.dumps(
                p, sort_keys=True, indent=2, separators=(',', ': '))
            pt = p['parameter_type']
            if 'ExistingFileOrFloat' in pt:
                ff = FileOrFloat(json_str, self, self.tool_args_frame)
                ff.grid(row=param_num, column=0, sticky=tk.NSEW)
                param_num = param_num + 1
            elif ('ExistingFile' in pt or 'NewFile' in pt or 'Directory' in pt):
                fs = FileSelector(json_str, self, self.tool_args_frame)
                fs.grid(row=param_num, column=0, sticky=tk.NSEW)
                param_num = param_num + 1
            elif 'FileList' in pt:
                b = MultifileSelector(json_str, self, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.W)
                param_num = param_num + 1
            elif 'Boolean' in pt:
                b = BooleanInput(json_str, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.W)
                param_num = param_num + 1
            elif 'OptionList' in pt:
                b = OptionsInput(json_str, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.W)
                param_num = param_num + 1
            elif ('Float' in pt or 'Integer' in pt or
                  'String' in pt or 'StringOrNumber' in pt or
                  'StringList' in pt or 'VectorAttributeField' in pt):
                b = DataInput(json_str, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.NSEW)
                param_num = param_num + 1
            else:
                messagebox.showinfo(
                    "Error", "Unsupported parameter type: {}.".format(pt))

        self.update_args_box()
        self.out_text.see("%d.%d" % (1, 0))

        argScroll = ttk.Scrollbar(self.tool_args_frame, orient=tk.VERTICAL)
        argScroll.grid(row=0, rowspan = param_num, column=1, sticky=(tk.N, tk.S))


    def update_tool_help(self, event):
        print("update_tool_help")

        curItem = self.tool_tree.focus()
        temp = self.tool_tree.item(curItem)
        self.tool_name = temp.get('text')
        # print("*********************temp: " + str(temp))
        print("*********************self.tool_name: " + self.tool_name)

        self.out_text.delete('1.0', tk.END)
        for widget in self.tool_args_frame.winfo_children():
            widget.destroy()

        k = wbt.tool_help(self.tool_name)
        self.print_to_output(k)

        j = json.loads(wbt.tool_parameters(self.tool_name))
        param_num = 0
        for p in j['parameters']:
            json_str = json.dumps(
                p, sort_keys=True, indent=2, separators=(',', ': '))
            pt = p['parameter_type']
            if 'ExistingFileOrFloat' in pt:
                ff = FileOrFloat(json_str, self, self.tool_args_frame)
                ff.grid(row=param_num, column=0, sticky=tk.NSEW)
                param_num = param_num + 1
            elif ('ExistingFile' in pt or 'NewFile' in pt or 'Directory' in pt):
                fs = FileSelector(json_str, self, self.tool_args_frame)
                fs.grid(row=param_num, column=0, sticky=tk.NSEW)
                param_num = param_num + 1
            elif 'FileList' in pt:
                b = MultifileSelector(json_str, self, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.W)
                param_num = param_num + 1
            elif 'Boolean' in pt:
                b = BooleanInput(json_str, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.W)
                param_num = param_num + 1
            elif 'OptionList' in pt:
                b = OptionsInput(json_str, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.W)
                param_num = param_num + 1
            elif ('Float' in pt or 'Integer' in pt or
                  'String' in pt or 'StringOrNumber' in pt or
                  'StringList' in pt or 'VectorAttributeField' in pt):
                b = DataInput(json_str, self.tool_args_frame)
                b.grid(row=param_num, column=0, sticky=tk.NSEW)
                param_num = param_num + 1
            else:
                messagebox.showinfo(
                    "Error", "Unsupported parameter type: {}.".format(pt))

        self.update_args_box()
        self.out_text.see("%d.%d" % (1, 0))

        argScroll = ttk.Scrollbar(self.tool_args_frame, orient=tk.VERTICAL)
        argScroll.grid(row=0, rowspan = param_num, column=1, sticky=(tk.N, tk.S))

    def update_args_box(self):
        print("update_args_box")
        s = ""
        self.current_tool_lbl['text'] = "Current Tool: {}".format(
            self.tool_name)
        # self.spacer['width'] = width=(35-len(self.tool_name))
        for item in wbt.tool_help(self.tool_name).splitlines():
            if item.startswith("-"):
                k = item.split(" ")
                if "--" in k[1]:
                    value = k[1].replace(",", "")
                else:
                    value = k[0].replace(",", "")

                if "flag" in item.lower():
                    s = s + value + " "
                else:
                    if "file" in item.lower():
                        s = s + value + "='{}' "
                    else:
                        s = s + value + "={} "

        # self.args_value.set(s.strip())

    def clear_args_box(self):
        print("clear_args_box")
        self.args_value.set("")

    def args_select_all(self, event):
        print("args_select_box")
        self.args_text.select_range(0, tk.END)
        return 'break'

    def custom_callback(self, value):
        print("custom_callback")
        ''' A custom callback for dealing with tool output.
        '''
        if "%" in value:
            try:
                str_array = value.split(" ")
                label = value.replace(
                    str_array[len(str_array) - 1], "").strip()
                progress = float(
                    str_array[len(str_array) - 1].replace("%", "").strip())
                self.progress_var.set(int(progress))
                self.progress_label['text'] = label
            except ValueError as e:
                print("Problem converting parsed data into number: ", e)
            except Exception as e:
                print(e)
        else:
            self.print_line_to_output(value)

        self.update()  # this is needed for cancelling and updating the progress bar

    def select_all(self, event):
        print("select_all")
        self.out_text.tag_add(tk.SEL, "1.0", tk.END)
        self.out_text.mark_set(tk.INSERT, "1.0")
        self.out_text.see(tk.INSERT)
        return 'break'

    def get_tools_list(self):
        print("get_tools_list")
        list = []
        selected_item = -1
        for item in wbt.list_tools().keys():
            if item:
                value = to_camelcase(item)
                list.append(value)
                if value == self.tool_name:
                    selected_item = len(list) - 1
        if selected_item == -1:
            selected_item = 0
            self.tool_name = list[0]

        return (list, selected_item)

    def get_toolboxes(self):
        print("get_toolboxes")
        toolboxes = set()
        for item in wbt.toolbox().splitlines():  # run wbt.toolbox with no tool specified--returns all
            if item:
                tb = item.split(":")[1].strip()
                toolboxes.add(tb)

        # for v in sorted(toolboxes):
        #     # print(v)
        #     self.print_line_to_output(v)
        return sorted(toolboxes)

    def refresh_tools(self):
        print("refresh_tools")
        (self.toolslist, selected_item) = self.get_tools_list()
        self.tool_tree.delete(0, len(self.toolslist))
        for item in sorted(self.toolslist):
            self.tool_tree.insert(len(self.toolslist), item)

        self.tools_frame["text"] = "{} Available Tools".format(
            len(self.toolslist))
    
    # Added 'sort_toolboxes' -RACHEL
    def sort_toolboxes(self):
        print("sort_toolboxes")
        self.toolboxes = self.get_toolboxes()
        self.upper_toolboxes = []
        self.lower_toolboxes = []
        for toolbox in self.toolboxes:
            if toolbox.find('/') == (-1):
                toolbox = to_camelcase(toolbox)
                toolboxStripped = toolbox.rstrip()
                self.upper_toolboxes.append(toolboxStripped)
                self.lower_toolboxes.append(toolboxStripped)
            else:
                first = toolbox[:toolbox.find('/')]
                second = toolbox[toolbox.find('/') + 1:]
                first = to_camelcase(first)
                second = to_camelcase(second)
                firstStripped = first.rstrip()
                secondStripped = second.rstrip()
                toolbox = firstStripped + "/" + secondStripped
                self.lower_toolboxes.append(toolbox) 
                # if self.lower_toolboxes.__contains__(firstStripped):    #gets rid of upper toolbox with has sub toolboxes
                #     self.lower_toolboxes.remove(firstStripped) 
        
        self.upper_toolboxes = sorted(self.upper_toolboxes)
        self.lower_toolboxes = sorted(self.lower_toolboxes)

    # Added 'sort_tools_by_toolbox' -RACHEL
    def sort_tools_by_toolbox(self): 
        print("sort_tools_by_toolbox")
        # print("self.lower_toolboxes: " + str(self.lower_toolboxes))
        self.sorted_tools = [[] for i in range(len(self.lower_toolboxes))]
        count = 1
        # print("self.tools_and_toolboxes: " + str(self.tools_and_toolboxes))
        # print("len(self.tools_and_toolboxes): " + str(len(self.tools_and_toolboxes)))
        # print("self.tools_and_toolboxes.split('\n'): " + str(self.tools_and_toolboxes.split('\n')))
        # print("len(self.tools_and_toolboxes.split('\n')): " + str(len(self.tools_and_toolboxes.split('\n'))))

        for toolAndToolbox in self.tools_and_toolboxes.split('\n'):
            if toolAndToolbox.strip():
                tool = toolAndToolbox.strip().split(':')[0].strip()

                itemToolbox = toolAndToolbox.strip().split(':')[1].strip()
                itemToolbox = to_camelcase(itemToolbox)
                itemToolboxStripped = itemToolbox.rstrip()
                index = 0
                for toolbox in self.lower_toolboxes:
                    if toolbox == itemToolboxStripped:
                        self.sorted_tools[index].append(tool)
                        # print("\t" + tool + " added to " + toolbox)
                        break
                    index = index + 1
                count = count + 1
                # if count > 50:                                   #for temporary faster processing
                #     break

class JsonPayload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


def main():
    tool_name = None
    if len(sys.argv) > 1:
        tool_name = str(sys.argv[1])
    wbr = WbRunner(tool_name)
    wbr.mainloop()


if __name__ == '__main__':
    main()
