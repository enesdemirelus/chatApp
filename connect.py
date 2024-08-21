import tkinter as tk
from tkinter import ttk, END, filedialog
from ttkbootstrap import Style
from tkinter.messagebox import showerror, showinfo
import socket
import threading
from playsound import playsound
import subprocess
from datetime import datetime
import random
import re
from imgurpython import ImgurClient

class ConnectScreen(tk.Tk):
    def __init__(self):
        super().__init__()

        # variables
        self.entry_variable = tk.StringVar()

        # style
        style = Style(theme='morph')
        style.master = self

        # window attributes
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = 400
        height = 150
        self.resizable(False, False)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2 - 200
        self.geometry(f"{width}x{height}+{x}+{y}")

        #title
        self.title("ChatApp")
        self.username = ""

        self.bind('<Return>', lambda event: self.connect())

        self.rowconfigure(0, weight= 2)
        self.rowconfigure(1, weight= 1)
        self.rowconfigure(2, weight= 1)
        self.columnconfigure(0, weight= 1)

        self.creating_widgets()
        self.packing_widgets()

        self.mainloop()

    def creating_widgets(self):
        self.top_label = ttk.Label(self, text= "Welcome!, enter your username below:", font="inconsolata 18")
        self.middle_entry = tk.Entry(self, textvariable= self.entry_variable)
        self.below_button = ttk.Button(self, text= "Login to chat!", command= self.connect)

    def packing_widgets(self):
        self.top_label.grid(row=0, column=0)
        self.middle_entry.grid(row=1, column=0, sticky="nsew", padx=10)
        self.below_button.grid(row=2, column=0)

    def connect(self):
        self.username = self.entry_variable.get()
        if self.username != "" and self.username != " ":
            client_socket.send(f'{self.username}'.encode('utf-8'))
            self.withdraw()
            chat(self.username, self)
            self.deiconify()
        else:
            showerror(message="Please enter an username!")


