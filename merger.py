import os
from PIL import Image

def merge_pngs_to_pdf(directory=".", output="output.pdf"):
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

if __name__ == "__main__":
    merge_pngs_to_pdf()
