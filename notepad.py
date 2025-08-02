import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog, font as tkfont
import os
import json
import sys
from pathlib import Path
import ctypes

class SettingsDialog:
    def __init__(self, parent, current_config):
        self.parent = parent
        self.config = current_config.copy()
        self.result = None
        
        self.dialog = tb.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.center_dialog()
        self.create_widgets()
        self.dialog.wait_window()
    
    def center_dialog(self):
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 250
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 300
        self.dialog.geometry(f"500x600+{x}+{y}")
    
    def create_widgets(self):
        notebook = tb.Notebook(self.dialog)
        notebook.pack(expand=True, fill=BOTH, padx=10, pady=10)
        
        self.create_appearance_tab(notebook)
        self.create_editor_tab(notebook)
        self.create_files_tab(notebook)
        self.create_buttons()
    
    def create_appearance_tab(self, notebook):
        appearance_frame = tb.Frame(notebook)
        notebook.add(appearance_frame, text="Appearance")
        
        theme_frame = tb.LabelFrame(appearance_frame, text="Application Theme", padding=10)
        theme_frame.pack(fill=X, padx=10, pady=5)
        
        self.theme_var = tb.StringVar(value=self.config['theme'])
        themes = [
            ('Dark', [('darkly', 'Darkly'), ('superhero', 'Superhero'), ('cyborg', 'Cyborg'), ('vapor', 'Vapor'), ('solar', 'Solar')]),
            ('Light', [('litera', 'Litera'), ('cosmo', 'Cosmo'), ('flatly', 'Flatly'), ('journal', 'Journal'), ('lumen', 'Lumen')]),
            ('Colorful', [('morph', 'Morph'), ('pulse', 'Pulse'), ('simplex', 'Simplex'), ('united', 'United'), ('yeti', 'Yeti')])
        ]
        
        row = 0
        for category, theme_list in themes:
            category_label = tb.Label(theme_frame, text=category, font=('', 10, 'bold'))
            category_label.grid(row=row, column=0, columnspan=3, sticky=W, pady=(10, 5))
            row += 1
            
            col = 0
            for theme_key, theme_name in theme_list:
                theme_radio = tb.Radiobutton(
                    theme_frame, 
                    text=theme_name, 
                    variable=self.theme_var, 
                    value=theme_key,
                    command=self.preview_theme
                )
                theme_radio.grid(row=row, column=col, sticky=W, padx=(20, 10), pady=2)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            
            if col > 0:
                row += 1
        
        font_frame = tb.LabelFrame(appearance_frame, text="Editor Font", padding=10)
        font_frame.pack(fill=X, padx=10, pady=5)
        
        font_family_frame = tb.Frame(font_frame)
        font_family_frame.pack(fill=X, pady=5)
        
        tb.Label(font_family_frame, text="Font Family:").pack(side=LEFT)
        self.font_family_var = tb.StringVar(value=self.config['font_family'])
        font_families = ['Consolas', 'Courier New', 'Lucida Console', 'Monaco', 'DejaVu Sans Mono', 'Liberation Mono']
        font_combo = tb.Combobox(font_family_frame, textvariable=self.font_family_var, values=font_families, state='readonly')
        font_combo.pack(side=RIGHT)
        
        font_size_frame = tb.Frame(font_frame)
        font_size_frame.pack(fill=X, pady=5)
        
        tb.Label(font_size_frame, text="Font Size:").pack(side=LEFT)
        self.font_size_var = tb.IntVar(value=self.config['font_size'])
        font_size_spin = tb.Spinbox(font_size_frame, from_=8, to=72, textvariable=self.font_size_var, width=10)
        font_size_spin.pack(side=RIGHT)
        
        preview_frame = tb.LabelFrame(font_frame, text="Preview", padding=10)
        preview_frame.pack(fill=BOTH, expand=True, pady=5)
        
        self.font_preview = tb.Text(preview_frame, height=3, wrap=WORD)
        self.font_preview.pack(fill=BOTH, expand=True)
        self.font_preview.insert(1.0, "Sample text for font preview\nThe quick brown fox jumps over the lazy dog\n1234567890 !@#$%^&*()")
        
        font_combo.bind('<<ComboboxSelected>>', self.update_font_preview)
        font_size_spin.bind('<KeyRelease>', self.update_font_preview)
        self.update_font_preview()
    
    def create_editor_tab(self, notebook):
        editor_frame = tb.Frame(notebook)
        notebook.add(editor_frame, text="Editor")
        
        wrap_frame = tb.LabelFrame(editor_frame, text="Text Display", padding=10)
        wrap_frame.pack(fill=X, padx=10, pady=5)
        
        self.word_wrap_var = tb.BooleanVar(value=self.config['word_wrap'])
        wrap_check = tb.Checkbutton(wrap_frame, text="Word wrap", variable=self.word_wrap_var)
        wrap_check.pack(anchor=W)
        
        self.show_line_numbers_var = tb.BooleanVar(value=self.config.get('show_line_numbers', False))
        line_numbers_check = tb.Checkbutton(wrap_frame, text="Show line numbers", variable=self.show_line_numbers_var)
        line_numbers_check.pack(anchor=W)
        
        self.highlight_current_line_var = tb.BooleanVar(value=self.config.get('highlight_current_line', True))
        highlight_line_check = tb.Checkbutton(wrap_frame, text="Highlight current line", variable=self.highlight_current_line_var)
        highlight_line_check.pack(anchor=W)
        
        indent_frame = tb.LabelFrame(editor_frame, text="Indentation", padding=10)
        indent_frame.pack(fill=X, padx=10, pady=5)
        
        self.auto_indent_var = tb.BooleanVar(value=self.config.get('auto_indent', True))
        auto_indent_check = tb.Checkbutton(indent_frame, text="Auto indent", variable=self.auto_indent_var)
        auto_indent_check.pack(anchor=W)
        
        tab_size_frame = tb.Frame(indent_frame)
        tab_size_frame.pack(fill=X, pady=5)
        
        tb.Label(tab_size_frame, text="Tab size:").pack(side=LEFT)
        self.tab_size_var = tb.IntVar(value=self.config.get('tab_size', 4))
        tab_size_spin = tb.Spinbox(tab_size_frame, from_=2, to=8, textvariable=self.tab_size_var, width=10)
        tab_size_spin.pack(side=RIGHT)
        
        backup_frame = tb.LabelFrame(editor_frame, text="Auto Save", padding=10)
        backup_frame.pack(fill=X, padx=10, pady=5)
        
        self.auto_save_var = tb.BooleanVar(value=self.config.get('auto_save', False))
        auto_save_check = tb.Checkbutton(backup_frame, text="Enable auto save", variable=self.auto_save_var)
        auto_save_check.pack(anchor=W)
        
        save_interval_frame = tb.Frame(backup_frame)
        save_interval_frame.pack(fill=X, pady=5)
        
        tb.Label(save_interval_frame, text="Save interval (minutes):").pack(side=LEFT)
        self.save_interval_var = tb.IntVar(value=self.config.get('save_interval', 5))
        save_interval_spin = tb.Spinbox(save_interval_frame, from_=1, to=60, textvariable=self.save_interval_var, width=10)
        save_interval_spin.pack(side=RIGHT)
    
    def create_files_tab(self, notebook):
        files_frame = tb.Frame(notebook)
        notebook.add(files_frame, text="Files")
        
        encoding_frame = tb.LabelFrame(files_frame, text="File Encoding", padding=10)
        encoding_frame.pack(fill=X, padx=10, pady=5)
        
        self.default_encoding_var = tb.StringVar(value=self.config.get('default_encoding', 'utf-8'))
        encodings = ['utf-8', 'windows-1250', 'iso-8859-2', 'ascii']
        
        for encoding in encodings:
            encoding_radio = tb.Radiobutton(encoding_frame, text=encoding.upper(), variable=self.default_encoding_var, value=encoding)
            encoding_radio.pack(anchor=W)
        
        extension_frame = tb.LabelFrame(files_frame, text="Default Extension", padding=10)
        extension_frame.pack(fill=X, padx=10, pady=5)
        
        ext_frame = tb.Frame(extension_frame)
        ext_frame.pack(fill=X)
        
        tb.Label(ext_frame, text="Extension:").pack(side=LEFT)
        self.default_extension_var = tb.StringVar(value=self.config.get('default_extension', '.txt'))
        ext_entry = tb.Entry(ext_frame, textvariable=self.default_extension_var, width=10)
        ext_entry.pack(side=RIGHT)
        
        recent_frame = tb.LabelFrame(files_frame, text="Recent Files", padding=10)
        recent_frame.pack(fill=X, padx=10, pady=5)
        
        max_recent_frame = tb.Frame(recent_frame)
        max_recent_frame.pack(fill=X)
        
        tb.Label(max_recent_frame, text="Maximum recent files:").pack(side=LEFT)
        self.max_recent_var = tb.IntVar(value=self.config.get('max_recent_files', 10))
        max_recent_spin = tb.Spinbox(max_recent_frame, from_=5, to=20, textvariable=self.max_recent_var, width=10)
        max_recent_spin.pack(side=RIGHT)
        
        clear_recent_btn = tb.Button(recent_frame, text="Clear recent files", command=self.clear_recent_files)
        clear_recent_btn.pack(pady=5)
    
    def create_buttons(self):
        button_frame = tb.Frame(self.dialog)
        button_frame.pack(side=BOTTOM, fill=X, padx=10, pady=10)
        
        tb.Button(button_frame, text="Cancel", command=self.cancel).pack(side=RIGHT, padx=(5, 0))
        tb.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=RIGHT)
        tb.Button(button_frame, text="OK", command=self.ok).pack(side=RIGHT, padx=(0, 5))
        tb.Button(button_frame, text="Defaults", command=self.reset_defaults).pack(side=LEFT)
    
    def preview_theme(self):
        try:
            new_theme = self.theme_var.get()
            self.parent.style.theme_use(new_theme)
        except Exception:
            pass
    
    def update_font_preview(self, event=None):
        try:
            family = self.font_family_var.get()
            size = self.font_size_var.get()
            self.font_preview.configure(font=(family, size))
        except Exception:
            pass
    
    def clear_recent_files(self):
        if messagebox.askyesno("Confirm", "Do you really want to clear all recent files?"):
            self.config['recent_files'] = []
            messagebox.showinfo("Done", "Recent files list has been cleared.")
    
    def collect_settings(self):
        self.config.update({
            'theme': self.theme_var.get(),
            'font_family': self.font_family_var.get(),
            'font_size': self.font_size_var.get(),
            'word_wrap': self.word_wrap_var.get(),
            'show_line_numbers': self.show_line_numbers_var.get(),
            'highlight_current_line': self.highlight_current_line_var.get(),
            'auto_indent': self.auto_indent_var.get(),
            'tab_size': self.tab_size_var.get(),
            'auto_save': self.auto_save_var.get(),
            'save_interval': self.save_interval_var.get(),
            'default_encoding': self.default_encoding_var.get(),
            'default_extension': self.default_extension_var.get(),
            'max_recent_files': self.max_recent_var.get()
        })
    
    def apply_settings(self):
        self.collect_settings()
        self.result = self.config
        self.parent.apply_settings(self.config)
    
    def ok(self):
        self.apply_settings()
        self.dialog.destroy()
    
    def cancel(self):
        try:
            original_theme = self.parent.config['theme']
            self.parent.style.theme_use(original_theme)
        except Exception:
            pass
        self.result = None
        self.dialog.destroy()
    
    def reset_defaults(self):
        if messagebox.askyesno("Confirm", "Do you really want to reset all settings to default values?"):
            default_config = {
                'theme': 'darkly',
                'font_family': 'Consolas',
                'font_size': 12,
                'word_wrap': True,
                'show_line_numbers': False,
                'highlight_current_line': True,
                'auto_indent': True,
                'tab_size': 4,
                'auto_save': False,
                'save_interval': 5,
                'default_encoding': 'utf-8',
                'default_extension': '.txt',
                'max_recent_files': 10
            }
            
            self.theme_var.set(default_config['theme'])
            self.font_family_var.set(default_config['font_family'])
            self.font_size_var.set(default_config['font_size'])
            self.word_wrap_var.set(default_config['word_wrap'])
            self.show_line_numbers_var.set(default_config['show_line_numbers'])
            self.highlight_current_line_var.set(default_config['highlight_current_line'])
            self.auto_indent_var.set(default_config['auto_indent'])
            self.tab_size_var.set(default_config['tab_size'])
            self.auto_save_var.set(default_config['auto_save'])
            self.save_interval_var.set(default_config['save_interval'])
            self.default_encoding_var.set(default_config['default_encoding'])
            self.default_extension_var.set(default_config['default_extension'])
            self.max_recent_var.set(default_config['max_recent_files'])
            
            self.update_font_preview()
            self.preview_theme()

