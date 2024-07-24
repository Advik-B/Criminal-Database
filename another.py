import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ctypes.windll.user32.SetProcessDPIAware()
# Make it so that the window icon is not python's icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dev.krish.CriminalDatabase")

from tkinter import Tk
from tkinter import ttk

root = Tk()
root.title("Criminal Database")
root.geometry("800x600")
root.resizable(False, False)

style = ttk.Style()
style.configure("TButton", font=("Arial", 12))
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))

widgets = ttk.Notebook(root)
tab1 = ttk.Frame(widgets)
tab2 = ttk.Frame(widgets)
widgets.add(tab1, text="Tab 1")
widgets.add(tab2, text="Tab 2")

btn = ttk.Button(tab1, text="Click Me")
btn.pack(pady=20)

widgets.pack(expand=True, fill="both")


root.mainloop()
