import tkinter as tk
import socket
import threading

class MasterGUI:
    def __init__(self,master):
        self.Master = master
        self.Master.title("Server")
        self.Master.configure(bg='dodgerblue')
        
        self.Host=tk.Label()
        self.Port=tk.Label()
        self.server = None
        self.HOST_ADDR = "192.168.1.242"
        self.HOST_PORT = 13000
        self.user_name = " "
        self.user_namestr = " "
        self.users = []
        self.user_names = []
        #onoffFrame for the buttons to accept and stop accepting users
        onoffFrame = tk.Frame(self.Master,bg= 'dodgerblue')
        self.Enable = tk.Button()
        self.Disable = tk.Button()
        self.Enable = tk.Button(onoffFrame, text="Enable",bg= 'grey', command= lambda : self.On())
        self.Enable.pack(side=tk.LEFT)
        
        self.Disable = tk.Button(onoffFrame, text="Disable",bg= 'grey', command= lambda : self.Off(),state=tk.DISABLED)
        self.Disable.pack(side=tk.RIGHT)
        onoffFrame.pack(side=tk.TOP, pady=(5, 0))

        #Info frame consists of labels for displaying the host and port info
        self.Info = tk.Frame(self.Master,bg= 'dodgerblue')
        self.Host = tk.Label(self.Info,bg= 'dodgerblue', text = "Host IP: X.X.X.X")
        self.Host.pack(side=tk.RIGHT)
        self.Port = tk.Label(self.Info,bg= 'dodgerblue', text = "Port:XXXX")
        self.Port.pack(side=tk.RIGHT)
        self.Info.pack(side=tk.TOP, pady=(5, 0))

        #The client frame shows the clients connected
        self.clientFrame = tk.Frame(self.Master,bg= 'dodgerblue')
        Title = tk.Label(self.clientFrame,bg= 'dodgerblue', text="_____________________CLIENT LIST_____________________").pack()
        scrollBar = tk.Scrollbar(self.clientFrame,bg= 'blue',)
        scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tkDisplay = tk.Text()
        self.tkDisplay = tk.Text(self.clientFrame, height=15, width=25)
        self.tkDisplay.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        #demo names
        self.tkDisplay.insert(tk.END, "User 1\n")
        self.tkDisplay.insert(tk.END, "User 2\n")
        scrollBar.config(command=self.tkDisplay.yview)
        self.tkDisplay.config(yscrollcommand=scrollBar.set, bg="#F4F6F7", highlightbackground="grey", state="disabled")
        self.clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

    def Off(self):
        self.Enable.config(state=tk.NORMAL)
        self.Disable.config(state=tk.DISABLED)
        print('BYE')

    # enable server connections

    def On(self):
        
        self.Enable.config(state=tk.DISABLED)
        self.Disable.config(state=tk.NORMAL)
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("attempt to bind server")
        server.bind((self.HOST_ADDR, self.HOST_PORT))
        print("attempt to listen for clients")
        server.listen(5)  # server is listening for client connection

        print("starting new thread")
        threading._start_new_thread(self.join, (server, " "))

        self.Host["text"] = "Host IP: " + self.HOST_ADDR
        self.Port["text"] = "Port: " + str(self.HOST_PORT)
        print("successfully up")

    #checks for joining clients
    def join(self,the_server, y):
        while True:
            
            print("try to accept clients")
            client, addr = the_server.accept()
            print("appending client list")
            self.users.append(client)

            # use a thread 
            threading._start_new_thread(self.send_receive, (client, addr))



    # Function to send and recieve messages
    def send_receive(self,client_connection, client_ip_addr):
        
        print("start send_recieve")
        client_msg = " "
        print("atempt recv of username")
        # send welcome message to client
        self.user_name = client_connection.recv(256)
        print("decode and print username")
        self.user_namestr  = self.user_name.decode('utf-8')
        print(self.user_namestr)
        send = "Welcome " + self.user_namestr + ". Use exit to quit"
        print(send)
        byte = send.encode('utf-8')
        client_connection.send(byte)

        self.user_names.append(self.user_namestr)
        print("update server display")
        self.update_display()  
        conditional=False
        data = b''
        if data != b'exit':
            print('Enter loop')
            conditional=True
        while conditional:
            data = client_connection.recv(256)
            if not data: 
                print("no data")
                break    
            if data == b'exit':
                print('exiting')
                break
            client_msg = data.decode('utf-8')
            print("get client index")
            idx = self.get_client_index(client_connection)
            sending_client_name = self.user_names[idx]
            temp = sending_client_name + "->" + client_msg
            print(temp)
            sendable = temp.encode('utf-8')
            for c in self.users:
                if c != client_connection:
                    c.send(sendable)

        # find the client index then remove from both lists(client name list and connection list)
        idx = self.get_client_index( client_connection)
        del self.user_names[idx]
        del self.users[idx]
        client_connection.send(b'BYE!')
        client_connection.close()

        self.update_display()  # update client names display


# Return the index of the current client in the list of clients
    def get_client_index(self, curr_client):
        i = 0
        for connections in self.users:
            if connections == curr_client:
                break
            i = i + 1
        print("client index = ",i)
        return i


# Update client name display when a new client connects OR
# When a connected client disconnects
    def update_display(self):
        self.tkDisplay.config(state=tk.NORMAL)
        self.tkDisplay.delete('1.0', tk.END)

        for c in self.user_names:
            print(c)
            self.tkDisplay.insert(tk.END, c+"\n")
        self.tkDisplay.config(state=tk.DISABLED)

root = tk.Tk()
master = MasterGUI(root)
root.mainloop()