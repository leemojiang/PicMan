import argparse
from picman.organize_by_date import organize_photos_by_date
from picman.organize_by_filetype import organize_photos_by_filetype
from picman.organize_by_rating import organize_by_rating

def main():
    parser = argparse.ArgumentParser(description="Organize photos by creation date.")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "-d", "--organize-by-date", action="store_true", help="按日期整理照片"
    )
    mode.add_argument(
        "-v", "--organize-by-type", action="store_true", help="把文件中的视频以及字幕移动到文件夹"
    )
    mode.add_argument(
        "-r", "--organize-by-rating", action="store_true", help="按照打分等级整理照片"
    )

    parser.add_argument(
        "-de", "--debug", action="store_true", help="debug flag"
    )

    parser.add_argument(
        "source", nargs="?", help="Source directory containing photos", default="./"
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Target directory to store organized photos",
        default="../",
    )

    args = parser.parse_args()
    if args.organize_by_date:
        organize_photos_by_date(args.source, args.target,args.debug)
    elif args.organize_by_type:
        organize_photos_by_filetype(args.source,suffix=[".mp4",".mov",".mkv"]  ,debug = args.debug)
    elif args.organize_by_rating:
        organize_by_rating(args.source,debug=args.debug)


if __name__ == "__main__":
    main()