class Notepad(tb.Window):
    def __init__(self):
        self.setup_windows_dark_mode()
        
        super().__init__(themename="darkly")
        
        self.title("Notepad")
        self.geometry("1200x700")
        self.minsize(800, 500)
        self.current_file = None
        self.file_modified = False
        self.config_file = Path.home() / '.notepad_config.json'
        self.auto_save_job = None
        
        self.load_config()
        
        try:
            self.style.theme_use(self.config['theme'])
        except Exception:
            self.style.theme_use('darkly')
        
        self.create_widgets()
        self.create_menu()
        self.create_statusbar()
        self.create_toolbar()
        self.bind_events()
        self.update_title()
        self.update_statusbar()
        
        if self.config.get('auto_save', False):
            self.start_auto_save()
        
        self.after(100, self.center_window)

    def setup_windows_dark_mode(self):
        if sys.platform == "win32":
            try:
                # Nastavení ikonky
                try:
                    self.iconbitmap("notepad.ico")
                except:
                    pass  # Launch without icon
                
                # Počkej na vytvoření okna
                self.update()
                
                # Tmavý title bar pro Windows 10/11
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                if hwnd == 0:
                    hwnd = self.winfo_id()
                
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 
                    DWMWA_USE_IMMERSIVE_DARK_MODE, 
                    ctypes.byref(value), 
                    ctypes.sizeof(value)
                )
                    
            except Exception as e:
                pass

    def load_config(self):
        default_config = {
            'theme': 'darkly',
            'font_family': 'Consolas',
            'font_size': 12,
            'window_size': '1200x700',
            'word_wrap': True,
            'show_line_numbers': False,
            'highlight_current_line': True,
            'auto_indent': True,
            'tab_size': 4,
            'auto_save': False,
            'save_interval': 5,
            'default_encoding': 'utf-8',
            'default_extension': '.txt',
            'max_recent_files': 10,
            'recent_files': [],
            'toolbar_visible': True,
            'statusbar_visible': True
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config = default_config.copy()
                    self.config.update(loaded_config)
            else:
                self.config = default_config
        except Exception:
            self.config = default_config

    def save_config(self):
        try:
            self.config['window_size'] = self.geometry()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_toolbar(self):
        if not self.config.get('toolbar_visible', True):
            return
            
        self.toolbar = tb.Frame(self, height=40)
        self.toolbar.pack(side=TOP, fill=X, padx=5, pady=(5, 0))
        self.toolbar.pack_propagate(False)
        
        buttons = [
            ("📄", "New file", self.new_file),
            ("📁", "Open", self.open_file),
            ("💾", "Save", self.save_file),
            ("✂️", "Cut", self.cut),
            ("📋", "Copy", self.copy),
            ("📌", "Paste", self.paste),
            ("🔍", "Find", self.find_text),
            ("⚙️", "Settings", self.show_settings),
        ]
        
        for emoji, tooltip, command in buttons:
            btn = tb.Button(self.toolbar, text=emoji, command=command, width=3)
            btn.pack(side=LEFT, padx=2)

    def create_widgets(self):
        main_frame = tb.Frame(self)
        main_frame.pack(expand=True, fill=BOTH, padx=10, pady=10)
        
        text_frame = tb.Frame(main_frame)
        text_frame.pack(expand=True, fill=BOTH)
        
        self.text = tb.Text(
            text_frame,
            wrap="word" if self.config['word_wrap'] else "none",
            font=(self.config['font_family'], self.config['font_size']),
            undo=True,
            maxundo=50,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=10,
            tabs=self.config.get('tab_size', 4) * 8
        )
        
        v_scrollbar = tb.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        h_scrollbar = tb.Scrollbar(text_frame, orient="horizontal", command=self.text.xview)
        
        self.text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.text.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        if self.config.get('highlight_current_line', True):
            self.text.tag_configure("current_line", background="#2d3748")

    def create_menu(self):
        menubar = tb.Menu(self)
        
        filemenu = tb.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        filemenu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        
        self.recent_menu = tb.Menu(filemenu, tearoff=0)
        self.update_recent_menu()
        filemenu.add_cascade(label="Recent files", menu=self.recent_menu)
        
        filemenu.add_separator()
        filemenu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        filemenu.add_command(label="Save as", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        filemenu.add_separator()
        filemenu.add_command(label="Settings", command=self.show_settings, accelerator="Ctrl+,")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_program, accelerator="Ctrl+Q")
        
        editmenu = tb.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        editmenu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        editmenu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        editmenu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        editmenu.add_separator()
        editmenu.add_command(label="Select all", command=self.select_all, accelerator="Ctrl+A")
        editmenu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        editmenu.add_command(label="Find & Replace", command=self.find_replace, accelerator="Ctrl+H")
        
        viewmenu = tb.Menu(menubar, tearoff=0)
        viewmenu.add_checkbutton(label="Toolbar", command=self.toggle_toolbar)
        viewmenu.add_checkbutton(label="Status bar", command=self.toggle_statusbar)
        viewmenu.add_separator()
        viewmenu.add_command(label="Increase font", command=self.increase_font, accelerator="Ctrl++")
        viewmenu.add_command(label="Decrease font", command=self.decrease_font, accelerator="Ctrl+-")
        viewmenu.add_command(label="Reset font size", command=self.reset_font_size, accelerator="Ctrl+0")
        
        toolsmenu = tb.Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Word count", command=self.word_count)
        toolsmenu.add_command(label="To uppercase", command=self.to_uppercase)
        toolsmenu.add_command(label="To lowercase", command=self.to_lowercase)
        toolsmenu.add_command(label="To title case", command=self.to_title_case)
        
        helpmenu = tb.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Keyboard shortcuts", command=self.show_shortcuts)
        helpmenu.add_command(label="About", command=self.show_about)
        
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="View", menu=viewmenu)
        menubar.add_cascade(label="Tools", menu=toolsmenu)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.configure(menu=menubar)

    def create_statusbar(self):
        if not self.config.get('statusbar_visible', True):
            return
            
        self.statusbar = tb.Frame(self, height=25)
        self.statusbar.pack(side=BOTTOM, fill=X)
        
        self.cursor_info = tb.Label(self.statusbar, text="Line: 1, Column: 1")
        self.cursor_info.pack(side=LEFT, padx=(10, 0))
        
        self.file_info = tb.Label(self.statusbar, text="UTF-8")
        self.file_info.pack(side=RIGHT, padx=(0, 10))
        
        self.auto_save_indicator = tb.Label(self.statusbar, text="")
        self.auto_save_indicator.pack(side=RIGHT, padx=10)

    def bind_events(self):
        self.text.bind("<<Modified>>", self.on_modified)
        self.text.bind("<KeyRelease>", self.update_statusbar)
        self.text.bind("<Button-1>", self.update_statusbar)
        self.text.bind("<Key>", self.on_key_press)
        
        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-Shift-Key-S>", lambda e: self.save_file_as())
        self.bind_all("<Control-q>", lambda e: self.exit_program())
        self.bind_all("<Control-comma>", lambda e: self.show_settings())
        
        self.bind_all("<Control-z>", lambda e: self.undo())
        self.bind_all("<Control-y>", lambda e: self.redo())
        self.bind_all("<Control-x>", lambda e: self.cut())
        self.bind_all("<Control-c>", lambda e: self.copy())
        self.bind_all("<Control-v>", lambda e: self.paste())
        self.bind_all("<Control-a>", lambda e: self.select_all())
        self.bind_all("<Control-f>", lambda e: self.find_text())
        self.bind_all("<Control-h>", lambda e: self.find_replace())
        
        self.bind_all("<Control-plus>", lambda e: self.increase_font())
        self.bind_all("<Control-equal>", lambda e: self.increase_font())
        self.bind_all("<Control-minus>", lambda e: self.decrease_font())
        self.bind_all("<Control-0>", lambda e: self.reset_font_size())
        
        self.protocol("WM_DELETE_WINDOW", self.exit_program)
        
        if self.config.get('highlight_current_line', True):
            self.text.bind("<KeyRelease>", self.highlight_current_line)
            self.text.bind("<Button-1>", self.highlight_current_line)

    def on_key_press(self, event):
        if self.config.get('auto_indent', True) and event.keysym == 'Return':
            self.after_idle(self.auto_indent)

    def auto_indent(self):
        try:
            current_line = self.text.index("insert").split('.')[0]
            previous_line = str(int(current_line) - 1)
            
            if int(previous_line) > 0:
                previous_text = self.text.get(f"{previous_line}.0", f"{previous_line}.end")
                indent = ""
                for char in previous_text:
                    if char in ' \t':
                        indent += char
                    else:
                        break
                
                if indent:
                    self.text.insert("insert", indent)
        except Exception:
            pass

    def highlight_current_line(self, event=None):
        if not self.config.get('highlight_current_line', True):
            return
            
        try:
            self.text.tag_remove("current_line", "1.0", "end")
            current_line = self.text.index("insert").split('.')[0]
            self.text.tag_add("current_line", f"{current_line}.0", f"{current_line}.end+1c")
        except Exception:
            pass

    def on_modified(self, event=None):
        if self.text.edit_modified():
            self.file_modified = True
            self.text.edit_modified(False)
            self.update_title()

    def update_title(self):
        name = os.path.basename(self.current_file) if self.current_file else "Untitled"
        star = "*" if self.file_modified else ""
        self.title(f"{star}{name} - Notepad")

    def update_statusbar(self, event=None):
        if not hasattr(self, 'statusbar'):
            return
            
        try:
            cursor_pos = self.text.index("insert")
            line, column = cursor_pos.split('.')
            self.cursor_info.configure(text=f"Line: {line}, Column: {int(column)+1}")
            
            char_count = len(self.text.get(1.0, "end-1c"))
            line_count = int(self.text.index("end-1c").split('.')[0])
            encoding = self.config.get('default_encoding', 'UTF-8').upper()
            self.file_info.configure(text=f"Characters: {char_count}, Lines: {line_count} | {encoding}")
        except Exception:
            pass

    def update_recent_menu(self):
        self.recent_menu.delete(0, 'end')
        
        recent_files = self.config.get('recent_files', [])
        if recent_files:
            for file_path in recent_files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    self.recent_menu.add_command(
                        label=filename, 
                        command=lambda f=file_path: self.open_recent_file(f)
                    )
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="Clear list", command=self.clear_recent_files)
        else:
            self.recent_menu.add_command(label="(No recent files)", state='disabled')

    def add_to_recent_files(self, file_path):
        recent_files = self.config.get('recent_files', [])
        
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        recent_files.insert(0, file_path)
        
        max_recent = self.config.get('max_recent_files', 10)
        recent_files = recent_files[:max_recent]
        
        self.config['recent_files'] = recent_files
        self.update_recent_menu()

    def open_recent_file(self, file_path):
        if self.confirm_save_changes():
            try:
                with open(file_path, "r", encoding=self.config.get('default_encoding', 'utf-8')) as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, "r", encoding="windows-1250") as f:
                        content = f.read()
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot load file:\n{str(e)}")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Cannot load file:\n{str(e)}")
                return
            
            self.text.delete(1.0, "end")
            self.text.insert("end", content)
            self.current_file = file_path
            self.file_modified = False
            self.update_title()
            self.update_statusbar()

    def clear_recent_files(self):
        self.config['recent_files'] = []
        self.update_recent_menu()

    def start_auto_save(self):
        if self.auto_save_job:
            self.after_cancel(self.auto_save_job)
        
        interval = self.config.get('save_interval', 5) * 60000
        self.auto_save_job = self.after(interval, self.auto_save)
        
        if hasattr(self, 'auto_save_indicator'):
            self.auto_save_indicator.configure(text="🔄 Auto-save")

    def stop_auto_save(self):
        if self.auto_save_job:
            self.after_cancel(self.auto_save_job)
            self.auto_save_job = None
        
        if hasattr(self, 'auto_save_indicator'):
            self.auto_save_indicator.configure(text="")

    def auto_save(self):
        if self.current_file and self.file_modified:
            try:
                with open(self.current_file, "w", encoding=self.config.get('default_encoding', 'utf-8')) as f:
                    content = self.text.get(1.0, "end-1c")
                    f.write(content)
                self.file_modified = False
                self.update_title()
                
                if hasattr(self, 'auto_save_indicator'):
                    self.auto_save_indicator.configure(text="✓ Saved")
                    self.after(2000, lambda: self.auto_save_indicator.configure(text="🔄 Auto-save"))
            except Exception:
                pass
        
        if self.config.get('auto_save', False):
            self.start_auto_save()

    def new_file(self):
        if self.confirm_save_changes():
            self.text.delete(1.0, "end")
            self.current_file = None
            self.file_modified = False
            self.update_title()
            self.update_statusbar()

    def open_file(self):
        if self.confirm_save_changes():
            filetypes = [
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("HTML files", "*.html;*.htm"),
                ("CSS files", "*.css"),
                ("JavaScript files", "*.js"),
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ]
            
            path = filedialog.askopenfilename(filetypes=filetypes)
            if path:
                try:
                    encoding = self.config.get('default_encoding', 'utf-8')
                    with open(path, "r", encoding=encoding) as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(path, "r", encoding="windows-1250") as f:
                            content = f.read()
                    except Exception as e:
                        messagebox.showerror("Error", f"Cannot load file:\n{str(e)}")
                        return
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot load file:\n{str(e)}")
                    return
                
                self.text.delete(1.0, "end")
                self.text.insert("end", content)
                self.current_file = path
                self.file_modified = False
                self.add_to_recent_files(path)
                self.update_title()
                self.update_statusbar()

    def save_file(self):
        if self.current_file:
            try:
                encoding = self.config.get('default_encoding', 'utf-8')
                with open(self.current_file, "w", encoding=encoding) as f:
                    content = self.text.get(1.0, "end-1c")
                    f.write(content)
                self.file_modified = False
                self.update_title()
                self.show_save_notification(os.path.basename(self.current_file))
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file:\n{str(e)}")
        else:
            self.save_file_as()

    def show_save_notification(self, filename):
        if hasattr(self, 'cursor_info'):
            try:
                original_text = self.cursor_info.cget("text")
                self.cursor_info.configure(text=f"✓ Saved: {filename}")
                self.after(2000, lambda: self.cursor_info.configure(text=original_text))
            except:
                pass

    def save_file_as(self):
        default_ext = self.config.get('default_extension', '.txt')
        filetypes = [
            ("Text files", "*.txt"),
            ("Python files", "*.py"),
            ("HTML files", "*.html"),
            ("CSS files", "*.css"),
            ("JavaScript files", "*.js"),
            ("JSON files", "*.json"),
            ("XML files", "*.xml"),
            ("Markdown files", "*.md"),
            ("All files", "*.*")
        ]
        
        path = filedialog.asksaveasfilename(
            defaultextension=default_ext, 
            filetypes=filetypes
        )
        if path:
            self.current_file = path
            self.add_to_recent_files(path)
            self.save_file()

    def confirm_save_changes(self):
        if self.file_modified:
            filename = os.path.basename(self.current_file) if self.current_file else "Untitled"
            result = messagebox.askyesnocancel(
                "Save changes?", 
                f"Document '{filename}' contains unsaved changes.\nDo you want to save them?"
            )
            if result:
                self.save_file()
                return not self.file_modified
            elif result is None:
                return False
        return True

    def undo(self):
        try:
            self.text.edit_undo()
        except Exception:
            pass

    def redo(self):
        try:
            self.text.edit_redo()
        except Exception:
            pass

    def cut(self):
        try:
            self.text.event_generate("<<Cut>>")
        except Exception:
            pass

    def copy(self):
        try:
            self.text.event_generate("<<Copy>>")
        except Exception:
            pass

    def paste(self):
        try:
            self.text.event_generate("<<Paste>>")
        except Exception:
            pass

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end")

    def find_text(self):
        search_text = simpledialog.askstring("Find", "Enter text to search:")
        if search_text:
            self.text.tag_remove("sel", "1.0", "end")
            
            start_pos = self.text.search(search_text, "insert", "end")
            if not start_pos:
                start_pos = self.text.search(search_text, "1.0", "end")
            
            if start_pos:
                end_pos = f"{start_pos}+{len(search_text)}c"
                self.text.tag_add("sel", start_pos, end_pos)
                self.text.mark_set("insert", start_pos)
                self.text.see(start_pos)
                self.text.focus_set()
            else:
                messagebox.showinfo("Find", "Text not found.")

    def find_replace(self):
        replace_dialog = tb.Toplevel(self)
        replace_dialog.title("Find and Replace")
        replace_dialog.geometry("400x200")
        replace_dialog.resizable(False, False)
        replace_dialog.transient(self)
        replace_dialog.grab_set()
        
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 100
        replace_dialog.geometry(f"400x200+{x}+{y}")
        
        find_frame = tb.Frame(replace_dialog)
        find_frame.pack(fill=X, padx=10, pady=5)
        tb.Label(find_frame, text="Find:").pack(side=LEFT)
        find_entry = tb.Entry(find_frame)
        find_entry.pack(side=RIGHT, fill=X, expand=True)
        
        replace_frame = tb.Frame(replace_dialog)
        replace_frame.pack(fill=X, padx=10, pady=5)
        tb.Label(replace_frame, text="Replace:").pack(side=LEFT)
        replace_entry = tb.Entry(replace_frame)
        replace_entry.pack(side=RIGHT, fill=X, expand=True)
        
        button_frame = tb.Frame(replace_dialog)
        button_frame.pack(fill=X, padx=10, pady=10)
        
        def find_next():
            search_text = find_entry.get()
            if search_text:
                start_pos = self.text.search(search_text, "insert+1c", "end")
                if not start_pos:
                    start_pos = self.text.search(search_text, "1.0", "end")
                
                if start_pos:
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    self.text.tag_remove("sel", "1.0", "end")
                    self.text.tag_add("sel", start_pos, end_pos)
                    self.text.mark_set("insert", end_pos)
                    self.text.see(start_pos)
                else:
                    messagebox.showinfo("Find", "Text not found.")
        
        def replace_current():
            try:
                if self.text.tag_ranges("sel"):
                    self.text.delete("sel.first", "sel.last")
                    self.text.insert("insert", replace_entry.get())
            except Exception:
                pass
        
        def replace_all():
            search_text = find_entry.get()
            replace_text = replace_entry.get()
            if search_text:
                content = self.text.get(1.0, "end-1c")
                new_content = content.replace(search_text, replace_text)
                self.text.delete(1.0, "end")
                self.text.insert(1.0, new_content)
                messagebox.showinfo("Replace All", f"Replaced {content.count(search_text)} occurrences.")
        
        tb.Button(button_frame, text="Find Next", command=find_next).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Replace", command=replace_current).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Replace All", command=replace_all).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Close", command=replace_dialog.destroy).pack(side=RIGHT, padx=5)
        
        find_entry.focus_set()

    def toggle_toolbar(self):
        self.config['toolbar_visible'] = not self.config.get('toolbar_visible', True)
        if hasattr(self, 'toolbar'):
            if self.config['toolbar_visible']:
                self.toolbar.pack(side=TOP, fill=X, padx=5, pady=(5, 0))
            else:
                self.toolbar.pack_forget()

    def toggle_statusbar(self):
        self.config['statusbar_visible'] = not self.config.get('statusbar_visible', True)
        if hasattr(self, 'statusbar'):
            if self.config['statusbar_visible']:
                self.statusbar.pack(side=BOTTOM, fill=X)
            else:
                self.statusbar.pack_forget()

    def increase_font(self):
        current_font = self.text.cget("font")
        
        if isinstance(current_font, tuple):
            family = current_font[0]
            size = current_font[1]
        else:
            font_parts = str(current_font).split()
            family = font_parts[0] if font_parts else self.config['font_family']
            try:
                size = int(font_parts[1]) if len(font_parts) > 1 else self.config['font_size']
            except ValueError:
                size = self.config['font_size']
        
        new_size = size + 1
        if new_size <= 72:
            self.text.configure(font=(family, new_size))
            self.config['font_size'] = new_size

    def decrease_font(self):
        current_font = self.text.cget("font")
        
        if isinstance(current_font, tuple):
            family = current_font[0]
            size = current_font[1]
        else:
            font_parts = str(current_font).split()
            family = font_parts[0] if font_parts else self.config['font_family']
            try:
                size = int(font_parts[1]) if len(font_parts) > 1 else self.config['font_size']
            except ValueError:
                size = self.config['font_size']
        
        new_size = size - 1
        if new_size >= 8:
            self.text.configure(font=(family, new_size))
            self.config['font_size'] = new_size

    def reset_font_size(self):
        family = self.config['font_family']
        default_size = 12
        self.text.configure(font=(family, default_size))
        self.config['font_size'] = default_size

    def word_count(self):
        content = self.text.get(1.0, "end-1c")
        
        char_count = len(content)
        char_count_no_spaces = len(content.replace(' ', '').replace('\t', '').replace('\n', ''))
        word_count = len(content.split())
        line_count = content.count('\n') + 1 if content else 0
        
        stats = f"""Document Statistics:

Characters (with spaces): {char_count:,}
Characters (without spaces): {char_count_no_spaces:,}
Words: {word_count:,}
Lines: {line_count:,}"""
        
        messagebox.showinfo("Word Count", stats)

    def to_uppercase(self):
        try:
            if self.text.tag_ranges("sel"):
                selected_text = self.text.get("sel.first", "sel.last")
                self.text.delete("sel.first", "sel.last")
                self.text.insert("insert", selected_text.upper())
        except Exception:
            pass

    def to_lowercase(self):
        try:
            if self.text.tag_ranges("sel"):
                selected_text = self.text.get("sel.first", "sel.last")
                self.text.delete("sel.first", "sel.last")
                self.text.insert("insert", selected_text.lower())
        except Exception:
            pass

    def to_title_case(self):
        try:
            if self.text.tag_ranges("sel"):
                selected_text = self.text.get("sel.first", "sel.last")
                self.text.delete("sel.first", "sel.last")
                self.text.insert("insert", selected_text.title())
        except Exception:
            pass

    def show_settings(self):
        settings_dialog = SettingsDialog(self, self.config)
        if settings_dialog.result:
            self.config.update(settings_dialog.result)
            self.apply_settings(self.config)

    def apply_settings(self, config):
        self.text.configure(
            font=(config['font_family'], config['font_size']),
            wrap="word" if config['word_wrap'] else "none",
            tabs=config.get('tab_size', 4) * 8
        )
        
        if config.get('highlight_current_line', True):
            self.highlight_current_line()
        else:
            self.text.tag_remove("current_line", "1.0", "end")
        
        if config.get('auto_save', False):
            self.start_auto_save()
        else:
            self.stop_auto_save()
        
        self.save_config()
        self.update_statusbar()

    def show_shortcuts(self):
        shortcuts_text = """Keyboard Shortcuts:

FILES:
• Ctrl+N - New file
• Ctrl+O - Open file
• Ctrl+S - Save
• Ctrl+Shift+S - Save as
• Ctrl+Q - Exit application

EDITING:
• Ctrl+Z - Undo
• Ctrl+Y - Redo
• Ctrl+X - Cut
• Ctrl+C - Copy
• Ctrl+V - Paste
• Ctrl+A - Select all

SEARCHING:
• Ctrl+F - Find text
• Ctrl+H - Find and replace

VIEW:
• Ctrl++ - Increase font
• Ctrl+- - Decrease font
• Ctrl+0 - Reset font size

SETTINGS:
• Ctrl+, - Open settings"""

        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)

    def show_about(self):
        about_text = """Notepad v1.1

Text editor created in Python by MichalBr."""

        messagebox.showinfo("About", about_text)

    def exit_program(self):
        if self.confirm_save_changes():
            self.save_config()
            self.destroy()

if __name__ == "__main__":
    try:
        app = Notepad()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()