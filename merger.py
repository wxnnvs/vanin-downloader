import argparse
import os
import random
import shutil
import tempfile
from pathlib import Path

from PIL import Image

# Explicitly register Pillow's JPEG plugin.
# This prevents:
#     KeyError: 'JPEG'
# when Pillow creates PDFs from RGB images.
try:
    from PIL import JpegImagePlugin  # noqa: F401
except ImportError:
    pass

import ocrmypdf


def get_default_download_dir():
    """Return the user's Downloads directory."""
    if os.name == "nt":
        return Path(os.environ["USERPROFILE"]) / "Downloads"

    return Path.home() / "Downloads"


def find_png_files(directory):
    """
    Find files named:

        vanin-1.png
        vanin-2.png
        vanin-3.png
        ...

    and sort them numerically.
    """
    directory = Path(directory)
    png_files = []

    for path in directory.iterdir():
        if not path.is_file():
            continue

        if path.suffix.lower() != ".png":
            continue

        name = path.stem

        if not name.startswith("vanin-"):
            continue

        number_part = name[6:]

        try:
            number = int(number_part)
        except ValueError:
            continue

        png_files.append((number, path))

    png_files.sort(key=lambda item: item[0])

    return png_files


def backup_existing_output(output_pdf):
    """
    If the output PDF already exists, rename it to:

        filename-12345.pdf

    using a random five-digit number.
    """
    output_pdf = Path(output_pdf)

    if not output_pdf.exists():
        return

    stem = output_pdf.stem
    suffix = output_pdf.suffix

    while True:
        random_number = random.randint(10000, 99999)

        backup = output_pdf.with_name(
            f"{stem}-{random_number}{suffix}"
        )

        if not backup.exists():
            break

    output_pdf.rename(backup)

    print(f"Existing output moved to: {backup}")


def create_pdf_from_pngs(png_files, output_pdf):
    """
    Convert PNG files into one PDF.
    """
    images = []

    try:
        for number, path in png_files:
            print(f"Adding page {number}: {path.name}")

            try:
                with Image.open(path) as img:
                    # Convert everything to RGB because PDF output
                    # does not handle all PNG modes consistently.
                    image = img.convert("RGB").copy()

                images.append(image)

            except Exception as exc:
                raise RuntimeError(
                    f"Could not read PNG file: {path}"
                ) from exc

        if not images:
            raise RuntimeError("No PNG files found.")

        first = images[0]
        rest = images[1:]

        print(f"Creating PDF with {len(images)} pages...")

        first.save(
            str(output_pdf),
            "PDF",
            save_all=True,
            append_images=rest,
            resolution=100.0,
        )

    finally:
        for image in images:
            image.close()


def check_tesseract():
    """
    Check whether Tesseract is installed and available on PATH.
    """
    if shutil.which("tesseract") is None:
        raise RuntimeError(
            "\n"
            "Tesseract is not installed or is not available on PATH.\n"
            "\n"
            "On Ubuntu/Debian, install it with:\n"
            "\n"
            "    sudo apt update\n"
            "    sudo apt install tesseract-ocr tesseract-ocr-nld\n"
            "\n"
            "Then verify with:\n"
            "\n"
            "    tesseract --version\n"
            "    tesseract --list-langs\n"
        )


def check_dutch_tesseract_language():
    """
    Check whether the Dutch ('nld') Tesseract language data is installed.
    """
    tesseract = shutil.which("tesseract")

    if tesseract is None:
        check_tesseract()

    result = shutil.run(
        [tesseract, "--list-langs"],
        capture_output=True,
        text=True,
        check=False,
    )

    languages = result.stdout.splitlines()

    if "nld" not in languages:
        raise RuntimeError(
            "\n"
            "Tesseract is installed, but the Dutch language data ('nld') "
            "is missing.\n"
            "\n"
            "On Ubuntu/Debian, install it with:\n"
            "\n"
            "    sudo apt install tesseract-ocr-nld\n"
            "\n"
        )


def ocr_the_pdf(input_pdf, output_pdf="output.pdf"):
    """
    Run Dutch OCR on an existing PDF.
    """
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    if not input_pdf.exists():
        raise FileNotFoundError(
            f"Input PDF does not exist: {input_pdf}"
        )

    check_tesseract()

    print(f"Running OCR on: {input_pdf}")

    try:
        ocrmypdf.ocr(
            str(input_pdf),
            str(output_pdf),
            deskew=True,
            optimize=0,
            clean=False,
            clean_final=False,
            force_ocr=True,
            language=["nld"],
        )

    except Exception as exc:
        raise RuntimeError(
            f"OCR failed for '{input_pdf}'."
        ) from exc

    print(f"Searchable PDF saved as: {output_pdf}")


