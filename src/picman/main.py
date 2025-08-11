import argparse
from picman.organize_by_date import organize_photos_by_date


def main():
    parser = argparse.ArgumentParser(description="Organize photos by creation date.")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "-t", "--organize-by-date", action="store_true", help="按日期整理照片"
    )
    mode.add_argument(
        "-g", "--organize-by-group", action="store_true", help="按照打分等级整理照片"
    )

    parser.add_argument(
        "-d", "--debug", action="store_true", help="进行debug"
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
    elif args.organize_by_group:
        return


if __name__ == "__main__":
    main()
