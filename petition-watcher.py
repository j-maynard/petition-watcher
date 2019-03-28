#!/usr/local/bin/python3
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import requests
import time
from datetime import datetime
import threading
import sys
import queue
from multiprocessing.dummy import Pool as ThreadPool 

def now():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Options
autoRefreshTime = 20
loadThreadCount = 10

class Petition:
    def __init__(self, number, action=None, background=None, initalCount=0, state=None, data=None):
        self.number = number
        self.data = data
        self.action = action
        self.background = background
        self.initalCount = initalCount
        self.currentCount = initalCount
        self.state = state
        if action is None and background is None:
            self.refreshData()
    
    def getFormatedCount(self):
        return '{:,d}'.format(self.currentCount)

    def refreshData(self):
        attempt = 4
        r = None
        while attempt:
            attempt = attempt -1
            try:
                r = requests.get("https://petition.parliament.uk/petitions/%s.json" % (self.number))
                self.data = r.json()
                self.action = self.data['data']['attributes']['action']
                self.background = self.data['data']['attributes']['background']
                self.initalCount = int(self.data['data']['attributes']['signature_count'])
                self.currentCount = int(self.data['data']['attributes']['signature_count'])
                self.state = self.data['data']['attributes']['state']
                break
            except:
                print("Unable to connect to petitions web site.  Shall retry %d times." % (attempt))
        if self.data is None:
            print("Unable to connect to peitions web site and get petition data, exiting...")
            quit()

    def updateCount(self):
        attempt = 4
        r = None
        while attempt:
            attempt = attempt - 1
            try:
                requestAddress = "https://petition.parliament.uk/petitions/%s/count.json" % (self.number)
                r = requests.get(requestAddress)
                if r is not None:
                    break
            except:
                print('Unable to connect to peitions web site.  Shall retry %d more times' % (attempt))
                time.sleep(1)
        if r is None:
            print('Unable to get petition count.  Will reattempt at next refresh.')
            return
        data = r.json()
        self.currentCount = data['signature_count']
        return self.getFormatedCount()

class PetitionWindow:
    def __init__(self, petition_number):
         self.petition = Petition(petition_number)
         self.window = Toplevel()
         self.window.title("Petition Details")
         #OptionMenu(self.window, "Peitions...", *petitions.values()).pack()
         top_frame = tk.Frame(self.window)#.pack(fill='y', expand=1)
         middle_frame = tk.Frame(self.window)#.pack(fill='y', expand=1)
         bottom_frame = tk.Frame(self.window)#.pack(side = "bottom", fill='y', expand=1)
         self.actionLbl = tk.Label(top_frame, text = self.petition.action)
         self.actionLbl.pack()
         self.countLbl = tk.Label(middle_frame, text = "Peition Count")
         self.countLbl.pack()
         self.currentCountLbl = tk.Label(middle_frame, text = self.petition.getFormatedCount(), font = ("Ubuntu Mono", 36))
         self.currentCountLbl.pack()
         self.updateTime = tk.Label(middle_frame, text = "Last updated: " + now())
         self.updateTime.pack()
         self.refreshBtnLabel = "Refresh (%d)" % (autoRefreshTime)
         self.refreshBtn = tk.Button(bottom_frame, text = self.refreshBtnLabel, command = self.refreshBtnClick)
         self.refreshBtn.pack(side = "left")
         self.infoBtn = tk.Button(bottom_frame, text = "Info", command = self.infoBtnClick)
         self.infoBtn.pack(side = "left")
         self.quitBtn = tk.Button(bottom_frame, text = "Close", command = self.quitBtnClick)
         self.quitBtn.pack(side = "left")
         self.refreshBtnClicked = 0
         top_frame.pack(fill='y', expand=1)
         middle_frame.pack(fill='y', expand=1)
         bottom_frame.pack(side = "bottom", fill='y', expand=1)
         self.countDown = autoRefreshTime
         self.window.after(1000, self.autoRefresh)

    def quitBtnClick(self):
        self.window.destroy()

    def refresh(self):
        self.countDown = autoRefreshTime
        self.refreshBtn.config(text = "Refresh (%d)" % (self.countDown))
        self.currentCountLbl.config(text = self.petition.updateCount())
        self.updateTime.config(text = "Last updated: " + now())

    def refreshBtnClick(self):
        self.refresh()

    def infoBtnClick(self):
        messagebox.showinfo("Description", self.petition.background)

    def autoRefresh(self):
        if self.countDown == 0:
            self.refresh()
            self.window.after(1000, self.autoRefresh)
        else:
            self.countDown = self.countDown - 1
            self.refreshBtn.config(text = "Refresh (%d)" % (self.countDown))
            self.window.after(1000, self.autoRefresh)

class AllPetitionsWindow:
    def loadPetitionsFromPage(self, requestUrl):
        #TODO change to a retry pattern
        try:
            r = requests.get(requestUrl)
        except:
            print("Unable to make inital connection to petitions web site.  Exiting...")
            quit()
        list_data = r.json()
        for raw_petition_data in list_data['data']:
            peition = Petition(
                raw_petition_data['id'],
                raw_petition_data['attributes']['action'],
                raw_petition_data['attributes']['background'],
                raw_petition_data['attributes']['signature_count'],
                raw_petition_data['attributes']['state'],
                raw_petition_data['attributes']
            )
            self.petitions[raw_petition_data['id']] = peition
        pages = re.findall('\d+',list_data['links']['last'])
        return int(pages[len(pages)-1])

    def init(self):
        initalRequestUrl = "https://petition.parliament.uk/petitions.json?state=open"
        totalPages = self.loadPetitionsFromPage(initalRequestUrl)
        pageUrls = []
        for pageNo in range(2, totalPages+1):
            pageUrls.append( "https://petition.parliament.uk/petitions.json?page=%d\u0026state=open" % (pageNo))
        requestPool = ThreadPool(loadThreadCount)
        requestPool.map(self.loadPetitionsFromPage, pageUrls)
        requestPool.close()
        requestPool.join()
        print("Total Peitiosn = ", len(self.petitions))

    def tree_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col == 'Sig Count' or col == 'Number':
            l.sort(key=lambda t: int(t[0].replace(',','')), reverse=reverse)
        else:
            l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
                self.tree_sort_column(tv, col, not reverse))

    def treeDoubleClick(self, event):
        item = self.tree.identify('item',event.x,event.y)
        #print("you clicked on", self.tree.item(item,"values")[2])
        PetitionWindow(self.tree.item(item,"values")[2])

    def __init__(self):
        self.petitions = {}
        self.init()
        root = tk.Tk()
        root.title("Root Window")
        columns=('Action','Sig Count', 'Number', 'State')
        self.tree = ttk.Treeview( root, columns=columns)
        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.tree_sort_column(self.tree, _col, False))
        
        self.tree.heading('#1', text='Action')
        self.tree.heading('#2', text='Sig Count')
        self.tree.heading('#3', text='Number')
        self.tree.heading('#4', text='State')
        
        self.tree.column('#1', stretch=tk.YES)
        self.tree.column('#2', stretch=tk.YES)
        self.tree.column('#3', stretch=tk.YES)
        self.tree.column('#4', stretch=tk.YES)
        self.tree.bind("<Double-1>", self.treeDoubleClick)
        
        for petition in self.petitions.values():
            self.tree.insert('', 'end', text='', values=(petition.action, '{:,d}'.format(petition.initalCount), petition.number, petition.state))
        self.tree.pack()
        root.mainloop()

def main():
    AllPetitionsWindow()

if __name__=="__main__":
    main()
