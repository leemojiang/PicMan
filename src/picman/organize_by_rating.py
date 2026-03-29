import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from pprint import pprint

import piexif
from tqdm import tqdm

def parse_bridge_xml(file: Path):
    try:
        # 解析 XML 文件
        tree = ET.parse(file)
        root = tree.getroot()

        # 定义命名空间
        ns = {
            "x": "adobe:ns:meta/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "xmp": "http://ns.adobe.com/xap/1.0/",
        }

        # 寻找 rdf:Description 节点
        description_elem = root.find(".//rdf:Description", ns)
        if description_elem is None:
            raise ValueError("未找到 rdf:Description 节点")

        # 提取 Rating
        rating = None
        if "{" + ns["xmp"] + "}Rating" in description_elem.attrib:
            rating = int(description_elem.attrib["{" + ns["xmp"] + "}Rating"])

        # 提取 Label
        label = None
        if "{" + ns["xmp"] + "}Label" in description_elem.attrib:
            label = description_elem.attrib["{" + ns["xmp"] + "}Label"]

        return {"Rating": rating, "Label": label}

    except Exception as e:
        print(f"错误: {e}")
        return {}


def parse_image_exif(file: Path):
    """
    Read EXIF and XMP metadata from image file.
    piexif can read XMP data stored in JPEG/TIFF files.
    """
    try:
        exif_dict = piexif.load(str(file))
        
        rating = None
        label = None
        
        # Extract XMP data if available
        if "XMP" in exif_dict:
            xmp_data = exif_dict["XMP"].decode('utf-8', errors='ignore')
            
            # Parse Rating from XMP
            if '<xmp:Rating>' in xmp_data:
                try:
                    start = xmp_data.find('<xmp:Rating>') + len('<xmp:Rating>')
                    end = xmp_data.find('</xmp:Rating>')
                    rating = int(xmp_data[start:end])
                except (ValueError, IndexError):
                    rating = None
            
            # Parse Label from XMP
            if '<xmp:Label>' in xmp_data:
                try:
                    start = xmp_data.find('<xmp:Label>') + len('<xmp:Label>')
                    end = xmp_data.find('</xmp:Label>')
                    label = xmp_data[start:end]
                except IndexError:
                    label = None
        
        # Also check 0th IFD for some camera-specific rating tags
        if "0th" in exif_dict:
            exif_data = exif_dict["0th"]
            # Tag 18246 (0x4726) - Author, some cameras use for rating
            # Tag 18247 (0x4727) - Comments
            pass
        
        return {"Rating": rating, "Label": label}

    except Exception as e:
        tqdm.write(f"Cannot read EXIF: {file.name} - {e}")
        return {}


def get_metadata(file: Path):
    # 支持的图片格式
    image_extensions = {".jpg", ".jpeg", ".tiff", ".dng", ".png", ".orf", ".arw"}
    meta_extensions = {".xml", ".xmp"}
    if file.suffix.lower() in image_extensions:
        return parse_image_exif(file)

    elif file.suffix.lower() in meta_extensions:
        return parse_bridge_xml(file)

    return {}


def organize_by_rating(source_dir: str = "./", debug: bool = False):
    source = Path(source_dir)
    delete_dir = source / "delete"
    pending_dir = source / "pending"

    # 创建目标文件夹
    delete_dir.mkdir(exist_ok=True)
    pending_dir.mkdir(exist_ok=True)

    # Rating files
    file_rating = {}
    file_label = {}

    def rate_files_in_path(dir_: Path):
        files = [f for f in dir_.iterdir() if f.is_file()]

        for file in tqdm(files,desc=f"Rating files in {dir_}", unit='file'):
            metadata = get_metadata(file)
            # pprint(metadata)
            rating = metadata.get("Rating", None)
            label = metadata.get("Label", None)
            if rating:
                file_rating.setdefault(file.stem, []).append(rating)
            if label:
                file_label.setdefault(file.stem, []).append(label)

    def move_files_in_path(dir_: Path):
        # move file

        files = [f for f in dir_.iterdir() if f.is_file()]

        for file in tqdm(files,desc=f"Organizing files in {dir_}", unit='file'):
            rating = file_rating.get(file.stem,[])
            if not rating:
                target = pending_dir / file.name  
            
            elif max(rating) == -1: # Rating -1 is reject
                target = delete_dir / file.name
            else: # Base dir
                target = source /file.name


            if debug:
                tqdm.write(f"Moving file: {file.name} -> {target}")
            else:
                if not target.exists():  # 检查目标文件是否存在
                    shutil.move(file, target)
                else:
                    tqdm.write(f"File '{target}' already exists, skipping...")

    rate_files_in_path(source)
    rate_files_in_path(delete_dir)
    rate_files_in_path(pending_dir)

    if debug:
        pprint(file_rating)
        # pprint(file_label)
    
    move_files_in_path(source)
    move_files_in_path(delete_dir)
    move_files_in_path(pending_dir)

    
