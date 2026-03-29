# PicMan

PicMan is a Python command-line tool for efficient photo management and organization. It helps you automatically organize your photo collection based on date, file type, and ratings.

### Updates 10.10.2025
  Using Typer to build Cli tool.


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
- Organizes photos based on ratings 
- Automatically moves files with rating "-1" or tag "Reject" to a "delete" folder
- Automatically moves files without rating to a "pending" folder
- Supports reading metadata from both image EXIF and Adobe Bridge XML files

## Installation
```bash
# Check and previou version
uv tool list 

# uninstall previous version if exists
uv tool uninstall picman

# Install the package
uv tool install git+https://github.com/leemojiang/PicMan.git

```

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/picman.git

# Navigate to the project directory
cd picman

# Sync project with uv
uv sync

# # Install the package
# uv tool install -e . --upgrade
```

## Requirements

- Python 3.11 or higher
- Dependencies:
  - pyexiftool (>=0.5.6)
  - tqdm (>=4.67.1)
  - typer>=0.19.2

## Usage

PicMan can be used with the `pm` command after installation, use `pm command --help` for more information.

### Organize Photos by Date

```bash
# Basic usage (uses current directory as source and parent directory as target)
pm date 

# Specify source and target directories
pm date /path/to/photos /path/to/destination

# Enable debug mode (shows operations without moving files)
pm date --debug
```

During execution, you'll be prompted to confirm the operation and optionally provide a camera model to include in the folder names.

### Organize Videos by File Type

```bash
# Move video files to a "Videos" subfolder in the current directory
pm type

# Enable debug mode
pm type --debug
```

This command will identify files with specified extensions (default: .mkv, .mp4, .mov) and move them, along with any related files sharing the same base name, to a "Videos" subfolder.

### Organize Photos by Rating

```bash
# Organize photos in the current directory based on ratings
pm rate

# Enable debug mode
pm rate --debug
```

This command reads EXIF data from images and Adobe Bridge XMP files to organize photos based on ratings:
- Files with rating "-1" or "Reject" are moved to a "delete" subfolder
- Files without rating are moved to a "pending" subfolder
- Other files remain in their original location

