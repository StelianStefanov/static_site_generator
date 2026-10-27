import os
import shutil


def copy_contents(source, destination):
    if not os.path.exists(source):
        raise ValueError(f"Source directory does not exist: {source}")

    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        dest_path = os.path.join(destination, item)

        if os.path.isfile(source_path):
            print(f"Copying file: {source_path} -> {dest_path}")
            shutil.copy(source_path, dest_path)
        else:
            print(f"Copying directory: {source_path} -> {dest_path}")
            copy_contents(source_path, dest_path)

