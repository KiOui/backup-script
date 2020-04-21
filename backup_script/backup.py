import os.path
import os
from argparse import ArgumentParser
import shutil
from datetime import datetime
from distutils.dir_util import copy_tree

TEMP_FOLDER = ".backup"


def get_files(path):
    """
    Get the files in path.

    :param path: the path
    :return: a list of all files in path
    """
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def get_zip_files(path):
    """
    Get all zip files in path.

    :param path: the path
    :return: a list of zip files in path
    """
    return [f for f in get_files(path) if f.endswith(".zip")]


def strip_extension(file):
    """
    Strip the extension of a file.

    :param file: the file
    :return: the filename without extension
    """
    return os.path.splitext(file)[0]


def date_to_string(date):
    """
    Convert a date to string.

    :param date: the date
    :return: date in string format
    """
    return str(date).split(".")[0].replace(":", ".")


def is_datetime(string):
    """
    Check if a string can be converted to a datetime object.

    :param string: the string
    :return: True if the string can be converted to a datetime object, False otherwise
    """
    try:
        datetime.strptime(string, "%Y-%m-%d %H.%M.%S")
    except Exception:
        return False
    return True


def backups_to_remove(amount, backup_folder):
    """
    Get a list of backups that have expired.

    :param amount: the maximum amount of backups to keep
    :param backup_folder: the folder where the backups are stored
    :return: a list of removed backups
    """
    all_zips = [
        f for f in get_zip_files(backup_folder) if is_datetime(strip_extension(f))
    ]
    all_zips.sort()
    to_remove = []
    today = date_to_string(datetime.now())
    if today in [strip_extension(f) for f in all_zips]:
        to_remove = to_remove + [date_to_string(datetime.now())]
        all_zips.remove(today)
    while len(all_zips) > amount:
        to_remove = to_remove + [all_zips[0]]
        all_zips.remove(all_zips[0])
    return to_remove


def remove_backups(backup_list, backup_folder):
    """
    Remove a list of backups.

    :param backup_list: a list of backup files to remove
    :param backup_folder: the folder containing the backup files
    :return: None
    """
    for backup in backup_list:
        print("Removing old backup {}".format(os.path.join(backup_folder, backup)))
        os.remove(os.path.join(backup_folder, backup))


def create_temp_folder(backup_folder):
    """
    Create a temporary folder.

    :param backup_folder: the folder where the backups are located
    :return: the path of the created temporary folder
    """
    if not os.path.exists(os.path.join(backup_folder, TEMP_FOLDER)):
        os.makedirs(os.path.join(backup_folder, TEMP_FOLDER))
    return os.path.join(backup_folder, TEMP_FOLDER)


def copy_backup_folders(backup_folder, to_backup):
    """
    Copy all folder to backup to the backup_folder location.

    :param backup_folder: the folder to copy all files/folder in to_backup to
    :param to_backup: a list of files/folders to backup
    :return: True if there were no errors, False otherwise
    """
    for folder in to_backup:
        try:
            print("Backing up " + str(folder))
            if not os.path.exists(
                os.path.join(
                    backup_folder, folder.split("/")[len(folder.split("/")) - 1]
                )
            ):
                print(
                    "Creating folder "
                    + str(
                        os.path.join(
                            backup_folder, folder.split("/")[len(folder.split("/")) - 1]
                        )
                    )
                )
                os.makedirs(
                    os.path.join(
                        backup_folder, folder.split("/")[len(folder.split("/")) - 1]
                    )
                )
            copy_tree(
                folder,
                os.path.join(
                    backup_folder, folder.split("/")[len(folder.split("/")) - 1]
                ),
            )
            print("Copy complete")
        except Exception as e:
            print("Directory not copied. Error: {}".format(e))
            return False
    return True


def remove_backup_folder(folder):
    """
    Remove a folder.

    :param folder: the folder to remove
    :return: None
    """
    print("Removing {}".format(folder))
    shutil.rmtree(folder)


def zip_file(filename, backup_folder):
    """
    Zip a folder.

    :param filename: the file to zip
    :param backup_folder: the folder to store the zipfile in
    :return: None
    """
    print(
        "Storing backup in: {}".format(
            os.path.join(backup_folder, date_to_string(datetime.now()))
        )
    )
    shutil.make_archive(
        os.path.join(backup_folder, date_to_string(datetime.now())), "zip", filename
    )


if __name__ == "__main__":
    """
    Main function.
    
    Parse arguments and backup folders.
    """
    parser = ArgumentParser(description="Backup script")
    parser.add_argument(
        "backup_folder", help="folder to which the backups will be written"
    )
    parser.add_argument(
        "-a",
        "--amount",
        default=7,
        nargs="?",
        const=7,
        help="number of backups to keep",
        type=int,
    )
    parser.add_argument("folders", nargs="*")
    args = parser.parse_args()
    if args.amount <= 0:
        print("Please specify an amount higher than zero!")
    elif len(args.folders) < 1:
        print("Please specify folders to backup.")
    else:
        print("Starting backup...")
        remove = backups_to_remove(args.amount, args.backup_folder)
        remove_backups(remove, args.backup_folder)
        backup_folder = create_temp_folder(args.backup_folder)
        if copy_backup_folders(backup_folder, args.folders):
            zip_file(backup_folder, args.backup_folder)
            remove_backup_folder(backup_folder)
        else:
            print("Folder copying failed!")
