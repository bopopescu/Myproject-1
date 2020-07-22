from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import datatable as matrix
import pandas as pd
import numpy as np
from tkinter import *
import mysql.connector


class MainForm:

    def __init__(self, main):

        self.main = main
        self.main.geometry('200x200')
        self.main.title('MainForm')

        self.button1 = Button(self.main, text="Load DataSet", command = self.gotoLoadDataset).place(x=50, y=5)
        self.button2 = Button(self.main, text="Unsupervised",  command = self.gotoUnsupervised).place(x=50, y=50)
        self.button3 = Button(self.main, text="Supervised",  command = self.gotoSupervised).place(x=50, y=100)

    def gotoLoadDataset(self):

        root2 = Toplevel(self.main)
        loaddataset = LoadDataset(root2)

    def gotoUnsupervised(self):

        root3 = Toplevel(self.main)
        unspervised = Unsupervised(root3)

    def gotoSupervised(self):

        root4 = Toplevel(self.main)
        supervised = Supervised(root4)




class LoadDataset():

    def __init__(self, main):

        self.main = main
        self.main.geometry('400x100')
        self.main.title('Load Dataset')

        self.fname = "Unknown"
        self.lines = "Unknown"
        try:
            self.con = mysql.connector.connect(user='root', password='r00tp@ss', host='127.0.0.1', database='MyProjectDB')
            self.cursor = self.con.cursor()

        except:
            print("Can't connect DB")

        self.label1 = Label(self.main, text="Select DataSet:").grid(row=0, column=1)
        self.button1 = Button(self.main, text="Browse", command=self.gotoBrowse).grid(row=0, column=4)
        self.button2 = Button(self.main, text="Load File", command=self.gotoLoadFile).grid(row=1, column=4)
        self.button3 = Button(self.main, text="Remove Stop words", command=self.gotoRemoveStopwords).grid(row=2, column=4)


    def gotoBrowse(self):
        self.fname = filedialog.askopenfilename(initialdir = "/home/ubuntuneedhi/Documents", title = "Select file", filetypes =(("text file","*.txt"),("all files","*.*")))
        self.label2 = Label(self.main, text=self.fname).grid(row=0, column=7)

    def gotoLoadFile(self):

        self.cursor.execute("Truncate table TblRawData")
        with open(self.fname) as fobj:
            lines = fobj.read().splitlines()
        fobj.close()
        temp="Unknown"
        for x in range(len(lines)):
            i = 1 + x
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
            a = 0
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
                            sql = "insert into TblWord (WordID, Word) values (%s, %s)"
                            val = (a+1, spl[i].strip().lower())
                            self.cursor.execute(sql, val)
                            self.con.commit()
                        except:
                            print("went wrong")


        self.con.commit()

        messagebox.showinfo("Removal of Stopwords", "Stopwords Removed Successfully!")




