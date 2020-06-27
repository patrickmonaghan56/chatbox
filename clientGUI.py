import socket
import tkinter as tk
from tkinter import messagebox
import threading
import sys

Master = tk.Tk()
Master.title("Client")
username = " "
Master.configure(bg='red')

NameCFrame = tk.Frame(Master,bg='red')
lblName = tk.Label(NameCFrame, text = "Name:").pack(side=tk.LEFT)
Name = tk.Entry(NameCFrame)
Name.pack(side=tk.LEFT)
Connect = tk.Button(NameCFrame, text="Connect", command=lambda : connect())
Connect.pack(side=tk.LEFT)
NameCFrame.pack(side=tk.TOP)

display = tk.Frame(Master,bg='red')
scrollBar = tk.Scrollbar(display)
scrollBar.pack(side=tk.LEFT, fill=tk.Y)
tkChat = tk.Text(display, height=25, width=50)
tkChat.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
tkChat.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkChat.yview)
tkChat.config(yscrollcommand=scrollBar.set, highlightbackground="grey", state="disabled")
display.pack(side=tk.TOP)


TextFrame = tk.Frame(Master,bg='red')
tkMessage = tk.Text(TextFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey")
tkMessage.bind("<Return>", (lambda event: getMessage(tkMessage.get("1.0", tk.END))))
sendbutton=tk.Button(TextFrame, text="Send", command=lambda : getMessage(tkMessage.get("1.0", tk.END)))
sendbutton.pack(side=tk.RIGHT)
TextFrame.pack(side=tk.BOTTOM)


def connect():
    global username, client
    if len(Name.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter a user name")
    else:
        username = Name.get()
        serverconnect(username)


# network client
client = None
HOST_ADDR = "192.168.1.242"
HOST_PORT = 13000

def serverconnect(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        print(name)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("attempt to connect to server")
        client.connect((HOST_ADDR, HOST_PORT))
        #name in byte string for send
        nameb = name.encode('utf-8')
        print("sending name to server")
        client.send(nameb) # Send name to server after connecting

        Name.config(state=tk.DISABLED)
        Connect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        # start a thread to keep receiving message from server
        # do not block the main thread :)
        print("starting recieve thread")
        threading._start_new_thread(receive,(client, "m"))
    except Exception:
        e = sys.exc_info()[0]
        print(e)
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


def receive(sck, m):
    while True:
        
        from_server = sck.recv(256)

        if not from_server: break

        # display message from server on the chat window

        # enable the display area and insert the text and then disable.
        texts = tkChat.get("1.0", tk.END).strip()
        tkChat.config(state=tk.NORMAL)
        #decode bytes to str
        displaystr = from_server.decode('utf-8')
        #check if there is previous text in the chat to keep track of
        if len(texts) < 1:
            tkChat.insert(tk.END, displaystr)
        else:
            tkChat.insert(tk.END, "\n\n"+ displaystr)
        #redisables chat so you cant type in the chat display
        tkChat.config(state=tk.DISABLED)
        tkChat.see(tk.END)

        print("Server says: " +displaystr)

    sck.close()
    Master.destroy()


def getMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkChat.get("1.0", tk.END).strip()

    # updates this clients chat display in the same way as recieve
    tkChat.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkChat.insert(tk.END, "\n\n" + "You:" + msg, "tag_your_message") # no line
    else:
        tkChat.insert(tk.END, "\n\n" + "You:" + msg, "tag_your_message")

    tkChat.config(state=tk.DISABLED)
    print("starting server send")
    server_send(msg)

    tkChat.see(tk.END)
    #clears old text in message box
    tkMessage.delete('1.0', tk.END)


def server_send(msg):
    print("encoding message")
    msg = msg.encode('utf-8')
    print("sending message")
    client.send(msg)
    if msg == "exit":
        print("goodbye",msg)
        client.close()
        Master.destroy()
    print("Sending message")


Master.mainloop()
