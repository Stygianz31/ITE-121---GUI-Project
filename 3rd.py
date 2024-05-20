import tkinter as tk
from tkinter import LabelFrame, Entry, Button, Toplevel, Scale, Text, Listbox, Scrollbar, Frame, colorchooser, messagebox
import subprocess
import sqlite3

class StickyNotesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stickies")
        self.configure(bg="#000000")  # Change background color to black

        # Create or open a database
        self.conn = sqlite3.connect('stickies.db')
        self.c = self.conn.cursor()

        # Create table if it doesn't exist
        self.c.execute('''CREATE TABLE IF NOT EXISTS notes
                          (id INTEGER PRIMARY KEY, title TEXT, content TEXT, font TEXT, font_size INTEGER, color TEXT)''')
        self.conn.commit()

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{int(self.screen_width * 0.3)}x{int(self.screen_height * 0.5)}+{self.screen_width // 2}+10")

        self.nameentry = tk.StringVar(self)
        self.alpha = tk.DoubleVar(value=0.95)
        self.font_family = tk.StringVar(value="Calibri")
        self.font_size = tk.IntVar(value=12)
        self.note_color = "#000000"  # Change default note color to black
        self.text_color = "#ffffff"   # Change default text color to white

        self.attributes('-alpha', self.alpha.get())
        self.setup_ui()
        self.load_saved_notes()

    def setup_ui(self):
        main_frame = LabelFrame(self, text='Stickies', bg="#000000")  # Change background color to black
        name_frame = LabelFrame(main_frame, text='Name your note', bg="#000000")  # Change background color to black
        name_entry = Entry(name_frame, textvariable=self.nameentry, bg="#ffffff")  # Change background color to white
        name_entry.pack(padx=5, pady=5, fill=tk.BOTH)
        name_frame.pack(padx=10, pady=10, fill=tk.BOTH)

        create_button = Button(main_frame, text='Create', command=self.create_sticky)
        create_button.pack(padx=5, pady=5)

        Button(main_frame, text='Settings', command=self.open_settings).pack(padx=5, pady=10, side='bottom')
        Button(main_frame, text='Load Saved Notes', command=self.load_selected_note_content).pack(padx=5, pady=5, side='bottom')
        Button(main_frame, text='Logout', command=self.logout).pack(padx=5, pady=5, side='bottom')

        main_frame.pack(expand=False, fill=tk.BOTH, padx=10, pady=10)

        # Section for displaying saved notes
        saved_notes_frame = Frame(self, bg="#000000")  # Change background color to black
        saved_notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        saved_notes_label = tk.Label(saved_notes_frame, text="Saved Notes", bg="#000000", fg="#ffffff")  # Change background color to black and text color to white
        saved_notes_label.pack()

        self.saved_notes_listbox = Listbox(saved_notes_frame, selectmode=tk.SINGLE, bg="#ffffff", fg="#000000")  # Change background color to white and text color to black
        saved_notes_scrollbar = Scrollbar(saved_notes_frame, orient=tk.VERTICAL, command=self.saved_notes_listbox.yview)
        self.saved_notes_listbox.config(yscrollcommand=saved_notes_scrollbar.set)
        saved_notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.saved_notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Buttons for deleting selected notes
        delete_button_frame = Frame(saved_notes_frame, bg="#000000")  # Change background color to black
        delete_button_frame.pack(pady=5)

        Button(delete_button_frame, text="Delete Selected", command=self.delete_selected_note, bg="#ffffff", fg="#000000").pack(side=tk.LEFT, padx=5)  # Change background color to white and text color to black
        Button(delete_button_frame, text="Delete All", command=self.delete_all_notes, bg="#ffffff", fg="#000000").pack(side=tk.LEFT, padx=5)  # Change background color to white and text color to black

        # Bind function to load note content when a note is selected
        self.saved_notes_listbox.bind('<<ListboxSelect>>', self.load_selected_note_content)

    def load_saved_notes(self):
        self.saved_notes_listbox.delete(0, tk.END)  # Clear existing items
        self.c.execute("SELECT title FROM notes")
        saved_notes = self.c.fetchall()
        for note in saved_notes:
            self.saved_notes_listbox.insert(tk.END, note[0])

    def create_sticky(self):
        title = self.nameentry.get() or 'Untitled'
        new_window = Toplevel(self)
        new_window.wm_title(title)
        new_window.geometry(f"{int(self.screen_width * 0.3)}x{int(self.screen_height * 0.3)}")

        text_frame = Frame(new_window, bg="#000000")  # Change background color to black
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = Text(text_frame, bg=self.note_color, fg=self.text_color, font=(self.font_family.get(), self.font_size.get()))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Save button for the sticky note
        save_button = Button(new_window, text="Save", command=lambda: self.save_note(title, text_widget.get("1.0", "end-1c")), bg="#ffffff", fg="#000000")  # Change background color to white and text color to black
        save_button.pack(pady=5)

    def save_note(self, title, content):
        self.c.execute("INSERT INTO notes (title, content, font, font_size, color) VALUES (?, ?, ?, ?, ?)",
                       (title, content, self.font_family.get(), self.font_size.get(), self.note_color))
        self.conn.commit()
        self.load_saved_notes()

    def open_settings(self):
        settings_window = Toplevel(self)
        settings_window.wm_title('Settings')

        tk.Label(settings_window, text='Font:', bg="#000000", fg="#ffffff").pack()  # Change background color to black and text color to white
        font_family_entry = Entry(settings_window, textvariable=self.font_family, bg="#ffffff", fg="#000000")  # Change background color to white and text color to black
        font_family_entry.pack()

        tk.Label(settings_window, text='Font Size:', bg="#000000", fg="#ffffff").pack()  # Change background color to black and text color to white
        font_size_entry = Entry(settings_window, textvariable=self.font_size, bg="#ffffff", fg="#000000")  # Change background color to white and text color to black
        font_size_entry.pack()

        tk.Label(settings_window, text='Note Color:', bg="#000000", fg="#ffffff").pack()  # Change background color to black and text color to white
        Button(settings_window, text="Choose Background Color", command=self.choose_background_color, bg="#ffffff", fg="#000000").pack()  # Change background color to white and text color to black
        Button(settings_window, text="Choose Text Color", command=self.choose_text_color, bg="#ffffff", fg="#000000").pack()  # Change background color to white and text color to black

        tk.Label(settings_window, text='Transparency:', bg="#000000", fg="#ffffff").pack()  # Change background color to black and text color to white
        Scale(settings_window, from_=0.5, to=1.0, resolution=0.05, orient='horizontal', variable=self.alpha, command=self.update_transparency).pack()

        Button(settings_window, text='Apply', command=settings_window.destroy, bg="#ffffff", fg="#000000").pack()  # Change background color to white and text color to black

    def delete_selected_note(self):
        selected_index = self.saved_notes_listbox.curselection()
        if selected_index:
            confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this note?")
            if confirmation:
                note_title = self.saved_notes_listbox.get(selected_index)
                self.c.execute("DELETE FROM notes WHERE title=?", (note_title,))
                self.conn.commit()
                self.load_saved_notes()

    def delete_all_notes(self):
        confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all notes?")
        if confirmation:
            self.c.execute("DELETE FROM notes")
            self.conn.commit()
            self.load_saved_notes()

    def update_transparency(self, value):
        self.attributes('-alpha', float(value))

    def choose_background_color(self):
        color_code = colorchooser.askcolor(title="Choose background color")
        if color_code:
            self.note_color = color_code[1]

    def choose_text_color(self):
        color_code = colorchooser.askcolor(title="Choose text color")
        if color_code:
            self.text_color = color_code[1]

    def logout(self):
        self.conn.close()  # Close the database connection
        self.quit()
        subprocess.Popen(["python", "1st.py"])

    def load_selected_note_content(self):
        selected_index = self.saved_notes_listbox.curselection()
        if selected_index:
            selected_title = self.saved_notes_listbox.get(selected_index)
            self.c.execute("SELECT content FROM notes WHERE title=?", (selected_title,))
            content = self.c.fetchone()[0]
            self.create_sticky_with_content(selected_title, content)

    def create_sticky_with_content(self, title, content):
        new_window = Toplevel(self)
        new_window.wm_title(title)
        new_window.geometry(f"{int(self.screen_width * 0.3)}x{int(self.screen_height * 0.3)}")

        text_frame = Frame(new_window)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = Text(text_frame, bg=self.note_color, fg=self.text_color, font=(self.font_family.get(), self.font_size.get()))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.insert(tk.END, content)

if __name__ == '__main__':
    app = StickyNotesApp()
    app.mainloop()
