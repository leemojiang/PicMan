import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from pprint import pprint

from exiftool import ExifToolHelper


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
    try:
        # 使用 ExifToolHelper 读取 EXIF 数据
        with ExifToolHelper() as et:
            metadata = et.get_metadata(str(file))
            assert len(metadata) == 1
            metadata = metadata[0]

        # 获取 Rating 和 XPKeywords
        rating = metadata.get("XMP:Rating", None)
        # raw_keywords = metadata.get("XMP:XPKeywords", "")
        raw_keywords = metadata.get("XMP:Label", None)
        # print(raw_keywords)

        # 解码和清理关键字
        if isinstance(raw_keywords, str):
            keywords = raw_keywords
        elif isinstance(raw_keywords, bytes):
            keywords = raw_keywords.decode("utf-16", errors="ignore")
        else:
            keywords = ""

        # tags = re.split(r"[;,]+", keywords)
        # clean_tags = [tag.strip() for tag in tags if tag.strip()]

        return {"Rating": rating, "Label": keywords}

    except Exception as e:
        print(f"Cannot read EXIF: {e}")
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


def organize_by_rating(source_dir: str, debug: bool = False):
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
        for file in dir_.iterdir():
            if file.is_file():
                metadata = get_metadata(file)
                # pprint(metadata)
                rating = metadata.get("Rating", None)
                label = metadata.get("Label", None)
                if rating:
                    file_rating.setdefault(file.stem, []).append(rating)
                if label:
                    file_label.setdefault(file.stem, []).append(label)

    def move_files_in_path(dir: Path):
        # move file
        for file in dir.iterdir():
            if file.is_file():
                rating = file_rating.get(file.stem,[])
                if not rating:
                    target = pending_dir / file.name  
                
                elif max(rating) == -1: # Rating -1 is reject
                    target = delete_dir / file.name
                else: # Base dir
                    target = source /file.name


                if debug:
                    print(f"Moving file: {file.name} -> {target}")
                else:
                    if not target.exists():  # 检查目标文件是否存在
                        shutil.move(file, target)
                    else:
                        print(f"File '{target}' already exists, skipping...")

    rate_files_in_path(source)
    rate_files_in_path(delete_dir)
    rate_files_in_path(pending_dir)

    if debug:
        pprint(file_rating)
        # pprint(file_label)
    
    move_files_in_path(source)
    move_files_in_path(delete_dir)
    move_files_in_path(pending_dir)

    
