import Tkinter as tk
import tkFileDialog
import sqlite3
import arcpy
import csv

arcpy.env.workspace = r""
arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True


class SQLCommander:
    # Variables for Methods
    ##__init__
    HUC8s = []
    nameTV = None
    mergeTV = None
    singleTV = None

    ##selectHUC8
    HUC10s = []
    selectedHUC8 = 0

    ##selectHUC10
    selectedHUC10 = 0
    nameList = []
    mergeList = []


    ##namesTL
    nameTL = None
    listnum = -1
    nameSQLStatement = None
    counterTV = None
    HUC10TV = None

    ##mergeTL
    mergeTL = None

    ##singleTL
    singleTL = None
    objectid_entry = None

    ##nearManual
    repeatList = []
    dropList = []
    lengthList = []
    singleSQLStatement = ""
    longestSQLStatement = ""
    entryBool = None
    singleButtonPress = None
    manualButtonPress = None
    choiceButtonPress = None
    autoButtonPress = None
    fidList = []
    tlNumber = 0
    totalLength = 0
    previouslength = 0
    checkboxTV = None
    clipboard = ""
    checkbox_switch = 'off'
    selection_clip = None
    totalLengthTV =None
    longestLength = 0
    moveDisplayRight = 0
    toplevelNumber = 0


    def __init__(self, master):
        self.master = master
        master.title("SqlCommander")

        SQLCommander.nameTV = tk.StringVar()
        SQLCommander.nameTV.set("0")
        SQLCommander.mergeTV = tk.StringVar()
        SQLCommander.mergeTV.set("0")
        SQLCommander.singleTV = tk.StringVar()
        SQLCommander.singleTV.set("0")


        # File Menu

        # Huc Labels
        self.huc8Label = tk.Label(master, text='HUC_8').grid(row=0, column=0, padx=5)
        self.huc10Label = tk.Label(master, text='HUC_10').grid(row=0, column=2, padx=5)

        # Huc Scroll Bars
        self.huc8Scroll = tk.Scrollbar(master)
        self.huc8Scroll.grid(row=1, column=1, rowspan=4, sticky=tk.N + tk.S)

        self.huc10Scroll = tk.Scrollbar(master)
        self.huc10Scroll.grid(row=1, column=3, rowspan=4, sticky=tk.N + tk.S)

        # Huc Listboxes
        self.huc8Listbox = tk.Listbox(master, height=7, width=25, yscrollcommand=self.huc8Scroll.set)
        self.huc8Listbox.grid(row=1, column=0, rowspan=4, sticky=tk.N)
        self.huc8Scroll.config(command=self.huc8Listbox.yview)

        self.huc10Listbox = tk.Listbox(master, height=7, width=25, yscrollcommand=self.huc10Scroll.set)
        self.huc10Listbox.grid(row=1, column=2, rowspan=4, sticky=tk.N)
        self.huc10Scroll.config(command=self.huc10Listbox.yview)

        # Huc Select Buttons
        self.h8Button = tk.Button(master, text='Select', width=20, command=self.selectHUC8)
        self.h8Button.grid(row=5, column=0, pady=5, padx=2.5)
        self.h10Button = tk.Button(master, text='Select', width=20, command=self.selectHUC10)
        self.h10Button.grid(row=5, column=2, pady=5, padx=2.5)

        # GNIS_ID Name and Number

        self.GLabel = tk.Label(master, text='Named Streams').grid(row=0, column=5, padx=5)
        self.GButton = tk.Button(master, textvariable=SQLCommander.nameTV, width=15, relief = "groove", pady = 5, command = self.namesTL)
        self.GButton.grid(row=1, column=5, padx=5)

        # Meragable Nulls
        self.MLabel = tk.Label(master, text="Mergable Nulls").grid(row=2, column=5, padx=5)
        self.MButton = tk.Button(master, textvariable= SQLCommander.mergeTV, width=15, relief = "groove", pady = 5,  command = self.mergesTL)
        self.MButton.grid(row=3, column=5, padx=5)

        # Single Nulls
        self.SLabel = tk.Label(master, text="Single Nulls").grid(row=4, column=5, padx=5)
        self.SButton = tk.Button(master, textvariable= SQLCommander.singleTV, width=15, relief = "groove", pady = 5, command = self.singlesTL)
        self.SButton.grid(row=5, column=5, padx=5)

        # Load Watershed CSV
        sqlite_file = "REWS.sqlite"
        table_name = "REWS1"
        conn = sqlite3.connect(sqlite_file)
        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()
        c.execute('SELECT distinct HUC8 FROM {tn}'.format(tn=table_name))
        SQLCommander.HUC8s = c.fetchall()
        c.close()

        for i in range(0, len(SQLCommander.HUC8s)):
            self.huc8Listbox.insert(i, SQLCommander.HUC8s[i])

    def selectHUC8(self):

        self.huc10Listbox.delete(0, len(SQLCommander.HUC10s))
        (SQLCommander.selectedHUC8,) = self.huc8Listbox.curselection()
        selectedHUC8 = "'" + str(SQLCommander.HUC8s[SQLCommander.selectedHUC8]) + "'"
        sqlite_file = "REWS.sqlite"
        table_name = "REWS1"
        conn = sqlite3.connect(sqlite_file)
        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()
        sqlstatement = 'Select distinct HUC10 from {tn} where HUC8 = ' + selectedHUC8
        c.execute(sqlstatement.format(tn=table_name))
        SQLCommander.HUC10s = c.fetchall()
        c.close()
        SQLCommander.HUC10s = sorted(SQLCommander.HUC10s)

        for i in range(0, len(SQLCommander.HUC10s)):
            self.huc10Listbox.insert(i, SQLCommander.HUC10s[i])


    def selectHUC10(self):

        (SQLCommander.selectedHUC10,) = self.huc10Listbox.curselection()
        SQLCommander.selectedHUC10 = SQLCommander.HUC10s[SQLCommander.selectedHUC10]

        sqlite_file = "REWS.sqlite"
        con = sqlite3.connect(sqlite_file)
        c = con.cursor()
        table_name = "HUC10_" + str(SQLCommander.selectedHUC10)

        tb_exist = "SELECT name FROM sqlite_master WHERE type='table' AND name='" +table_name+ "'"

        if not c.execute(tb_exist).fetchone():

            arcpy.env.workspace = r"stream1"
            arcpy.env.overwriteOutput = True

            arcpy.MakeFeatureLayer_management('Flowlines.shp',
                                              'LIMS_Lyr')
            arcpy.MakeFeatureLayer_management('ReWatersheds1.shp',
                                              'Watershed_Lyr')

            sqlstatement = "HUC10 =" + "'" + str(SQLCommander.selectedHUC10) + "'"

            arcpy.SelectLayerByAttribute_management('Watershed_Lyr', 'NEW_SELECTION', sqlstatement)
            arcpy.SelectLayerByLocation_management('LIMS_Lyr', 'intersect', 'Watershed_Lyr', 0, "new_selection")
            arcpy.CopyRows_management('LIMS_Lyr', 'temp.csv')

            col1 = 'FID'
            col2 = 'OBJECTID'
            col3 = 'GNIS_ID'
            col4 = 'GNIS_Name'
            col5 = 'ReachCode'
            col6 = 'lengthM'


            c.execute(
                "CREATE TABLE {tn}({c1}, {c2}, {c3}, {c4}, {c5}, {c6});".format(tn=table_name, c1=col1, c2=col2, c3=col3,
                                                                                c4=col4, c5 = col5, c6 = col6))

            with open(r'temp.csv', 'rb') as fin:
                dr = csv.DictReader(fin)
                to_db = [(i[col1], i[col2], i[col3], i[col4], i[col5], i[col6]) for i in dr]

            c.executemany(
                "INSERT INTO {tn} ({c1}, {c2}, {c3}, {c4}, {c5}, {c6}) VALUES (?, ?, ?, ?, ?, ?);".format(tn=table_name, c1=col1,
                                                                                                    c2=col2, c3=col3, c4=col4,
                                                                                                    c5 = col5, c6 = col6), to_db)

        else:
            pass


        con.commit()
        con.close()

        conn = sqlite3.connect(sqlite_file)
        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()

        #Calculate number of streams with names
        nameSQL = 'SELECT DISTINCT GNIS_ID FROM {tn} WHERE GNIS_ID IS NOT NULL and GNIS_ID <> \' \''
        c.execute(nameSQL.format(tn=table_name))
        SQLCommander.nameList = c.fetchall()
        SQLCommander.nameTV.set(str(len(SQLCommander.nameList)))

        #Calculate number of mergable streams
        mergeSQL = 'SELECT DISTINCT ReachCode FROM {tn} WHERE GNIS_ID = \' \' or ReachCode = \' \' GROUP BY ReachCode HAVING COUNT(ReachCode)>1'
        c.execute(mergeSQL.format(tn=table_name))
        SQLCommander.mergeList = c.fetchall()
        SQLCommander.mergeTV.set(str(len(SQLCommander.mergeList)))

        #Calculate number of single streams
        singleSQL = 'SELECT OBJECTID FROM {tn} WHERE GNIS_ID = \' \' or ReachCode = \' \' GROUP BY ReachCode HAVING COUNT(ReachCode)<2'
        c.execute(singleSQL.format(tn=table_name))
        singleList = c.fetchall()
        SQLCommander.singleTV.set(str(len(singleList)))

        conn.commit()
        conn.close()

    def namesTL(self):

        SQLCommander.nameTL = tk.Toplevel()
        yloc = master.winfo_y()
        yloc = yloc + 300
        xloc = master.winfo_x()
        xloc = xloc + 75
        SQLCommander.nameTL.geometry('+%d+%d' % (xloc, yloc))

        SQLCommander.HUC10TV = tk.StringVar()
        SQLCommander.HUC10TV.set(SQLCommander.selectedHUC10)
        SQLCommander.counterTV = tk.StringVar()
        SQLCommander.counterTV.set("HitNext")
        SQLCommander.nameSQLStatement = tk.StringVar()
        SQLCommander.nameSQLStatement.set("Hit Next")
        SQLCommander.listnum = -1

        #Labels
        tk.Label(SQLCommander.nameTL, text = "HUC_10:").grid(row = 0)
        tk.Label(SQLCommander.nameTL, text = "Complete: ").grid(row = 1)
        tk.Label(SQLCommander.nameTL, text = "SQL Statment:  ").grid(row = 2)

        #HUC10 TV
        tk.Label(SQLCommander.nameTL, textvariable = SQLCommander.HUC10TV, width = 20).grid(row=0, column = 1)
        #Count TV
        tk.Label(SQLCommander.nameTL, textvariable = SQLCommander.counterTV).grid(row = 1, column = 1)
        #SQL Statment TV
        tk.Label(SQLCommander.nameTL, textvariable = SQLCommander.nameSQLStatement, wraplength = 100).grid(row=2, column=1)

        nextBut = tk.Button(SQLCommander.nameTL, text = "Next", width = 20, command = self.copyMechNames)
        nextBut.grid(row=1, column = 2, sticky = "N", padx = 5)
        backBut = tk.Button(SQLCommander.nameTL, text = "Back", width = 20, command = self.backMechNames)
        backBut.grid(row=2, column = 2, sticky = "N", padx = 5)

    def copyMechNames(self):

        SQLCommander.listnum += 1

        if SQLCommander.listnum < len(SQLCommander.nameList):
            GNIS_ID = str(SQLCommander.nameList[SQLCommander.listnum])
            sqlstatment = "GNIS_ID = '" + GNIS_ID + "'"
            SQLCommander.nameSQLStatement.set(sqlstatment)
            master.clipboard_append(sqlstatment)
            countString = str(SQLCommander.listnum + 1) + " out of " + str(len(SQLCommander.nameList))
            SQLCommander.counterTV.set(countString)

        else:
            empty = "----"
            SQLCommander.counterTV.set(empty)
            SQLCommander.nameSQLStatement("List Finished")
            endButton = tk.Button(SQLCommander.nameTL, text = "Done", command = SQLCommander.nameTL.destroy)
            endButton.grid(row=2, column=2)



    def backMechNames(self):

        if SQLCommander.listnum < 0:
            SQLCommander.listnum = 0
        else:
            SQLCommander.listnum -= 1
            GNIS_ID = str(SQLCommander.nameList[SQLCommander.listnum])
            sqlstatement = "GNIS_ID = '" + GNIS_ID + "'"
            SQLCommander.nameSQLStatement.set(sqlstatement)
            master.clipboard_append(sqlstatement)
            countString = str(SQLCommander.listnum + 1) + " out of " + str(len(SQLCommander.nameList))
            SQLCommander.counterTV.set(countString)


    def mergesTL(self):

        SQLCommander.mergeTL = tk.Toplevel()
        yloc = master.winfo_y()
        yloc = yloc + 300
        xloc = master.winfo_x()
        xloc = xloc + 75
        SQLCommander.mergeTL.geometry('+%d+%d' % (xloc, yloc))

        SQLCommander.HUC10TV = tk.StringVar()
        SQLCommander.HUC10TV.set(SQLCommander.selectedHUC10)
        SQLCommander.counterTV = tk.StringVar()
        SQLCommander.counterTV.set("HitNext")
        SQLCommander.nameSQLStatement = tk.StringVar()
        SQLCommander.nameSQLStatement.set("Hit Next")
        SQLCommander.listnum = -1

        #Labels
        tk.Label(SQLCommander.mergeTL, text = "HUC_10:").grid(row = 0)
        tk.Label(SQLCommander.mergeTL, text = "Complete: ").grid(row = 1)
        tk.Label(SQLCommander.mergeTL, text = "SQL Statment:  ").grid(row = 2)


        #HUC10 TV
        tk.Label(SQLCommander.mergeTL, textvariable = SQLCommander.HUC10TV, width = 20).grid(row=0, column = 1)
        #Count TV
        tk.Label(SQLCommander.mergeTL, textvariable = SQLCommander.counterTV).grid(row = 1, column = 1)
        #SQL Statment TV
        tk.Label(SQLCommander.mergeTL, textvariable = SQLCommander.nameSQLStatement, wraplength = 100).grid(row=2, column=1)

        nextBut = tk.Button(SQLCommander.mergeTL, text = "Next", width = 20, command = self.copyMechMerges)
        nextBut.grid(row=1, column = 2, sticky = "N", padx = 5)
        backBut = tk.Button(SQLCommander.mergeTL, text = "Back", width = 20, command = self.backMechMerges)
        backBut.grid(row=2, column = 2, sticky = "N", padx = 5)


    def copyMechMerges(self):

        SQLCommander.listnum += 1
        if SQLCommander.listnum < len(SQLCommander.mergeList):
            ReachCode = str(SQLCommander.mergeList[SQLCommander.listnum])
            sqlstatment = "ReachCode = '" + ReachCode + "'"
            SQLCommander.nameSQLStatement.set(sqlstatment)
            master.clipboard_append(sqlstatment)
            countString = str(SQLCommander.listnum + 1) + " out of " + str(len(SQLCommander.mergeList))
            SQLCommander.counterTV.set(countString)

        else:
            empty = "----"
            SQLCommander.counterTV.set(empty)
            SQLCommander.nameSQLStatement("List Finished")
            endButton = tk.Button(SQLCommander.nameTL, text="Done", command=SQLCommander.mergeTL.destroy)
            endButton.grid(row=2, column=2)


    def backMechMerges(self):

        if SQLCommander.listnum < 0:
            SQLCommander.listnum = 0
        else:
            SQLCommander.listnum -= 1
            ReachCode = str(SQLCommander.mergeList[SQLCommander.listnum])
            sqlstatement = "ReachCode = '" + ReachCode + "'"
            SQLCommander.nameSQLStatement.set(sqlstatement)
            master.clipboard_append(sqlstatement)
            countString = str(SQLCommander.listnum + 1) + " out of " + str(len(SQLCommander.mergeList))
            SQLCommander.counterTV.set(countString)

    def updateTable(self):
        (SQLCommander.selectedHUC10,) = self.huc10Listbox.curselection()
        SQLCommander.selectedHUC10 = SQLCommander.HUC10s[SQLCommander.selectedHUC10]

        sqlite_file = "REWS.sqlite"
        con = sqlite3.connect(sqlite_file)
        c = con.cursor()
        table_name = "HUC10_" + str(SQLCommander.selectedHUC10) + 'u'
        near_table = table_name + "_near"

        tb_exist = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + near_table + "'"

        thing = c.execute(tb_exist).fetchone()
        print thing

        if not c.execute(tb_exist).fetchone():

            arcpy.MakeFeatureLayer_management('Flowlines.shp',
                                              'LIMS_Lyr')
            arcpy.MakeFeatureLayer_management('ReWatersheds.shp',
                                              'Watershed_Lyr')

            sqlstatement = "HUC10 =" + "'" + str(SQLCommander.selectedHUC10) + "'"


            arcpy.SelectLayerByAttribute_management('Watershed_Lyr', 'NEW_SELECTION', sqlstatement)
            arcpy.SelectLayerByLocation_management('LIMS_Lyr', 'intersect', 'Watershed_Lyr', 0, "new_selection")
            arcpy.SelectLayerByAttribute_management('LIMS_Lyr', 'SUBSET_SELECTION', '"GNIS_ID" = \' \' or "ReachCode" = \' \'')
            arcpy.CopyRows_management('LIMS_Lyr', 'LIMS_NULLS.csv')

            #NT = near_table

            arcpy.GenerateNearTable_analysis('LIMS_Lyr', 'LIMS_Lyr', "nt", '1 Meters', 'NO_LOCATION', 'NO_ANGLE', 'All', 10)
            arcpy.MakeTableView_management("nt", "nt")
            arcpy.AddJoin_management('nt', "IN_FID", 'LIMS_Lyr', "FID")
            arcpy.CopyRows_management('nt', 'nt.csv')


            col1n = 'Rowid'
            col2n = 'nt_OBJECTID'
            col3n = 'nt_IN_FID'
            col4n = 'nt_NEAR_FID'
            col5n = 'nt_NEAR_DIST'
            col6n = 'nt_NEAR_RANK'
            col7n = 'FID'
            col8n = 'OBJECTID'
            col9n = 'GNIS_ID'
            col10n = 'GNIS_Name'
            col11n = 'ReachCode'
            col12n = 'lengthM'

            c.execute(
                "CREATE TABLE {tn}({c1}, {c2}, {c3}, {c4}, {c5}, {c6}, {c7}, {c8}, {c9}, {c10}, {c11}, {c12});".format(
                    tn=near_table, c1=col1n, c2=col2n, c3=col3n, c4=col4n, c5=col5n, c6=col6n, c7=col7n, c8=col8n,
                    c9=col9n, c10 = col10n, c11 = col11n, c12 = col12n))

            with open(r'C:\Users\cfelt\Documents\python\scripts27\stream1\nt.csv', 'rb') as fin:
                dr = csv.DictReader(fin)
                to_db = [(i[col1n], i[col2n], i[col3n], i[col4n], i[col5n], i[col6n], i[col7n], i[col8n], i[col9n], 
                          i[col10n], i[col11n], i[col12n]) for i in dr]

            c.executemany(
                "INSERT INTO {tn} ({c1}, {c2}, {c3}, {c4}, {c5}, {c6}, {c7}, {c8}, {c9}, {c10}, {c11}, {c12}) VALUES "
                "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);".format(tn=near_table, c1=col1n, c2=col2n, c3=col3n, c4=col4n, 
                                                               c5=col5n, c6=col6n, c7=col7n, c8=col8n, c9=col9n, 
                                                               c10 = col10n, c11 = col11n, c12 = col12n), to_db)

        else:
            pass

        con.commit()
        con.close()


    def singlesTL(self):

        self.updateTable()

        SQLCommander.singleTL = tk.Toplevel()
        yloc = master.winfo_y()
        yloc = yloc + 300
        xloc = master.winfo_x()
        xloc = xloc + 75
        SQLCommander.singleTL.geometry('+%d+%d' % (xloc, yloc))

        SQLCommander.totalLengthTV = tk.StringVar()
        SQLCommander.totalLengthTV.set(SQLCommander.totalLength)



        #Entry
        tk.Label(master = SQLCommander.singleTL, text = "OBJECTID").grid(row = 0)
        SQLCommander.objectid_entry = tk.Entry(master = SQLCommander.singleTL, width = 20)
        SQLCommander.objectid_entry.grid(row=1, pady = 5, padx = 2.5)
        SQLCommander.checkboxTV = tk.StringVar()
        SQLCommander.checkboxTV.set("NO_CLIPBOARD")
        clipboard_checkbox = tk.Checkbutton(SQLCommander.singleTL, text="Use Clipboard", variable=SQLCommander.checkboxTV, onvalue = "CLIPBOARD", offvalue = "NO_CLIPBOARD")
        clipboard_checkbox.grid(row = 3)
        clipboard_checkbox.bind("<1>", self.getClipboard)

        #Total Length
        tk.Label(master = SQLCommander.singleTL, text = "Total Length").grid(row = 0, column = 1)
        tk.Label(master = SQLCommander.singleTL, text = "TBD").grid(row=1, column = 1)

        #Manual
        manBut = tk.Button(master = SQLCommander.singleTL, text = "Manual", width = 15, command = self.nearGenerate)
        manBut.grid(row=4, pady = 5)
        tk.Label(master = SQLCommander.singleTL, text = "TBD", width = 15, relief = "groove", pady = 5).grid(row=4, column = 1)
        manBut.bind("<1>", self.f)

        #Choice
        optionBut = tk.Button(master = SQLCommander.singleTL, text = "Option", width = 15, command = self.nearGenerate)
        optionBut.grid(row=5, pady = 5)
        tk.Label(master = SQLCommander.singleTL, text = "TBD", width = 15, relief = "groove", pady = 5).grid(row=5, column = 1)
        optionBut.bind("<1>", self.g)

        #Auto
        autoBut = tk.Button(master = SQLCommander.singleTL, text = "Auto", width = 15, command = self.nearGenerate)
        autoBut.grid(row=6, pady = 5)
        tk.Label(master = SQLCommander.singleTL, textvariable = SQLCommander.totalLengthTV, width = 15, relief = "groove", pady = 5).grid(row=6, column = 1)
        autoBut.bind("<1>", self.h)

    def nearGenerate(self, OBJECTID = "Nothing"):

        nfidList = []

        print SQLCommander.checkbox_switch

        if SQLCommander.checkbox_switch == 'on':
            OBJECTID = str(SQLCommander.selection_clip)
            SQLCommander.checkbox_switch = 'off'
            SQLCommander.objectid_entry.insert(0,str(SQLCommander.selection_clip))
            if len(OBJECTID) > 6:
                "Hit Button"
            else:
                pass
            OBJECTID = str(OBJECTID)
            SQLCommander.repeatList.append(OBJECTID)
            SQLCommander.entryBool = False
        elif OBJECTID == "Nothing":
            OBJECTID = SQLCommander.objectid_entry.get()
            OBJECTID = str(OBJECTID)
            SQLCommander.singleSQLStatement = "LIMS_Flowlines_ID1.OBJECTID = " + OBJECTID
            master.clipboard_clear()
            master.clipboard_append(SQLCommander.singleSQLStatement)
            SQLCommander.repeatList.append(OBJECTID)
            SQLCommander.entryBool = True
        else:
            OBJECTID = str(OBJECTID)
            SQLCommander.repeatList.append(OBJECTID)
            SQLCommander.entryBool = False

        sqlite3_file = "REWS.sqlite"
        conn = sqlite3.connect(sqlite3_file)
        conn.row_factory = lambda cursor, row: row[:]
        c = conn.cursor()

        limsTable = "HUC10_" + str(SQLCommander.selectedHUC10) + "u"
        near_table = limsTable + "_near"

        col1 = 'nt_IN_FID'
        col2 = 'OBJECTID'
        col3 = 'lengthM'
        col4 = 'nt_NEAR_FID'

        join_sql = "select {c1}, {c2}, {c3}, {c4} from {t1} where OBJECTID = '" + OBJECTID + "'"

        join_sql = join_sql.format(c1=col1, c2=col2, c3=col3, c4=col4, t1=near_table)

        try:
            c.execute(join_sql)

            #get the near fids
            SQLCommander.fid_list = c.fetchall()
            near_fid_list = [(i[3]) for i in SQLCommander.fid_list]

            for nfid in near_fid_list:

                skip_nfid_repeat = nfid in SQLCommander.repeatList
                skip_nfid_drop = nfid in SQLCommander.dropList

                if skip_nfid_repeat == True or skip_nfid_drop == True:
                    pass
                else:
                    nfidList.append(nfid)
                    subSQL = "select {c2}, {c3} from {t1} where FID = '" + nfid + "'"
                    subSQL = subSQL.format(t1 = near_table, c2 = col2, c3 = col3)
                    c.execute(subSQL)
                    nfidSQLList = c.fetchall()
                    SQLCommander.fidList.append(nfidSQLList[0][0])
                    SQLCommander.lengthList.append(nfidSQLList[0][1])


            conn.commit()
            conn.close()


            if SQLCommander.singleButtonPress == SQLCommander.manualButtonPress: #manBut
                print "manual button"



                searchScreen = tk.Toplevel()

                yloc = SQLCommander.singleTL.winfo_y()
                xloc = SQLCommander.singleTL.winfo_x()
                xwid = SQLCommander.singleTL.winfo_width()
                xloc = xloc +  xwid + 25 + SQLCommander.moveDisplayRight
                searchScreen.geometry('+%d+%d' % (xloc, yloc))
                searchScreen.update_idletasks()

                n = 0
                for nl in SQLCommander.fidList:
                    skipobj = SQLCommander.fidList[n] in SQLCommander.repeatList

                    if skipobj == True:
                        pass
                    else:
                        tk.Label(master = searchScreen, text = round(float(SQLCommander.lengthList[n]))).grid(row=n+1, column=2)
                        tk.Button(master = searchScreen, text = SQLCommander.fidList[n], command = lambda n=n: self.searchBut(SQLCommander.fidList[n], SQLCommander.lengthList[n])).grid(row=n+1)
                        tk.Button(master = searchScreen, text = "Search", command = lambda n=n: self.nearGenerate(SQLCommander.fidList[n])).grid(row=n+1, column=1)
                    SQLCommander.repeatList.append((SQLCommander.fidList[n]))
                    n += 1


            #########################################################################################


            elif SQLCommander.singleButtonPress == SQLCommander.choiceButtonPress:
                print "choice button"

                n = 0
                s = 0
                deleteList = []
                for nl in SQLCommander.fidList:
                    skipobj = SQLCommander.fidList[n] in SQLCommander.repeatList
                    skipDrop = SQLCommander.fidList[n] in SQLCommander.dropList

                    if skipobj == True or skipDrop == True:
                        deleteList.append(SQLCommander.fidList[n])
                    else:
                        s += 1
                        print "fidList =", SQLCommander.fidList[n]
                        # print "lengthList = ", SQLCommander.lengthList

                    SQLCommander.repeatList.append(SQLCommander.fidList[n])
                    n += 1

                for d in deleteList:
                    if d in SQLCommander.fidList:
                        SQLCommander.fidList.remove(d)


                if s==0:
                    master.clipboard_clear()
                    master.clipboard_append(SQLCommander.singleSQLStatement)
                    SQLCommander.dropList.append(OBJECTID)
                    SQLCommander.repeatList = []
                    SQLCommander.tlNumber +=1
                    SQLCommander.totalLength = 0
                else:

                    SQLCommander.singleSQLStatement = SQLCommander.singleSQLStatement + ' OR LIMS_Flowlines_ID1.OBJECTID = ' + str(OBJECTID)
                    master.clipboard_clear()
                    master.clipboard_append(SQLCommander.singleSQLStatement)
                    SQLCommander.totalLength = SQLCommander.totalLength + SQLCommander.lengthList[0]
                    self.nearGenerate(SQLCommander.fidList[0])

            #########################################################################################

            else:
                # print "auto button"
                n = 0
                s = 0
                deleteList = []
                for nl in SQLCommander.fidList:
                    skipobj = SQLCommander.fidList[n] in SQLCommander.repeatList
                    skipDrop = SQLCommander.fidList[n] in SQLCommander.dropList

                    if skipobj == True or skipDrop == True:
                        deleteList.append(SQLCommander.fidList[n])
                    else:
                        s += 1

                    SQLCommander.repeatList.append(SQLCommander.fidList[n])
                    n += 1

                for d in deleteList:
                    if d in SQLCommander.fidList:
                        SQLCommander.fidList.remove(d)


                if s==0:

                    if SQLCommander.totalLength > SQLCommander.previouslength:

                        SQLCommander.previouslength = SQLCommander.totalLength
                        SQLCommander.longestSQLStatement = SQLCommander.singleSQLStatement
                        SQLCommander.longestLength = SQLCommander.totalLength
                        master.clipboard_clear()
                        master.clipboard_append(SQLCommander.longestSQLStatement)

                    else:

                        master.clipboard_clear()
                        master.clipboard_append(SQLCommander.longestSQLStatement)

                    SQLCommander.dropList.append(OBJECTID)
                    SQLCommander.repeatList = []
                    SQLCommander.tlNumber += 1
                    SQLCommander.totalLength = 0

                    if SQLCommander.entryBool and len(SQLCommander.fidList) == 0:
                        master.clipboard_clear()
                        master.clipboard_append(SQLCommander.longestSQLStatement)
                        SQLCommander.totalLengthTV.set(SQLCommander.longestLength)
                    else:

                        self.nearGenerate()

                else:
                    lengthSQL = "select {c3} from {t1} where OBJECTID = '" + SQLCommander.fidList[0] + "'"
                    lengthSQL = lengthSQL.format(c3 = col3, t1 = near_table)
                    sqlite3_file = "REWS_Test1.sqlite"
                    conn = sqlite3.connect(sqlite3_file)
                    conn.row_factory = lambda cursor, row: row[:]
                    c = conn.cursor()
                    c.execute(lengthSQL)
                    lengthNList = c.fetchall()
                    lengthN = round(float(lengthNList[0][0]), 2)
                    conn.commit()
                    conn.close()
                    SQLCommander.singleSQLStatement = SQLCommander.singleSQLStatement + ' OR LIMS_Flowlines_ID1.OBJECTID = ' + str(
                        SQLCommander.fidList[0])
                    SQLCommander.totalLength = SQLCommander.totalLength + lengthN
                    self.nearGenerate(SQLCommander.fidList[0])

                SQLCommander.dropList.append(OBJECTID)

        except sqlite3.OperationalError:
            print "Empty Table"

    def f(self, event):
        SQLCommander.manualButtonPress = event.widget
        SQLCommander.singleButtonPress = event.widget
        SQLCommander.longestSQLStatement = ""
        SQLCommander.singleSQLStatement = ""
        SQLCommander.repeatList = []
        SQLCommander.totalLength = 0
        SQLCommander.previouslength = 0


    def g(self, event):
        SQLCommander.choiceButtonPress = event.widget
        SQLCommander.singleButtonPress = event.widget
        SQLCommander.longestSQLStatement = ""
        SQLCommander.singleSQLStatement = ""
        SQLCommander.repeatList = []
        SQLCommander.totalLength = 0
        SQLCommander.previouslength = 0


    def h(self, event):
        SQLCommander.autoButtonPress = event.widget
        SQLCommander.singleButtonPress = event.widget
        SQLCommander.longestSQLStatement = ""
        SQLCommander.singleSQLStatement = ""
        SQLCommander.repeatList = []
        SQLCommander.totalLength = 0
        SQLCommander.previouslength = 0

    def getClipboard(self, event):
        SQLCommander.clipboard = SQLCommander.checkboxTV.get()
        SQLCommander.checkbox_switch = 'on'
        SQLCommander.selection_clip = master.selection_get(selection="CLIPBOARD")

    def searchBut(self, objectid, length_add):
        SQLCommander.singleSQLStatement = SQLCommander.singleSQLStatement + ' OR LIMS_Flowlines_ID1.OBJECTID = ' + str(objectid)
        master.clipboard_clear()
        master.clipboard_append(SQLCommander.singleSQLStatement)
        SQLCommander.totalLength = SQLCommander.totalLength + float(length_add)
        singleTLWidth = SQLCommander.singleTL.winfo_width()
        SQLCommander.moveDisplayRight += SQLCommander.moveDisplayRight + singleTLWidth
        toText = '->' + str(objectid)





if __name__ == "__main__":
    master = tk.Tk()
    sqlCom = SQLCommander(master)
    master.mainloop()
