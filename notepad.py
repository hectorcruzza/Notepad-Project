from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import pyperclip as p
import os

class Notebook:
    def __init__(self):
        self.root = Tk()
        self.root.option_add("*tearOff", False)
        self.root.title("Sin título")
        self.root.geometry("1000x475+260+150")
        self.root.minsize(350, 150)
        self.root.rowconfigure(0, weight = 1)
        self.root.columnconfigure(0, weight = 1)
        self.menubar = Menu(self.root, font = ("Verdana", 9))
        self.root.config(menu = self.menubar)

        self.file = Menu(self.menubar, font = ("Verdana", 9))
        self.edit = Menu(self.menubar, font = ("Verdana", 9))
        self.view = Menu(self.menubar, font = ("Verdana", 9))

        self.menubar.add_cascade(menu = self.file, label = "Archivo")
        self.menubar.add_cascade(menu = self.edit, label = "Editar")
        self.menubar.add_cascade(menu = self.view, label = "Ver")

        self.file.add_command(label = "Abrir", accelerator = "Ctrl+P", command = self.open_file)
        self.file.add_command(label = "Guardar", accelerator = "Ctrl+G", command = self.save_file)
        self.file.add_command(label = "Guardar como", accelerator = "Ctrl+Shift+S", command = self.save_as_file)
        self.file.add_separator()
        self.file.add_command(label = "Salir", command = self.on_closing)

        self.edit.add_command(label = "Deshacer", accelerator = "Ctrl+Z", command = self.undo_text)
        self.edit.add_command(label = "Rehacer", accelerator = "Ctrl+Y", command = self.redo_text)
        self.edit.add_command(label = "Cortar", accelerator = "Ctrl+X", state = "disabled", command = self.cut_text)
        self.edit.add_command(label = "Copiar", accelerator = "Ctrl+C", state = "disabled", command = self.copy_text)
        self.edit.add_command(label = "Pegar", accelerator = "Ctrl+V", command = self.paste_text)
        self.edit.add_command(label = "Eliminar", accelerator = "Supr", state = "disabled", command = self.delete_text)
        self.edit.add_command(label = "Seleccionar todo", accelerator = "Ctrl+E", command = self.select_all)

        self.check_clipboard()

        self.zoom = Menu(self.view, font = ("Verdana", 9))
        self.view.add_cascade(menu = self.zoom, label = "Zoom")
        self.zoom.add_command(label = "Acercar", accelerator = "Ctrl+signo más", command = self.zoom_in)
        self.zoom.add_command(label = "Alejar", accelerator = "Ctrl+signo menos", command = self.zoom_out)
        self.zoom.add_command(label = "Restaurar zoom predeterminado", accelerator = "Ctrl+0", command = self.default_zoom)

        self.body = ttk.Frame(self.root)
        self.body.rowconfigure(0, weight = 1)
        self.body.columnconfigure(0, weight = 1)

        self.footer = ttk.Frame(self.root)
        self.footer.columnconfigure([0, 1, 2, 3], weight = 1)

        self.font_size = 10

        self.text = Text(self.body, wrap = "word", font = ("Verdana", self.font_size), undo = True, autoseparators = True, maxundo = -1)
        self.text.grid(row = 0, column = 0, sticky = "nsew")
        self.text.focus_set()

        self.scrollbar = ttk.Scrollbar(self.body, orient = VERTICAL, command = self.text.yview)
        self.scrollbar.grid(row = 0, column = 1, sticky = "ns")
        self.text.config(yscrollcommand = self.scrollbar.set)

        self.body.grid(row = 0, column = 0, sticky = "nsew")

        self.line_number_str = StringVar()
        self.line_number_str.set(f"Línea {self.text.index("insert").split(".")[0]}")

        self.chars_number_str = StringVar()
        self.chars_number_str.set(f"{len(self.text.get("1.0", "end - 1 chars"))} caracteres")

        self.zoom_percent_int = 100
        self.zoom_percent_str = StringVar()
        self.zoom_percent_str.set(f"{self.zoom_percent_int}%")

        self.file_coding_str = StringVar()
        self.file_coding_str.set("UTF-8")

        self.style = ttk.Style()
        self.style.configure("TLabel", font = ("Verdana", 9))

        self.lbl_line_number = ttk.Label(self.footer, textvariable = self.line_number_str)
        self.lbl_line_number.grid(row = 0, column = 0, sticky = "w", padx = 25)

        self.lbl_chars_number = ttk.Label(self.footer, textvariable = self.chars_number_str)
        self.lbl_chars_number.grid(row = 0, column = 1, sticky = "w", padx = 25)

        self.lbl_zoom_percent = ttk.Label(self.footer, textvariable = self.zoom_percent_str)
        self.lbl_zoom_percent.grid(row = 0, column = 2, sticky = "w", padx = 25)

        self.lbl_file_coding = ttk.Label(self.footer, textvariable = self.file_coding_str)
        self.lbl_file_coding.grid(row = 0, column = 3, sticky = "w", padx = 25)

        self.footer.grid(row = 1, column = 0, sticky = "ew")

        self.filename = None
        self.utf_8_file = True
        self.content = self.text.get("1.0", "end - 1 chars")

        self.text.event_add("<<Check_Keys_Clicks>>", "<Key>", "<KeyRelease>", "<ButtonPress>", "<B1-Motion>", "<ButtonRelease-1>")
        self.text.bind("<<Check_Keys_Clicks>>", self.check_keys_clicks)
        self.menubar.bind("<<MenuSelect>>", self.check_keys_clicks)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def check_clipboard(self):
        if not p.paste():
            self.edit.entryconfig("Pegar", state = "disabled")
        else:
            self.edit.entryconfig("Pegar", state = "active")

    def check_line_number_chars_number(self):
        self.line_number_str.set(f"Línea {self.text.index("insert").split(".")[0]}")
        self.chars_number_str.set(f"{len(self.text.get("1.0", "end - 1 chars"))} caracteres")

    def ckeck_file_coding(self):
        if self.utf_8_file:
            self.file_coding_str.set("UTF-8")
        else:
            self.file_coding_str.set("ANSI")

    def check_modified_file(self):
        if self.text.get("1.0", "end - 1 chars") != self.content:
            if self.filename != None:   
                self.root.title(f"{os.path.basename(self.filename)}*")
            else:
                self.root.title("Sin título*")
        else:
            if self.filename != None:   
                self.root.title(f"{os.path.basename(self.filename)}")
            else:
                self.root.title("Sin título")

    def check_selection(self):
        if not self.text.tag_ranges("sel"):
            self.edit.entryconfig("Eliminar", state = "disabled")
            self.edit.entryconfig("Cortar", state = "disabled")
            self.edit.entryconfig("Copiar", state = "disabled")
        else:
            self.edit.entryconfig("Eliminar", state = "active")
            self.edit.entryconfig("Cortar", state = "active")
            self.edit.entryconfig("Copiar", state = "active")

    def state_zoom(self):
        if self.zoom_percent_int == 500:
            self.zoom.entryconfig("Acercar", state = "disabled")
        else:
            self.zoom.entryconfig("Acercar", state = "active")
        if self.zoom_percent_int == 10:
            self.zoom.entryconfig("Alejar", state = "disabled")
        else:
            self.zoom.entryconfig("Alejar", state = "active")

    def check_keys_clicks(self, event):
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()
        self.check_modified_file()
        self.state_zoom()

        if event.type == EventType.Key:
            if event.state == 4 and event.keysym == "p":
                self.open_file()
            elif event.state == 4 and event.keysym == "g":
                self.save_file()
            elif event.state == 5 and event.keysym == "S":
                self.save_as_file()
            elif event.state == 4 and event.keysym == "e":
                self.select_all()
            elif event.state == 4 and event.keysym == "plus":
                self.zoom_in()
            elif event.state == 4 and event.keysym == "minus":
                self.zoom_out()
            elif event.state == 4 and event.keysym == "0":
                self.default_zoom()
        
        if event.num == 3:
            self.popup_menu(event)

    def copy_text(self):
        self.text.event_generate("<<Copy>>")
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()
        self.check_modified_file()
    
    def paste_text(self):
        self.text.event_generate("<<Paste>>")
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()
        self.check_modified_file()

    def cut_text(self):
        self.text.event_generate("<<Cut>>")
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()
        self.check_modified_file()

    def undo_text(self):
        self.text.event_generate("<<Undo>>")
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()
        self.check_modified_file()

    def redo_text(self):
        self.text.event_generate("<<Redo>>")
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()
        self.check_modified_file()

    def delete_text(self):
        self.text.event_generate("<Delete>")
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()
        self.check_modified_file()

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end - 1 chars")
        self.check_clipboard()
        self.check_selection()

    def zoom_in(self):
        if self.zoom_percent_int != 500:
            self.zoom_percent_int += 10
            self.font_size += 1 
            self.text.config(font = ("Verdana", self.font_size))
            self.zoom_percent_str.set(f"{self.zoom_percent_int}%")
        self.state_zoom()

    def zoom_out(self):
        if self.zoom_percent_int != 10:
            self.zoom_percent_int -= 10
            self.font_size -= 1 
            self.text.config(font = ("Verdana", self.font_size))
            self.zoom_percent_str.set(f"{self.zoom_percent_int}%")
        self.state_zoom()

    def default_zoom(self):
        self.zoom_percent_int = 100
        self.font_size = 10
        self.text.config(font = ("Verdana", self.font_size))
        self.zoom_percent_str.set(f"{self.zoom_percent_int}%")
        self.state_zoom()

    def popup_menu(self, coords):
        self.edit.tk_popup(coords.x_root, coords.y_root)
        self.edit.grab_release()

    def open_utf_8_file(self):
        with open(self.dialogstate_, "r", encoding = "utf-8") as file_content:
            self.content_n = file_content.read()
        if self.text.get("1.0", "end - 1 chars") != self.content:
            if self.filename == None:
                self.result = messagebox.askyesno(title = "Cambios sin guardar", message = f"Antes de continuar, ¿desea guardar el archivo?")
            else:
                self.result = messagebox.askyesno(title = "Cambios sin guardar", message = f"Antes de continuar, ¿desea guardar los cambios hechos a {self.filename}?")
            if self.result:
                self.save_file()
        self.utf_8_file = True
        self.content = self.content_n
        self.filename = self.dialogstate_
        self.text.edit_separator()
        self.text.config(autoseparators = False)
        self.root.title(os.path.basename(self.filename))
        self.text.delete("1.0", "end")
        self.text.insert("1.0", self.content)
        self.text.config(autoseparators = True)
        self.text.edit_separator()
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()

    def open_ansi_file(self):
        with open(self.dialogstate_, "r") as file_content:
            self.content_n = file_content.read()
        if self.text.get("1.0", "end - 1 chars") != self.content:
            if self.filename == None:
                self.result = messagebox.askyesno(title = "Cambios sin guardar", message = f"Antes de continuar, ¿desea guardar el archivo?")
            else:
                self.result = messagebox.askyesno(title = "Cambios sin guardar", message = f"Antes de continuar, ¿Desea guardar los cambios hechos a {self.filename}?")
            if self.result:
                self.save_file()
        self.utf_8_file = False
        self.content = self.content_n
        self.filename = self.dialogstate_
        self.text.edit_separator()
        self.text.config(autoseparators = False)
        self.root.title(os.path.basename(self.filename))
        self.text.delete("1.0", "end")
        self.text.insert("1.0", self.content)
        self.text.config(autoseparators = True)
        self.text.edit_separator()
        self.check_clipboard()
        self.check_line_number_chars_number()
        self.check_selection()

    def save_utf_8_file(self):
        with open(self.filename, "w", encoding = "utf-8") as file_content:
            self.content = self.text.get("1.0", "end - 1 chars")
            file_content.write(self.content)

    def save_ansi_file(self):
        with open(self.filename, "w") as file_content:
            self.content = self.text.get("1.0", "end - 1 chars")
            file_content.write(self.content)

    def open_file(self):
        self.dialogstate_ = filedialog.askopenfilename(filetypes = [("Documento de Texto", ".txt"), ("Archivo INI", ".ini"), ("Python", ".py"), ("Archivo JSON", ".json"), ("Archivo CSV", ".csv"), ("Todos los archivos", "*.*")])
        if self.dialogstate_:
            try:
                self.open_utf_8_file()
                self.ckeck_file_coding()
            except:
                try:
                    self.open_ansi_file()
                    self.ckeck_file_coding()
                except:
                    messagebox.showerror(title = "Error de archivo", message = "La extensión o el formato de codificación del archivo seleccionado no es compatible.")

    def save_file(self):
        if self.filename != None:
            if self.utf_8_file:
                self.save_utf_8_file()
            else:
                self.save_ansi_file()
            self.root.title(os.path.basename(self.filename))
        else:
            self.save_as_file()

    def save_as_file(self):
        if self.filename != None:
            self.dialogstate = filedialog.asksaveasfilename(initialfile = os.path.basename(self.filename), filetypes = [("Documento de Texto", ".txt"), ("Archivo INI", ".ini"), ("Python", ".py"), ("Archivo JSON", ".json"), ("Archivo CSV", ".csv"), ("Todos los archivos", "*.*")], defaultextension = ".txt")
        else:
            self.dialogstate = filedialog.asksaveasfilename(initialfile = "Sin título", filetypes = [("Documento de Texto", ".txt"), ("Archivo INI", ".ini"), ("Python", ".py"), ("Archivo JSON", ".json"), ("Archivo CSV", ".csv"), ("Todos los archivos", "*.*")], defaultextension = ".txt")
        if self.dialogstate:
            self.filename = self.dialogstate
            if self.utf_8_file:
                self.save_utf_8_file()
            else:
                self.save_ansi_file()
            self.root.title(os.path.basename(self.filename))

    def on_closing(self):
        if self.text.get("1.0", "end - 1 chars") != self.content:
            if self.filename == None:
                self.result = messagebox.askyesnocancel(title = "Cambios sin guardar", message = f"¿Desea guardar el archivo?")
            else:
                self.result = messagebox.askyesnocancel(title = "Cambios sin guardar", message = f"¿Desea guardar los cambios hechos a {self.filename}?")
            if self.result != None:
                if self.result:
                    if self.filename == None:
                        self.save_as_file()
                        if self.dialogstate:
                            self.root.destroy()
                    else:
                        self.save_file()
                        self.root.destroy()
                else:
                    self.root.destroy()
        else:
            self.root.destroy()
        
def main():
    Notebook()

if __name__ == "__main__":
    main()