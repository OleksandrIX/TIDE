import eel

from tkinter import filedialog
from ttkthemes import ThemedTk


@eel.expose
def get_file(allowed_extensions: list[str]):
    """
    Using TKinter select files path
    If allowed_extensions is present, file explorer will filter files by file type
    """
    root = ThemedTk(theme="breeze")
    root.withdraw()
    root.wm_attributes("-topmost", 1)

    options = {}

    if allowed_extensions:
        allowed_extensions = (
            (allowed_extension, allowed_extension)
            for allowed_extension in allowed_extensions
        )
        options["filetypes"] = allowed_extensions

    file = filedialog.askopenfile(**options)

    if not file:
        return None

    root.destroy()
    return file.name


@eel.expose
def get_dir():
    root = ThemedTk(theme="breeze")
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    dir = filedialog.askdirectory()
    return dir
