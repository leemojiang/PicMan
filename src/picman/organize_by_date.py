import shutil
from datetime import datetime
from pathlib import Path

import exiftool
from tqdm import tqdm  # 进度条库


def get_exif_date(file_path: Path):
    with exiftool.ExifToolHelper() as tool:
        metadata = tool.get_metadata(file_path)
        assert len(metadata) == 1
        creation_date = metadata[0].get("EXIF:DateTimeOriginal", None)
        return creation_date


def organize_photos_by_date(source_dir: str, target_dir: str, debug: bool):
    source = Path(source_dir).resolve()
    target = Path(target_dir).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source directory {source} does not exist.")

    files = [f for f in source.iterdir() if f.is_file()]
    if not files:
        print("No files found in source directory.")
        return

    date_mapping = {}
    for f in files:
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
