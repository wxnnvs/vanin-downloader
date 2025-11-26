import os
from PIL import Image
import sys
import ctypes
from pathlib import Path
from ctypes.wintypes import HWND, HANDLE, PWSTR, DWORD
import uuid
def get_default_download_dir():
    if os.name == "nt":  # Windows
        try:
            # Use SHGetKnownFolderPath for Downloads
            FOLDERID_Downloads = '{374DE290-123F-4565-9164-39C4925E467B}'
            SHGetKnownFolderPath = ctypes.windll.shell32.SHGetKnownFolderPath
            SHGetKnownFolderPath.argtypes = [ctypes.c_void_p, DWORD, HANDLE, ctypes.POINTER(PWSTR)]
            SHGetKnownFolderPath.restype = ctypes.HRESULT
            folderid = uuid.UUID(FOLDERID_Downloads)
            pPath = PWSTR()
            if SHGetKnownFolderPath(folderid.bytes_le, 0, 0, ctypes.byref(pPath)) == 0:
                return pPath.value
        except Exception:
            # Fallback to USERPROFILE\Downloads
            return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:  # macOS/Linux
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")

def merge_pngs_to_pdf(directory=None, output="output.pdf"):
    if directory is None or directory == ".":
        directory = get_default_download_dir()
    elif len(sys.argv) > 1:
        directory = sys.argv[1]
    # Collect all files ending with .png that start with a number
    png_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(".png"):
            name = filename[:-4]  # remove .png
            if name.isdigit():
                png_files.append((int(name), filename))

    if not png_files:
        raise Exception("No numbered PNG files found.")

    # Sort by numeric value
    png_files.sort(key=lambda x: x[0])

    images = []
    for num, fname in png_files:
        img = Image.open(os.path.join(directory, fname)).convert("RGB")
        images.append(img)

    # Save first image + append the rest to PDF
    first, rest = images[0], images[1:]
    first.save(output, save_all=True, append_images=rest)
    print(f"Saved PDF as {output}")
    # delete all the png files
    for _, fname in png_files:
        os.remove(os.path.join(directory, fname))
    print("Deleted original PNG files.")

if __name__ == "__main__":
    merge_pngs_to_pdf()
