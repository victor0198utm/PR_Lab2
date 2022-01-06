from tkinter import *
from tkinter import ttk
import smtplib, ssl

class MyWindow:

    def __init__(self, win):
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
        window.title('Write email')
        window.geometry("600x470+10+10")
        window.resizable(False, False)
        writerWindow = WW(window, self.t1.get(), self.t2.get())

class WW:

    def __init__(self, win, email, password):
        
        self.email = email
        self.password = password
        self.port = 465
        self.smtp_server = "smtp.gmail.com"
        
        self.lbl1=Label(win, text='To')
        self.t1=Entry(win, width=75)
        self.t1.insert(0, '')
        self.lbl1.place(x=10, y=12)
        self.t1.place(x=40, y=10)
        
        self.left = Label(win, text="Message")
        self.left.place(x=10, y=36)        

        btnSend = Button(win, text="Send", command=self.send_msg)
        btnSend.place(x=500, y=420)
        
        self.text = Text(win)
        self.text.place(x=10, y=60)
        
    def send_msg(self):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.email, self.password)
            server.sendmail(self.email, self.t1.get(), self.text.get(1.0, "end-1c"))
        self.t1.delete(0, 'end')
        self.text.delete('1.0', END)
        
window=Tk()
mywin=MyWindow(window)
window.title('Log in')
window.geometry("250x130+10+10")
window.resizable(False, False)
window.mainloop()