class Unsupervised():

    def __init__(self, main):

        self.main = main
        self.main.title('Unsupervised')
        self.main.geometry('700x300')

        try:
            self.con = mysql.connector.connect(user='root', password='r00tp@ss', host='127.0.0.1',
                                               database='MyProjectDB')
            self.cursor = self.con.cursor()

        except:
            print("Can't connect DB")


        self.matrix = pd.DataFrame()
        self.matrix1 = pd.DataFrame(columns=['Word', 'Spread Activation'])
        self.final = pd.DataFrame(columns=['Review Text'])
        self.seedf = "Unkonwn"
        self.cmbcategory = StringVar()
        self.button1 = Button(self.main, text="Initiate Matrix", command = self.gotoInitiate).place(x=5, y=5)
        self.button2 = Button(self.main, text="Compute Matrix", command = self.gotoCompute).place(x=150, y=5)
        self.label1 = Label(self.main, text="Select Over All Seed Word:").place(x=5, y=50)
        self.button3 = Button(self.main, text="Browse", command = self.gotoBrowseSeedwords).place(x=190, y=50)
        self.button4 = Button(self.main, text="Load", command = self.gotoLoadSeedWords).place(x=190, y=100)
        self.label3 = Label(self.main, text="Choose Category:").place(x=5, y=140)
        self.comboExample = ttk.Combobox(self.main, values=["food", "service", "place", "price"], textvariable = self.cmbcategory).place(x=150, y=140)
        self.button5 = ttk.Button(self.main, text="submit", command=self.gotoGraph).place(x=350, y=140)



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
        self.label2 = Label(self.main, text=self.seedf).place(x=270, y=50)

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
        self.root5 = Tk()
        self.tree = ttk.Treeview(self.root5)
        self.graph(self.cmbcategory.get())

    def graph(self, categ):
        self.tree.pack()
        self.tree.config(height = 50)

        self.tree.insert("", "0", "head item 0", text=categ)
        x = 0
        for i in range(len(self.matrix.index)):
            rh = self.matrix.index[i].strip().lower()
            if (rh.strip().lower() == categ):
                for j in range(len(self.matrix.columns) - 1):
                    valu = int(self.matrix.iloc[i, j])
                    if (valu > 0):
                        colhead = self.matrix.columns[j]
                        val = float(self.matrix.iloc[i, j])
                        column = len(self.matrix.columns)
                        weight = float(self.matrix.iloc[i, column - 1])
                        val = val / weight
                        self.tree.insert("head item 0", "%s" % x, "sub item[0][%s]" % x, text=colhead + "," + str(val))
                        x = x + 1

        for k in range(len(self.tree.get_children("head item 0"))):
            x = 0
            m = str(self.tree.item("sub item[0][%s]" % k))
            m = m[m.index(':') + len(':'):]
            sep = m.split(',')
            if (sep[1] != 'such'):
                we = sep[1].replace("'", "0")
                weight = float(we.strip().lower())
                atrrb = sep[0].replace("'", " ").strip().lower()
                if (k + 1 <= 38):
                    self.tree.insert("", "%s" % (k + 1), "head item %s" % (k + 1), text=atrrb)
                else:
                    self.tree.insert("", "%s" % k, "head item %s" % k, text=atrrb)
                for i in range(len(self.matrix.index)):
                    rh = self.matrix.index[i].strip().lower()
                    if (rh.strip().lower() == atrrb):
                        for j in range(len(self.matrix.columns) - 1):
                            valu = int(self.matrix.iloc[i, j])
                            if (valu > 0):
                                colhead = self.matrix.columns[j]
                                val = float(self.matrix.iloc[i, j])
                                column = len(self.matrix.columns)
                                weight = float(self.matrix.iloc[i, column - 1])
                                val = val / weight
                                if (k + 1 <= 38):
                                    self.tree.insert("head item %s" % (k + 1), "%s" % x,
                                                "sub item[%s]" % (k + 1) + "[%s]" % x,
                                                text=colhead + "," + str(val))
                                    x = x + 1
                                else:
                                    self.tree.insert("head item %s" % k, "%s" % x, "sub item[%s]" % k + "[%s]" % x,
                                                text=colhead + "," + str(val))
                                    x = x + 1

        self.cursor.execute("SELECT * FROM TblProcessData")
        dgseedwords = self.cursor.fetchall()


        for j in range(len(self.tree.get_children())):
            for k in range(len(self.tree.get_children("head item %s" % j))):
                nodevalue = str(self.tree.item("sub item[%s]" % j + "[%s]" % k))
                nodevalue = nodevalue[nodevalue.index(':') + len(':'):]
                sep = nodevalue.split(',')
                if (sep[1] != 'such'):
                    we = sep[1].replace("'", "0")
                    weight = float(we.strip().lower())
                    atrrb = sep[0].replace("'", " ").strip().lower()
                    value = 0
                    for i in range(len(dgseedwords)):
                        seedword = dgseedwords[i][1]
                        if (seedword.strip().lower() == atrrb.strip().lower()):
                            value = 1
                    final1 = float(((value + 1) * weight) * .2)
                    if (final1 > 1):
                        final1 = 1
                    self.matrix1 = self.matrix1.append({'Word': atrrb, 'Spread Activation': str(final1)}, ignore_index=True)

        dtfina = pd.DataFrame(columns=[categ, 'Rule Generation'])
        flythreshold = 0
        for i in range(len(self.matrix1.index)):
            flythreshold = flythreshold + float(self.matrix1.iloc[i, 1])
        flythreshold = flythreshold / float(len(self.matrix1.index))
        for i in range(len(self.matrix1.index)):
            value = float(self.matrix1.iloc[i][1])
            if (value >= flythreshold):
                dtfina = dtfina.append({categ: self.matrix1.iloc[i, 0], 'Rule Generation': self.matrix1.iloc[i, 1]},
                                       ignore_index=True)

        self.cursor.execute("select RawData from TblRawData")
        dtraw = self.cursor.fetchall()

        for i in range(len(dtraw)):
            review = dtraw[i][0].strip().lower()
            for j in range(len(dtfina.index)):
                temp = dtfina.iloc[j, 0].strip().lower()
                if (temp in review):
                    self.final = self.final.append({'Review Text': review.strip().upper()}, ignore_index=True)
                    break

        print(self.final)




class Supervised():

    def __init__(self, main):

        self.main = main
        self.main.title('Supervised')

        self.label1 = Label(self.main, text="Select DataSet:").grid(row=0, column=1)
        self.entry = Entry(self.main).grid(row=0, column=4)
        self.button1 = Button(self.main, text="Browse").grid(row=0, column=7)

def main():
    root = Tk()
    mainform = MainForm(root)
    root.mainloop()

if __name__== '__main__':
    main()