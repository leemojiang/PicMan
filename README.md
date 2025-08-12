# PicMan

PicMan is a Python command-line tool for efficient photo management and organization. It helps you automatically organize your photo collection based on date, file type, and ratings.

## Features

### Date-based Organization
- Automatically sorts photos into folders based on their creation date
- Creates a structured directory hierarchy for easy navigation
- Option to include camera model in folder names

### Video File Management
- Identifies and moves video files (and related files) into a dedicated "Videos" folder
- Supports common video formats (MP4, MOV, MKV)
- Preserves file relationships by moving files with the same base name

### Rating and Tag Management
- Organizes photos based on ratings and tags from EXIF data
- Automatically moves files with rating "1" or tag "Delete" to a "delete" folder
- Automatically moves files with rating "2" or tag "Pending" to a "pending" folder
- Supports reading metadata from both image EXIF and Adobe Bridge XML files

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/picman.git

# Navigate to the project directory
cd picman

# Sync project with uv
uv sync

# Install the package
uv tool install -e . --upgrade
```

## Requirements

- Python 3.11 or higher
- Dependencies:
  - piexif (>=1.1.3)
  - tqdm (>=4.67.1)

## Usage

PicMan can be used with the `pm` command after installation:

### Organize Photos by Date

```bash
# Basic usage (uses current directory as source and parent directory as target)
pm -d

# Specify source and target directories
pm -d /path/to/photos /path/to/destination

# Enable debug mode (shows operations without moving files)
pm -d --debug
```

During execution, you'll be prompted to confirm the operation and optionally provide a camera model to include in the folder names.

### Organize Videos by File Type

```bash
# Move video files to a "Videos" subfolder in the current directory
pm -v

# Enable debug mode
pm -v --debug
```

This command will identify files with specified extensions (default: .mkv, .mp4, .mov) and move them, along with any related files sharing the same base name, to a "Videos" subfolder.

### Organize Photos by Rating

```bash
# Organize photos in the current directory based on ratings
pm -r

# Enable debug mode
pm -r --debug
```

This command reads EXIF data from images and Adobe Bridge XML files to organize photos based on ratings:
- Files with rating "1" or tag "Delete" are moved to a "delete" subfolder
- Files with rating "2" or tag "Pending" are moved to a "pending" subfolder
- Other files remain in their original location

## Command Reference

```
usage: pm [-h] (-d | -v | -r) [-de] [source] [target]

Organize photos by creation date.

positional arguments:
  source                Source directory containing photos (default: current directory)
  target                Target directory to store organized photos (default: parent directory)

options:
  -h, --help            show this help message and exit
  -d, --organize-by-date
                        按日期整理照片
  -v, --organize-by-type
                        把文件中的视频以及字幕移动到文件夹
  -r, --organize-by-rating
                        按照打分等级整理照片
  -de, --debug          debug flag