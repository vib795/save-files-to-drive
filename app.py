import os
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Function to move PDF files
def move_pdf_files(source_dir, dest_dir):
    print(f"Moving files from {source_dir} to {dest_dir}")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created directory {dest_dir}")
    for filename in os.listdir(source_dir):
        if filename.endswith('.pdf'):
            source_path = os.path.join(source_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            try:
                shutil.move(source_path, dest_path)
                print(f"Moved: {filename}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")

# Function to upload files to Google Drive
def upload_files_to_drive(dest_dir, folder_id=None):
    print("Authenticating with Google Drive...")
    gauth = GoogleAuth()
    gauth.CommandLineAuth()  # Use CommandLineAuth instead of LocalWebserverAuth
    drive = GoogleDrive(gauth)
    print("Authentication successful.")

    # Verify files in destination directory
    files_to_upload = [f for f in os.listdir(dest_dir) if f.endswith('.pdf')]
    if not files_to_upload:
        print(f"No PDF files found in {dest_dir} to upload.")
        return

    # Get the folder or create if it doesn't exist
    if folder_id:
        folder = drive.CreateFile({'id': folder_id})
    else:
        folder_metadata = {
            'title': 'PDF_Files',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']
        print(f"Created new folder with ID: {folder_id}")

    # Upload files to Google Drive
    for filename in files_to_upload:
        file_path = os.path.join(dest_dir, filename)
        print(f"Preparing to upload: {filename}")
        try:
            file_list = drive.ListFile({'q': f"'{folder_id}' in parents and title='{filename}'"}).GetList()
            if file_list:
                file_drive = file_list[0]
                file_drive.SetContentFile(file_path)
                file_drive.Upload()
                print(f"Updated: {filename}")
            else:
                file_drive = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
                file_drive.SetContentFile(file_path)
                file_drive.Upload()
                print(f"Uploaded: {filename}")
        except Exception as e:
            print(f"Error uploading {filename}: {e}")

if __name__ == '__main__':
    source_directory = 'tests/source'  # Change this to your source directory
    destination_directory = 'tests/destination'  # Change this to your destination directory
    drive_folder_id = None  # Change this to your folder ID or set to None

    print("Starting to move files...")
    move_pdf_files(source_directory, destination_directory)
    print("Finished moving files.")
    
    # Check if files exist in destination directory
    if not os.listdir(destination_directory):
        print(f"No files found in {destination_directory}. Please check the source directory and try again.")
    else:
        print("Starting to upload files to Google Drive...")
        upload_files_to_drive(destination_directory, drive_folder_id)
        print("Finished uploading files.")
