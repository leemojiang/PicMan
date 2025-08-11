import shutil
from datetime import datetime
from pathlib import Path
from tqdm import tqdm  # 进度条库

def organize_photos_by_date(source_dir: str, target_dir: str,debug:bool):
    source = Path(source_dir).resolve()
    target = Path(target_dir).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source directory {source} does not exist.")

    files = [f for f in source.iterdir() if f.is_file()]
    if not files:
        print("No files found in source directory.")
        return
    
    key = input(f"Copy {len(files)} files? \nfrom {source.resolve()} \nto {target.resolve()} \n[Y/N]?" )
    if key.lower()=='y':
        print("Process")
    else:
        print("Abort")
        return
    
    camera_model = input(f"Camera model?")

    skipped_files = []

    for file in tqdm(files, desc="Organizing photos", unit="file"):

        mtime = datetime.fromtimestamp(file.stat().st_mtime)  # 修改时间
        ctime = datetime.fromtimestamp(file.stat().st_ctime)  # 创建时间

        earliest = min(mtime, ctime)
        date_str = earliest.strftime('%Y-%m-%d')

        if camera_model:
            date_str = date_str+"_"+camera_model
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
                shutil.move(file,dst_file)

    print(f"Skip {len(skipped_files)} files.")
