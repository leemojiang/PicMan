from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import piexif
import pytest

from picman.organize_by_date import get_exif_date

# 把你的真实测试图片放到这个目录。
# 你也可以通过环境变量 PICMAN_TEST_FILES_DIR 覆盖它。
TEST_FILES_DIR = Path(
    os.getenv("PICMAN_TEST_FILES_DIR", r"C:\Users\LEEL\Desktop\PicMan\tests\test_files")
)


def test_get_exif_date_returns_datetimeoriginal(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = b"2024:01:02 03:04:05"

    def fake_load(_path: str) -> dict:
        return {
            "Exif": {piexif.ExifIFD.DateTimeOriginal: expected},
            "0th": {},
        }

    monkeypatch.setattr(piexif, "load", fake_load)

    result = get_exif_date(Path("dummy.jpg"))

    assert result == "2024:01:02 03:04:05"


def test_get_exif_date_falls_back_to_ifd0_datetime(monkeypatch: pytest.MonkeyPatch) -> None:
    fallback = b"2023:12:31 23:59:59"

    def fake_load(_path: str) -> dict:
        return {
            "Exif": {},
            "0th": {piexif.ImageIFD.DateTime: fallback},
        }

    monkeypatch.setattr(piexif, "load", fake_load)

    result = get_exif_date(Path("dummy.jpg"))

    assert result == "2023:12:31 23:59:59"


def test_get_exif_date_returns_none_when_no_datetime(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_load(_path: str) -> dict:
        return {"Exif": {}, "0th": {}}

    monkeypatch.setattr(piexif, "load", fake_load)

    result = get_exif_date(Path("dummy.jpg"))

    assert result is None


def test_get_exif_date_returns_none_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_load(_path: str) -> dict:
        raise RuntimeError("bad file")

    monkeypatch.setattr(piexif, "load", fake_load)

    result = get_exif_date(Path("broken.jpg"))

    assert result is None


def test_get_exif_date_with_user_real_files_path() -> None:
    # 这个测试会读取你在 TEST_FILES_DIR 里放的真实图片，验证返回值格式。
    # 如果想要看到具体日期 手动检查 uv run pytest -q -s （不捕获输出）并放一些图片在 TEST_FILES_DIR 里。
    if not TEST_FILES_DIR.exists():
        pytest.skip(f"Test files dir not found: {TEST_FILES_DIR}")

    image_files = [
        p
        for p in TEST_FILES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".orf", ".arw"}
    ]

    if not image_files:
        pytest.skip(f"No test image files found in: {TEST_FILES_DIR}")

    for image_file in image_files:
        result = get_exif_date(image_file)
        if result is not None:
            datetime.strptime(result, "%Y:%m:%d %H:%M:%S")
            print(f"{image_file.name}: EXIF date = {result}")
