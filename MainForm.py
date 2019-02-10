from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import datatable as matrix
import pandas as pd
import numpy as np
from tkinter import *
import mysql.connector


class MainForm:

    def __init__(self, master):

        self.master = master
        self.master.geometry('200x200')
        self.master.title('MainForm')

        self.button1 = Button(self.master, text="Load DataSet", command = self.gotoLoadDataset).place(x=50, y=5)
        self.button2 = Button(self.master, text="Unsupervised",  command = self.gotoUnsupervised).place(x=50, y=50)
        self.button3 = Button(self.master, text="Supervised",  command = self.gotoSupervised).place(x=50, y=100)

    def gotoLoadDataset(self):

        root2 = Toplevel(self.master)
        loaddataset = LoadDataset(root2)

    def gotoUnsupervised(self):

        root3 = Toplevel(self.master)
        unspervised = Unsupervised(root3)

    def gotoSupervised(self):

        root4 = Toplevel(self.master)
        supervised = Supervised(root4)


class LoadDataset():

    def __init__(self, master):

        self.master = master
        self.master.geometry('400x100')
        self.master.title('Load Dataset')

        self.fname = "Unknown"
        self.lines = "Unknown"
        try:
            self.con = mysql.connector.connect(user='root', password='r00tp@ss', host='127.0.0.1', database='MyProjectDB')
            self.cursor = self.con.cursor()

        except:
            print("Can't connect DB")

        self.label1 = Label(self.master, text="Select DataSet:").grid(row=0, column=1)
        self.button1 = Button(self.master, text="Browse", command=self.gotoBrowse).grid(row=0, column=4)
        self.button2 = Button(self.master, text="Load File", command=self.gotoLoadFile).grid(row=1, column=4)
        self.button3 = Button(self.master, text="Remove Stop words", command=self.gotoRemoveStopwords).grid(row=2, column=4)


    def gotoBrowse(self):
        self.fname = filedialog.askopenfilename(initialdir = "/home/ubuntuneedhi/Documents", title = "Select file", filetypes =(("text file","*.txt"),("all files","*.*")))
        self.label2 = Label(self.master, text=self.fname).grid(row=0, column=7)

    def gotoLoadFile(self):

        self.cursor.execute("Truncate table TblRawData")
        with open(self.fname) as fobj:
            lines = fobj.read().splitlines()
        fobj.close()
        temp="Unknown"
        for x in range(len(lines)):
            i = 1 + x;
            temp = lines[x]
            try:
                sql = "INSERT INTO TblRawData (RawID, RawData) VALUES (%s, %s)"
                val = (i, temp)
                self.cursor.execute(sql, val)
                self.con.commit()
            except:
                print("Went Wrong")

        messagebox.showinfo("Loading of DataSet", "Dataset Loaded Successfully!")

    def gotoRemoveStopwords(self):

        self.cursor.execute("SELECT * FROM TblRawData")
        rawdata =  self.cursor.fetchall()

        self.cursor.execute("SELECT * FROM Stopwords")
        dtstop =  self.cursor.fetchall()

        self.cursor.execute("Truncate table TblProcessData")

        for i in range(len(rawdata)):

            revi = rawdata[i][1].lower().replace('.', ' ')
            revi = " " + " " + revi.lower()

            for j in range(len(dtstop)):
                stop = " " + dtstop[j][1] + " "
                revi = revi.replace(stop, ' ')

            sql = "INSERT INTO TblProcessData (DataID, ReviewText) VALUES (%s, %s)"
            val = (i+1, revi)
            self.cursor.execute(sql, val)
            self.con.commit()

        self.cursor.execute("SELECT * FROM TblProcessData")
        dtprocess = self.cursor.fetchall()
        self.cursor.execute("Truncate table TblWord")

        for x in range(len(dtprocess)):

            spl = dtprocess[x][1].split(' ')
            for i in range(len(spl)):
                if (spl[i].strip().lower() != ""):
                    revi = spl[i].strip().lower()
                    flag = 0

                    for j in range(len(dtstop)):
                        stop = dtstop[j][1].strip().lower()
                        if (stop == revi):
                            flag = 1

                    if (flag == 0):
                        try:
                            sql = "insert into TblWord values (%s, %s)"
                            val = (i, spl[i].strip().lower())
                            self.cursor.execute(sql, val)
                        except:
                            print("went wrong")


        self.con.commit()

        messagebox.showinfo("Removal of Stopwords", "Stopwords Removed Successfully!")




