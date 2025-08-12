import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from pprint import pprint

import piexif


def parse_bridge_xml(file: Path):
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        # 通常 Bridge 使用 XMP 格式，命名空间可能需要处理
        ns = {
            "x": "adobe:ns:meta/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "xmp": "http://ns.adobe.com/xap/1.0/",
            "xmp:Rating": "http://ns.adobe.com/xap/1.0/",
            "xmp:Keywords": "http://ns.adobe.com/xap/1.0/DynamicMedia/",
        }

        rating = None
        keywords = []

        # 查找 rating
        rating_elem = root.find(".//xmp:Rating", ns)
        if rating_elem is not None:
            rating = int(rating_elem.text)

        # 查找关键词（可能是多个 li 元素）
        keyword_elems = root.findall(".//rdf:li", ns)
        for elem in keyword_elems:
            if elem.text:
                keywords.append(elem.text.strip())

        return {"Rating": rating, "XPKeywords": keywords}
    except Exception as e:  # noqa: F841
        return {}


def parse_image_exif(file: Path):
    try:
        exif_dict = piexif.load(str(file))
        rating = exif_dict["0th"].get(piexif.ImageIFD.Rating, None)
        raw_keywords = exif_dict["0th"].get(piexif.ImageIFD.XPKeywords, b"")

        if isinstance(raw_keywords, bytes):
            keywords = raw_keywords.decode("utf-16", errors="ignore")
        elif isinstance(raw_keywords, list):
            keywords = bytes(raw_keywords).decode("utf-16", errors="ignore")
        else:
            keywords = ""

        tags = re.split(r"[;,]+", keywords)
        clean_tags = [tag.strip() for tag in tags if tag.strip()]

        return {"Rating": rating, "XPKeywords": clean_tags}
    except Exception as e:
        print(f"Can not read EXIF:{e}")
        return {}


def get_metadata(file: Path):
    # 支持的图片格式
    image_extensions = {".jpg", ".jpeg", ".tiff"}
    meta_extensions = {".xml"}
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

    def rate_files_in_path(dir: Path):
        for file in dir.iterdir():
            if file.is_file():
                metadata = get_metadata(file)
                # pprint(metadata)
                rating = metadata.get("Rating", None)
                tags = metadata.get("XPKeywords", [])

                file_rating.setdefault(file.stem, []).extend(tags)
                if rating:
                    file_rating[file.stem].append(rating)

    def move_files_in_path(dir: Path):
        # move file
        for file in dir.iterdir():
            tags = file_rating[file.stem]
            # 判断移动逻辑
            if 1 in tags or "Delete" in tags:
                target = delete_dir / file.name
            elif 2 in tags or "Pending" in str(tags):
                target = pending_dir / file.name
            else:
                continue  # 保留在原目录

            if debug:
                print(f"移动文件: {file.name} -> {target}")
            else:
                shutil.move(str(file), str(target))

    rate_files_in_path(source)
    pprint(file_rating)