def merge_pngs_to_pdf(
    directory=None,
    output="output.pdf",
    ocr=False,
):
    """
    Merge Vanin PNG pages into a PDF.

    Optionally run Dutch OCR afterwards.
    """
    if directory is None:
        directory = get_default_download_dir()

    directory = Path(directory)
    output = Path(output)

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {directory}"
        )

    if not directory.is_dir():
        raise NotADirectoryError(
            f"Not a directory: {directory}"
        )

    png_files = find_png_files(directory)

    if not png_files:
        raise RuntimeError(
            f"No files matching 'vanin-<number>.png' "
            f"found in:\n{directory}"
        )

    print(f"Found {len(png_files)} PNG files in:")
    print(f"  {directory}")

    print(
        f"Page range: "
        f"{png_files[0][0]} -> {png_files[-1][0]}"
    )

    # Convert output to an absolute path.
    output = output.resolve()

    # Make sure the output directory exists.
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Back up an existing output before doing anything.
    backup_existing_output(output)

    # Create temporary PDF in the same directory as the output.
    with tempfile.NamedTemporaryFile(
        prefix="merger-",
        suffix=".pdf",
        dir=output.parent,
        delete=False,
    ) as temp_file:
        temp_pdf = Path(temp_file.name)

    ocr_temp = None

    try:
        # ---------------------------------------------------------
        # Step 1: PNG -> PDF
        # ---------------------------------------------------------

        create_pdf_from_pngs(
            png_files,
            temp_pdf,
        )

        print(f"Temporary PDF created: {temp_pdf}")

        # ---------------------------------------------------------
        # Step 2: Optional OCR
        # ---------------------------------------------------------

        if ocr:
            print("OCR requested.")

            check_tesseract()

            ocr_temp = temp_pdf.with_name(
                temp_pdf.stem + "-ocr.pdf"
            )

            ocr_the_pdf(
                temp_pdf,
                ocr_temp,
            )

            # Move OCR'd PDF to final destination.
            ocr_temp.replace(output)

            ocr_temp = None

        else:
            # No OCR required, simply move temporary PDF
            # to the final destination.
            temp_pdf.replace(output)

        print()
        print("========================================")
        print("Successfully created:")
        print(f"  {output}")
        print("========================================")
        print()

    finally:
        # Remove temporary PDF if it still exists.
        if temp_pdf.exists():
            try:
                temp_pdf.unlink()
            except OSError:
                pass

        # Remove OCR temporary file if it still exists.
        if ocr_temp is not None and ocr_temp.exists():
            try:
                ocr_temp.unlink()
            except OSError:
                pass

    # -------------------------------------------------------------
    # Step 3: Delete PNGs ONLY after successful PDF creation
    # -------------------------------------------------------------

    print("Deleting original PNG files...")

    deleted = 0

    for _, png_path in png_files:
        try:
            png_path.unlink()
            deleted += 1
        except OSError as exc:
            print(
                f"Warning: could not delete {png_path}: {exc}"
            )

    print(f"Deleted {deleted} PNG files.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Merge Vanin PNG pages into a single PDF "
            "and optionally perform Dutch OCR."
        )
    )

    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help=(
            "Directory containing the PNG files. "
            "Defaults to ~/Downloads."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output.pdf"),
        help=(
            "Output PDF filename. "
            "Default: output.pdf"
        ),
    )

    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Perform Dutch OCR on the resulting PDF.",
    )

    parser.add_argument(
        "--ocr-only",
        action="store_true",
        help=(
            "Run OCR on an existing PDF instead of "
            "merging PNGs."
        ),
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help=(
            "Input PDF for --ocr-only. "
            "If omitted, --output is used."
        ),
    )

    args = parser.parse_args()

    # -------------------------------------------------------------
    # --ocr-only
    # -------------------------------------------------------------

    if args.ocr_only:
        input_pdf = args.input or args.output

        if not input_pdf.exists():
            raise FileNotFoundError(
                f"Input PDF does not exist: {input_pdf}"
            )

        # Do not overwrite the input PDF accidentally.
        if input_pdf.resolve() == args.output.resolve():
            raise RuntimeError(
                "\n"
                "For --ocr-only, input and output must be "
                "different files.\n"
                "\n"
                "For example:\n"
                "\n"
                '    python3 merger.py --ocr-only \\\n'
                '        --input "input.pdf" \\\n'
                '        --output "searchable.pdf"\n'
            )

        # Back up existing output if necessary.
        backup_existing_output(args.output)

        ocr_the_pdf(
            input_pdf,
            args.output,
        )

        return

    # -------------------------------------------------------------
    # Normal PNG -> PDF operation
    # -------------------------------------------------------------

    merge_pngs_to_pdf(
        directory=args.dir,
        output=args.output,
        ocr=args.ocr,
    )


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        raise SystemExit(1)

    except Exception as exc:
        print()
        print("ERROR:")
        print(exc)
        print()
        raise SystemExit(1)
