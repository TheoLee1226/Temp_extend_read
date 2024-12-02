import os

def delete_files_with_name(directory, filename):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == filename:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

if __name__ == "__main__":
    directory = os.getcwd()
    filename = "desktop.ini"  
    delete_files_with_name(directory, filename)