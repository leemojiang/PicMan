import pprint
import shutil
from pathlib import Path
from typing import List
from tqdm import tqdm



def organize_photos_by_filetype(source_dir: str, suffix:List[str] = [".mkv",".mp4"] ,debug:bool = False):
    source = Path(source_dir).resolve()
    target_folder = source / "Videos"
    target_folder.mkdir(exist_ok=True)

    suffix_lower = [s.lower() for s in suffix]

    if not source.exists():
        raise FileNotFoundError(f"Source directory {source} does not exist.")
    
    files = [f for f in source.iterdir() if f.is_file() and f.suffix.lower() in suffix_lower]
    if not files:
        print("No files found in source directory.")
        return

    
    pprint.pp(files)
    if input("Process? [Y/N]?").lower() == 'y':
        print("Process")
    else:
        print("Abort")
        return

    file_names ={f.stem for f in files}
    all_files = [f for f in source.iterdir() if f.is_file()]
    for file in all_files:
        if file.stem in file_names:
            dst_file = target_folder / file.name

            if dst_file.exists():
                tqdm.write(f"Skipping {dst_file.name}, already exists.")
            else:
                if debug:
                    tqdm.write(f"Debug : \nFrom {file} \nTo {dst_file}")
                else:
                    shutil.move(file,dst_file)
               
