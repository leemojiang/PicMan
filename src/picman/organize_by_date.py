import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import piexif
from tqdm import tqdm  # 进度条库

from typer import Option

def get_exif_date(file_path: Path) -> Optional[str]:
    """
    Extract EXIF date from image file.
    Returns datetime string in format "YYYY:MM:DD HH:MM:SS" or None.
    """
    try:
        exif_dict = piexif.load(str(file_path))
        
        # Try to get DateTimeOriginal (拍摄时间)
        if "Exif" in exif_dict:
            exif_data = exif_dict["Exif"]
            if piexif.ExifIFD.DateTimeOriginal in exif_data:
                dt_bytes = exif_data[piexif.ExifIFD.DateTimeOriginal]
                return dt_bytes.decode('ascii')
        
        # Fallback to DateTime (modification time in EXIF)
        if "0th" in exif_dict:
            exif_data = exif_dict["0th"]
            if piexif.ImageIFD.DateTime in exif_data:
                dt_bytes = exif_data[piexif.ImageIFD.DateTime]
                return dt_bytes.decode('ascii')
        
        return None
    except Exception as e:
        # Log error and return None instead of crashing
        tqdm.write(f"Warning: Failed to read EXIF from {file_path.name}: {e}")
        return None


def organize_photos_by_date(source_dir: str = Option("./"), target_dir: str= Option("../"), debug: bool = False):
    source = Path(source_dir).resolve()
    target = Path(target_dir).resolve()
    print(f"Source: {source}")
    print(f"Target: {target}")

    if not source.exists():
        raise FileNotFoundError(f"Source directory {source} does not exist.")

    files = [f for f in source.iterdir() if f.is_file()]
    if not files:
        print("No files found in source directory.")
        return
    print(f"Found {len(files)} files in source directory.")

    date_mapping = {}
    for f in tqdm(files, desc="Reading file dates", unit="file"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)  # 修改时间
        ctime = datetime.fromtimestamp(f.stat().st_ctime)  # 创建时间
        earliest = min(mtime, ctime)
        date_mapping.setdefault(f.stem, []).append(earliest)

        exif_date_str = get_exif_date(f)
        if exif_date_str:
            exif_time = datetime.strptime(exif_date_str, "%Y:%m:%d %H:%M:%S")
            date_mapping[f.stem].append(exif_time)

    key = input(
        f"Copy {len(files)} files? \nfrom {source.resolve()} \nto {target.resolve()} \n[Y/N]?"
    )
    if key.lower() == "y":
        print("Process")
    else:
        print("Abort")
        return

    camera_model = input("Camera model?")

    skipped_files = []

    for file in tqdm(files, desc="Organizing photos", unit="file"):
        # mtime = datetime.fromtimestamp(file.stat().st_mtime)  # 修改时间
        # ctime = datetime.fromtimestamp(file.stat().st_ctime)  # 创建时间

        # earliest = min(mtime, ctime)
        earliest = min(date_mapping[file.stem])
        date_str = earliest.strftime("%Y-%m-%d")

        if camera_model:
            date_str = date_str + "_" + camera_model
        date_folder = target / date_str
        date_folder.mkdir(exist_ok=True)

        dst_file = date_folder / file.name
        if dst_file.exists():
            tqdm.write(f"Skipping {dst_file.name}, already exists.")
            skipped_files.append(file)
        else:
            if debug:
                tqdm.write(f"Debug : \nFrom {file} \nTo {dst_file}")
            else:
                shutil.move(file, dst_file)

    print(f"Skip {len(skipped_files)} files.")