class Unsupervised():

    def __init__(self, master):

        self.master = master
        self.master.title('Unsupervised')
        self.master.geometry('700x300')

        try:
            self.con = mysql.connector.connect(user='root', password='r00tp@ss', host='127.0.0.1',
                                               database='MyProjectDB')
            self.cursor = self.con.cursor()

        except:
            print("Can't connect DB")


        self.matrix = pd.DataFrame()
        self.seedf = "Unkonwn"
        self.cmbcategory = StringVar()
        self.button1 = Button(self.master, text="Initiate Matrix", command = self.gotoInitiate).place(x=5, y=5)
        self.button2 = Button(self.master, text="Compute Matrix", command = self.gotoCompute).place(x=150, y=5)
        self.label1 = Label(self.master, text="Select Over All Seed Word:").place(x=5, y=50)
        self.button3 = Button(self.master, text="Browse", command = self.gotoBrowseSeedwords).place(x=190, y=50)
        self.button4 = Button(self.master, text="Load", command = self.gotoLoadSeedWords).place(x=190, y=100)
        self.label3 = Label(self.master, text="Choose Category:").place(x=5, y=140)
        self.comboExample = ttk.Combobox(self.master, values=["food", "service", "place", "price"], textvariable = self.cmbcategory).place(x=150, y=140)
        self.button5 = ttk.Button(self.master, text="submit", command=self.gotoGraph).place(x=350, y=140)


    def gotoInitiate(self):

        self.cursor.execute("SELECT distinct word FROM TblWord order by word")
        dtword = self.cursor.fetchall()

        self.matrix = pd.DataFrame({'Xij': range(len(dtword))})

        for i in range(len(dtword)):
            self.matrix[dtword[i][0].strip().lower()] = 0
        self.matrix["Number of items"] = 0

        for i in range(len(dtword)):
            self.matrix['Xij'][i] = dtword[i][0].strip().lower()

        self.matrix = self.matrix.set_index('Xij')

        messagebox.showinfo("Initialization of Matrix", "Matrix initiated Successfully!")


    def gotoCompute(self):

        self.cursor.execute("SELECT distinct word FROM TblWord order by word")
        dtword = self.cursor.fetchall()

        self.cursor.execute("Select  reviewtext from TblProcessData")
        dtreview = self.cursor.fetchall()

        for i in range(len(self.matrix.index)):
            for j in range(len(self.matrix.columns)):
                colheader = self.matrix.columns[j]
                rowheader = self.matrix.index[i]
                for k in range(len(dtreview)):
                    review = dtreview[k][0].strip().lower()
                    if (colheader in review):
                        bef = review[:review.index(colheader)].strip().lower()
                        if (rowheader in bef):
                            self.matrix.iloc[i, j] = self.matrix.iloc[i, j] + 1

        self.cursor.execute("select distinct word,count(word) as noofterm from TblWord  group by word order by word")
        dtcount = self.cursor.fetchall()

        for i in range(len(self.matrix.index)):
            count = dtcount[i][1]
            column = len(self.matrix.columns)
            self.matrix.iloc[i, column - 1] = count

        messagebox.showinfo("Computation of Matrix", "Matrix computed Successfully!")


    def gotoBrowseSeedwords(self):
        self.seedf = filedialog.askopenfilename(initialdir="/home/ubuntuneedhi/Documents", title="Select file",
                                                    filetypes=(("text file", "*.txt"), ("all files", "*.*")))
        self.label2 = Label(self.master, text=self.seedf).place(x=270, y=50)

    def gotoLoadSeedWords(self):

        self.cursor.execute("Truncate table TblSeedWord")
        with open(self.seedf) as fobj:
            lines = fobj.read().splitlines()
        fobj.close()
        for x in range(len(lines)):
            i = 1 + x
            temp = lines[x]
            try:
                sql = "INSERT INTO TblSeedWord (SeedID, Words) VALUES (%s, %s)"
                val = (i, temp)
                self.cursor.execute(sql, val)
                self.con.commit()
            except:
                print("Went Wrong")


        messagebox.showinfo("Loading of Seed Words", "Seed Words Loaded Successfully!")

    def gotoGraph(self):
        print(self.cmbcategory.get())


class Supervised():

    def __init__(self, master):

        self.master = master
        self.master.title('Supervised')

        self.label1 = Label(self.master, text="Select DataSet:").grid(row=0, column=1)
        self.entry = Entry(self.master).grid(row=0, column=4)
        self.button1 = Button(self.master, text="Browse").grid(row=0, column=7)

def main():
    root = Tk()
    mainform = MainForm(root)
    root.mainloop()

if __name__== '__main__':
    main()