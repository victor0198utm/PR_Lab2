import  poplib
from tkinter import *
from tkinter import ttk
import smtplib, ssl

i=0
data = ['-1']
class MyWindow:

    def __init__(self, win):
        win.title('Server files manager')
        self.lbl1=Label(win, text='Email')
        self.lbl2=Label(win, text='Password')
        self.t1=Entry(win)
        self.t1.insert(0, '')
        self.t2=Entry(bd=3, show="*")
        self.t2.insert(0, '')
        self.lbl1.place(x=10, y=12)
        self.t1.place(x=80, y=10)
        self.lbl2.place(x=10, y=52)
        self.t2.place(x=80, y=50)
        
        btnDownloadSelected = Button(win, text="Log in", command=self.openWriter)
        btnDownloadSelected.place(x=140, y=90)

    
    def openWriter(self):
        window=Tk()
        window.title('Server files manager')
        window.geometry("690x410+10+10")
        window.resizable(False, False)
        writerWindow = WW(window, self.t1.get(), self.t2.get())

class WW:

    def __init__(self, win, email, password):
        win.title('Messages')
        
        self.email = email
        self.password = password
        self.port = 465
        self.smtp_server = "smtp.gmail.com"
        
        self.Lb1 = Listbox(win, height=22, width=30)
        self.Lb1.place(x=10, y=10)
        self.Lb1.bind('<<ListboxSelect>>', self.displayMessage)
        
        btnSend = Button(win, text="Refresh", command=self.get_msgs)
        btnSend.place(x=550, y=370)
        
        self.text = Text(win, width=60)
        self.text.place(x=240, y=10)
        
        
    def get_msgs(self): 
        # Connect to the mail box 
        Mailbox = poplib.POP3_SSL('pop.googlemail.com', '995') 
        Mailbox.user(self.email) 
        Mailbox.pass_(self.password) 
        print(Mailbox.list())
        NumofMessages = len(Mailbox.list()[1])
        msgs = list()
        for i in range(NumofMessages):
            strmsg=str()
            for msg in Mailbox.retr(NumofMessages-i)[1]:
        #        print(msg.decode("utf-8"))
                if("From: " in msg.decode("utf-8")):
                    strmsg=strmsg+msg.decode("utf-8")+'\n'
                else:
                    strmsg=strmsg+msg.decode("utf-8")
        #        print("i=",i)
            msgs.append(strmsg)
        #print(len(msgs))
        #print(msgs)
        Mailbox.quit()
        
        for msg in reversed(msgs):
            newMsg = str()
            if("From: " in msg):
                print(msg)
                start = msg.index('From: ')
                end = msg.index('\n', start, len(msg))
                i=int()
                if data[len(data)-1] == '-1':
                    i=0
                else:
                    print('len(data)',len(data))
                    print('data[len(data)-1]',data[len(data)-1])
                    i=int(data[len(data)-1][0])+1
                print('i=',i)
                newMsg = str(i) +'~'
                newMsg = newMsg + msg[start:end] + '~'
                self.Lb1.insert(1,msg[start:end])
                
            start = msg.index('Content-Type: text/plain; charset="UTF-8"')+41
            end = msg.index('--', start, len(msg))
            newMsg = newMsg + msg[start:end]
            data.append(newMsg)
            
    
        print(data)
    
    def displayMessage(self, event):
        selected = len(data) - 2 - self.Lb1.curselection()[0]
        print("selected:",selected)
        for mes in data:
            if str(selected) == mes[0]:
                print(mes)
                self.text.delete('1.0', END)
                start=mes.index('~')
                print('start1', start)
                start=mes.index('~', start+1, len(mes))
                print('start2', start)
                
                self.text.insert(INSERT, mes[start+1:])
            
        
window=Tk()
mywin=MyWindow(window)
window.title('Log in')
window.geometry("250x130+10+10")
window.resizable(False, False)
window.mainloop()