class chat(tk.Toplevel):
    def __init__(self, username, parent):
        super().__init__()

        self.username = username
        self.message_str = tk.StringVar(value= "enter your message here")
        self.is_minimized = False
        style = Style(theme='morph')
        style.master = self

        self.title_str = tk.StringVar(value = f"Connected as {self.username}")

        self.current_time = datetime.now().strftime("%I:%M%p")

        self.parent = parent

        self.width = 700
        self.height = 500

        self.geometry(f"{self.width}x{self.height}")

        self.title("Chat App!")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=70)
        self.columnconfigure(2, weight=10)
        self.columnconfigure(3, weight=10)


        self.creating_widgets()
        self.packing_widgets()
        self.history_getter()

        self.entry_bind = self.entry.bind("<Button-1>", lambda event: self.entry.delete(0, END))
        self.bind('<Return>', lambda event: self.send())
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.bind('<Unmap>', lambda event: self.set_minimize(True))
        self.bind('<Map>', lambda event: self.set_minimize(False))

        self.mainloop()

    def creating_widgets(self):
        self.title = ttk.Label(self, textvariable= self.title_str, anchor="center", font=("Futura Medium", 20))
        self.send_image_button = ttk.Button(self, text= 'Send Image', command= self.send_image)
        self.message_display = tk.Text(self)
        self.message_display.config(state=tk.DISABLED)
        self.entry = tk.Entry(self, textvariable = self.message_str)
        self.button = ttk.Button(self, text="->", command= self.send)
        self.back_button = ttk.Button(self, text="<-", command= self.back)
        self.clear_chat_button = ttk.Button(self, text= 'clear chat', command= self.clear_chat)
        self.nudge_button = ttk.Button(self, text= "Nudge", command= self.nudge)

    def packing_widgets(self):
        self.back_button.grid(row = 0, column = 0, sticky="ew", padx=(10,10))
        self.clear_chat_button.grid(row = 0, column= 3, sticky= 'ew', padx=(0,10))
        self.title.grid(row=0, column=1, columnspan = 2, sticky="nsew")
        self.message_display.grid(row=1, column=0, columnspan=4, padx=10, sticky="nsew")
        self.send_image_button.grid(row = 2, column= 0, sticky= 'we', padx=(10,0))
        self.entry.grid(row=2, column=1, sticky="ew", padx=(5, 5)) 
        self.button.grid(row=2, column=2, sticky="ew", padx=(5, 5))
        self.nudge_button.grid(row = 2, column= 3, sticky= 'we', padx=(5, 10))

    def send(self):
        message = self.message_str.get()

        if message == "enter your message here":
            message = ""
            
        if message != "" and message != " ":
            self.message_display.config(state=tk.NORMAL) 
            self.message_display.insert(tk.END, f"{self.username}: {message}" + " " + f'({self.current_time})' + '\n') 
            self.message_display.config(state=tk.DISABLED)
            self.message_display.yview(tk.END)
            client_socket.send(f'{message}'.encode('utf-8'))
            self.history_writer(f"{self.username}: {message}" + " " + f'({self.current_time})')
            self.entry.delete(0, END)
        else:
            showerror(message= "Please don't send an empty message")

    def receive_messages(self):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    match = re.search('nudge', message.lower()) 
                    second_match = re.search('cxhyr4567', message.lower())
                    
                    if second_match:
                        self.after(2)
                        person_count = message[11:]

                        if "Connected" in self.title_str.get():
                            self.title_str.set(f"{person_count} people are online!")
                        else:
                            self.title_str.set(f"Connected as {self.username}")
                    else:
                        if match: 
                            if self.is_minimized == True:
                                subprocess.run([
                                "osascript", "-e",
                                f'display notification "You have been nudged!" with title " "'
                            ])
                            
                            else:
                                for _ in range(10):
                                    x_offset = random.randint(-5, 5)
                                    y_offset = random.randint(-5, 5)
                                    self.geometry(f"+{self.winfo_x() + x_offset}+{self.winfo_y() + y_offset}")
                                    self.update()
                                    self.after(20)

                            playsound('nudge.mp3')
                            self.display_message("You have been nudged!")

                        else:
                            if self.is_minimized == True:
                                subprocess.run([
                                "osascript", "-e",
                                f'display notification "{message}" with title "A new message!"'
                            ])

                            playsound('message_sound.mp3')
                            self.display_message(message)

            except ConnectionAbortedError:
                break
            except Exception as e:
                print("Error receiving message:", e)
                break

    def display_message(self, message):
        self.message_display.config(state=tk.NORMAL)
        self.message_display.insert(tk.END, message + " " + f'({self.current_time})' + '\n')
        self.message_display.config(state=tk.DISABLED)
        self.message_display.yview(tk.END)
        if message != 'You have been nudged!':
            self.history_writer(message + " " + f'({self.current_time})')

    def history_getter(self):
        chat_history_open = open('chats.txt', 'r')
        chat_history= chat_history_open.read()
        if chat_history:
            self.message_display.config(state=tk.NORMAL) 
            self.message_display.insert(tk.END, chat_history + '\n')
            self.message_display.config(state=tk.DISABLED)
            self.message_display.yview(tk.END)
        else:
            pass

        chat_history_open.close()

    def history_writer(self, message):
        with open('chats.txt', 'a+') as chat_history:
            chat_history.seek(0)
            data = chat_history.read()
            if data:
                chat_history.write('\n')
            chat_history.write(message)


    def back(self):
        self.destroy()
        self.parent.deiconify()

    def nudge(self):
        client_socket.send('nudge'.encode('utf-8'))

    def set_minimize(self, value):
        self.is_minimized = value

    def clear_chat(self):
        self.message_display.config(state=tk.NORMAL) 
        self.message_display.delete('1.0', END)
        open("chats.txt", "w").close()
        self.message_display.insert(tk.END, f"chat and history cleared at {self.current_time} from only you!" + '\n')
        self.message_display.config(state=tk.DISABLED)

    def send_image(self):
        file_path = filedialog.askopenfilename()

        if file_path:
            print(f"Selected file: {file_path}")
            try:
                link = self.upload_image(file_path)
                print(f"Image uploaded successfully: {link}")
            except Exception as e:
                print(f"Failed to upload image: {str(e)}")
        else:
            print("No file selected")


    def upload_image(self, file_path):
        CLIENT_ID = ''
        CLIENT_SECRET = ''

        client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
        response = client.upload_from_path(file_path, anon=True)
        link = response['link']
        self.message_display.config(state=tk.NORMAL) 
        self.message_display.insert(tk.END, f"{self.username}: {link}" + " " + f'({self.current_time})' + '\n') 
        self.message_display.config(state=tk.DISABLED)
        self.message_display.yview(tk.END)
        client_socket.send(f'{link}'.encode('utf-8'))
        self.history_writer(f"{self.username}: {link}" + " " + f'({self.current_time})')
        

if "__main__" == __name__:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('', 12345))
        app = ConnectScreen()
    except:
        showerror(message= "Server is not connected!")