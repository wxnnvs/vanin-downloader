import os
import sys
from PIL import Image
import random
import argparse

def get_default_download_dir():
    if os.name == "nt":  # Windows
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:  # macOS/Linux
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")

def merge_pngs_to_pdf(directory=None, output="output.pdf"):
    if directory is None:
        directory = get_default_download_dir()
    elif len(sys.argv) > 1:
        directory = sys.argv[1]
    # Collect all files ending with .png that start with a number
    png_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(".png"):
            name = filename[:-4]  # remove .png
            if name.startswith('vanin-'):
                png_files.append((int(name[6:]), filename))

    if not png_files:
        raise Exception("No numbered PNG files found.")

    # Sort by numeric value
    png_files.sort(key=lambda x: x[0])

    images = []
    for num, fname in png_files:
        img = Image.open(os.path.join(directory, fname)).convert("RGB")
        images.append(img)

    # If output already exists, move it to output-<random 5 digits>.pdf
    if os.path.exists(output):
        rand_digits = random.randint(10000, 99999)
        backup_name = f"output-{rand_digits}.pdf"
        os.rename(output, backup_name)
        print(f"Existing output moved to {backup_name}")

    # Save first image + append the rest to PDF
    first, rest = images[0], images[1:]
    first.save(output, save_all=True, append_images=rest)
    print(f"Saved PDF as {output}")
    # delete all the png files
    for _, fname in png_files:
        os.remove(os.path.join(directory, fname))
    print("Deleted original PNG files.")

parser = argparse.ArgumentParser(description="Merge PNGs to a single PDF.")
parser.add_argument('--dir', type=str, default=None, help='Directory containing PNG files')
parser.add_argument('--output', type=str, default="output.pdf", help='Output PDF file name')
args = parser.parse_args()

directory = args.dir
output = args.output

if __name__ == "__main__":
    merge_pngs_to_pdf(directory=directory if 'directory' in locals() else None,
                      output=output if 'output' in locals() else "output.pdf")
