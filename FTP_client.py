from ftplib import FTP
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
import requests
import json
import time


class MyWindow:
    FTPConnected = False
    ftp = FTP()

    def __init__(self, win):
        win.title('Server files manager')
        self.lbl1=Label(win, text='Username')
        self.lbl2=Label(win, text='Password')
        self.lbl3=Label(win, text='Host')
        self.lbl4=Label(win, text='Port')
        self.t1=Entry(win)
        self.t1.insert(0, 'me')
        self.t2=Entry(bd=3, show="*")
        self.t2.insert(0, '1234')
        self.t3=Entry(win)
        self.t3.insert(0, 'localhost')
        self.t4=Entry(win, width=5)
        self.t4.insert(0, '2121') 
        self.btn1 = Button(win, text='Add')
        self.btn2=Button(win, text='Subtract')
        self.lbl1.place(x=10, y=12)
        self.t1.place(x=80, y=10)
        self.lbl2.place(x=245, y=12)
        self.t2.place(x=310, y=10)
        self.lbl3.place(x=480, y=12)
        self.t3.place(x=520, y=10)
        self.lbl4.place(x=690, y=12)
        self.t4.place(x=725, y=10)
        self.b1=Button(win, text='Connect', command=self.FTPConnect)
        self.b1.place(x=800, y=6)
        
        labelframe = LabelFrame(win, text="File uploading", width=870, height=70)
        labelframe.place(x=10, y=40)
        self.openFileButton = Button(
            labelframe,
            text='Select a File',
            command=self.selectFile
        )
        self.openFileButton.place(x=10, y=10)
        self.fileLbl=Label(labelframe, text='No file selected')
        self.fileLbl.place(x=120, y=16)
        left = Label(labelframe, text="Description")
        left.place(x=270, y=16)
        self.description=Entry(labelframe, width=60)
        self.description.place(x=350,y=14)
        self.uploadFileButton = Button(
            labelframe,
            text='Upload',
            command=self.uploadFile
        )
        self.uploadFileButton.place(x=790, y=10)

        left = Label(win, text="Files on server:")
        left.place(x=10, y=127)

        frame = Frame(win)
        frame.place(x=10, y=150)

        self.tv = ttk.Treeview(frame, columns=(1, 2, 3), show='headings', height=8)
        self.tv.pack(side=LEFT)

        self.tv.heading(1, text="name")
        self.tv.heading(2, text="description")
        self.tv.heading(3, text="uploaded")

        self.tv.column(1, width = 100, anchor = W)
        self.tv.column(2, width = 605, anchor = W)
        self.tv.column(3, width = 150, anchor = W)

        sb = Scrollbar(frame, orient=VERTICAL)
        sb.pack(side=RIGHT, fill=Y)
        self.tv.config(yscrollcommand=sb.set)
        sb.config(command=self.tv.yview)

        btnDownloadSelected = Button(win, text="Download", command=self.downloadSelected)
        btnDownloadSelected.place(x=785, y=340)

        self.hostname = ''
        self.username = ''
        self.filePath = ''
        self.fileName = ''

    def registerRequest(self):
        url = 'http://' + self.t3.get() + ':8081/register'
        myobj = {'Username': self.t1.get(),
        'Password': self.t2.get()}

        requests.post(url, json = myobj, headers={"Content-Type": "application/json"})
            

    def FTPConnect(self):
        if not self.FTPConnected:
            if self.t3.get() == '' or self.t1.get() == '' or self.t2.get() == '':
                messagebox.showwarning(title='Empty filed(s)', message='Provide all data for connection')
            else:

                self.registerRequest()

                time.sleep(0.2)

                self.hostname = self.t3.get()
                self.ftp.connect(self.hostname, 2121)
                try:
                    self.username = self.t1.get()
                    self.ftp.login(self.t1.get(), self.t2.get())
                    
                except Exception:
                    messagebox.showwarning(title='Account', message='Username or password is incorrect')
                    return

                
                response = str(self.ftp.getwelcome())
            
                if '220' in response:
                    self.FTPConnected = True
                    self.b1['text'] = 'Disconnect'

                    self.getFiles()
        else:
            self.ftp.close()
            self.FTPConnected = False
            self.b1['text'] = 'Connect'
            self.username = ''
            self.hostname = ''

    def selectFile(self):
        filetypes = (
            ('All files', '*.*'),
            ('text files', '*.txt')
        )
        f = fd.askopenfile(filetypes=filetypes)
        self.filePath = f.name
        self.fileName = f.name[f.name.rindex('/')+1:]
        self.fileLbl.config(text=self.fileName)
    
    def uploadFile(self):
        if not self.FTPConnected:
            messagebox.showwarning(title='Not connected', message='Connect to an FTP server')
        else:
            if self.filePath == '' or self.fileName == '':
                messagebox.showwarning(title='File selection', message='Select a file first')
            else:
                self.ftp.storbinary('STOR '+ self.fileName, open(self.filePath, 'rb'))
                
                messagebox.showinfo('Sucess', 'File uploaded')

                self.registerFile(self.username, self.fileName, self.description.get())

                self.filePath = ''
                self.fileName = ''
                self.description.delete(0,END)
                self.description.insert(0,'')
                self.fileLbl.config(text='')
        
        self.getFiles()

    def registerFile(self, username, fileName, description):
        url = 'http://' + self.hostname + ':8081/new'
        myobj = {'Username': username,
        'Name': fileName,
        'Description': description}
        print(url, myobj)

        response = requests.post(url, json = myobj, headers={"Content-Type": "application/json"})
        print(response)

    def getFiles(self):
        if not self.FTPConnected:
            messagebox.showwarning(title='Not connected', message='Connect to an FTP server')
        else:
            print("will get")
            url = 'http://' + self.hostname + ':8081/all'
            print(url)
            response = requests.get(url)
            if response.text != '':
                self.fileList = json.loads(response.text)
                print(self.fileList)
                self.reloadContents()

    def reloadContents(self):
        self.tv.delete(*self.tv.get_children())
        for id, data in enumerate(self.fileList):
            print("item:", id, data)
            self.tv.insert(parent='', index=id, iid=id, values=(data['Name'], data['Description'], data['Uploaded']))

    def downloadSelected(self):
        item = int(self.tv.selection()[0])
        if not self.FTPConnected:
            messagebox.showwarning(title='Not connected', message='Connect to an FTP server')
        else:
            filename = self.fileList[item]['Name']
            print(filename)
            localfile = open(filename, 'wb')
            self.ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
            self.ftp.quit()

window=Tk()
mywin=MyWindow(window)
window.title('Server files manager')
window.geometry("900x390+10+10")
window.resizable(False, False)
window.mainloop()

