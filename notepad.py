import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Style

class Notepad(tk.Tk):
    def __init__(self):
        super().__init__()
        Style().theme_use("clam")

        self.title("Poznámkový blok")
        self.geometry("900x500")
        
        self.text = tk.Text(self)
        self.text.pack(expand=True, fill='both')

        self.create_menu()
        self.create_scrollbar()
        
        self.night_mode = False
        
    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.configure(bg='black', fg='white')
        filemenu.add_command(label="Nový", command=self.new_file)
        
        filemenu.add_command(label="Otevřít", command=self.open_file)
        
        filemenu.add_command(label="Uložit", command=self.save_file)
        filemenu.add_separator()
        filemenu.add_command(label="Noční režim", command=self.night_mode_toggle)
        filemenu.add_separator()
        filemenu.add_command(label="Ukončit aplikaci", command=self.exit_program)
        menubar.add_cascade(label="Hlavní menu", menu=filemenu)

    def create_scrollbar(self):
        scrollbar = tk.Scrollbar(self.text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

    def new_file(self):
        self.text.delete(1.0, tk.END)

    def open_file(self):
        file = filedialog.askopenfile(defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*"),])
        if file:
            self.text.delete(1.0, tk.END)
            content = file.read()
            self.text.insert(tk.INSERT, content)
            file.close()

    def save_file(self):
        file = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*"),])
        if file:
            content = self.text.get(1.0, tk.END)
            file.write(content)
            file.close()

    def night_mode_toggle(self):
        if self.night_mode:
            self.text.configure(bg='white', fg='black')
            self.night_mode = False
        else:
            self.text.configure(bg='black', fg='white')
            self.night_mode = True


    def exit_program(self):
        self.destroy()

notepad = Notepad()
notepad.mainloop()