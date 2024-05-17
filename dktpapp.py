import os
import shutil
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, simpledialog
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys
import webbrowser

class PDFMoverUploaderApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF Mover and Uploader")

        self.label = Label(master, text="PDF Mover and Uploader")
        self.label.pack()

        self.source_button = Button(master, text="Select Source Directory", command=self.select_source_directory)
        self.source_button.pack()

        self.source_entry = Entry(master, width=50)
        self.source_entry.pack()

        self.destination_button = Button(master, text="Select Destination Directory", command=self.select_destination_directory)
        self.destination_button.pack()

        self.destination_entry = Entry(master, width=50)
        self.destination_entry.pack()

        self.move_button = Button(master, text="Move PDFs", command=self.move_pdfs)
        self.move_button.pack()

        self.upload_button = Button(master, text="Upload to Google Drive", command=self.upload_to_drive)
        self.upload_button.pack()

        self.source_directory = None
        self.destination_directory = None

    def select_source_directory(self):
        self.source_directory = filedialog.askdirectory()
        self.source_entry.delete(0, 'end')
        self.source_entry.insert(0, self.source_directory)

    def select_destination_directory(self):
        self.destination_directory = filedialog.askdirectory()
        self.destination_entry.delete(0, 'end')
        self.destination_entry.insert(0, self.destination_directory)

    def move_pdfs(self):
        if not self.source_directory or not self.destination_directory:
            messagebox.showerror("Error", "Please select both source and destination directories")
            return

        print(f"Moving files from {self.source_directory} to {self.destination_directory}")
        if not os.path.exists(self.destination_directory):
            os.makedirs(self.destination_directory)
            print(f"Created directory {self.destination_directory}")

        for filename in os.listdir(self.source_directory):
            if filename.endswith('.pdf'):
                source_path = os.path.join(self.source_directory, filename)
                dest_path = os.path.join(self.destination_directory, filename)
                try:
                    shutil.move(source_path, dest_path)
                    print(f"Moved: {filename}")
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
        messagebox.showinfo("Success", "PDF files moved successfully!")

    def upload_to_drive(self):
        if not self.destination_directory:
            messagebox.showerror("Error", "Please select a destination directory")
            return

        print("Authenticating with Google Drive...")
        gauth = GoogleAuth()

        # Use the absolute path to the client_secrets.json file
        client_secrets_path = os.path.join(os.path.dirname(sys.executable), 'client_secrets.json') if hasattr(sys, '_MEIPASS') else 'client_secrets.json'
        gauth.settings['client_config_file'] = client_secrets_path

        try:
            gauth.LoadCredentialsFile("mycreds.txt")
        except Exception as e:
            print(f"Error loading credentials: {e}")

        if gauth.credentials is None:
            gauth.CommandLineAuth() #LocalWebserverAuth()
            if gauth.credentials is None:
                auth_url = gauth.GetAuthUrl()
                webbrowser.open(auth_url)
                auth_code = simpledialog.askstring("Authentication", "Enter the authentication code:")
                gauth.Auth(auth_code)
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile("mycreds.txt")
        drive = GoogleDrive(gauth)
        print("Authentication successful.")

        files_to_upload = [f for f in os.listdir(self.destination_directory) if f.endswith('.pdf')]
        if not files_to_upload:
            messagebox.showerror("Error", f"No PDF files found in {self.destination_directory} to upload.")
            return

        folder_metadata = {'title': 'PDF_Files', 'mimeType': 'application/vnd.google-apps.folder'}
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']
        print(f"Created new folder with ID: {folder_id}")

        for filename in files_to_upload:
            file_path = os.path.join(self.destination_directory, filename)
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
        messagebox.showinfo("Success", "PDF files uploaded to Google Drive successfully!")

if __name__ == "__main__":
    root = Tk()
    app = PDFMoverUploaderApp(root)
    root.mainloop()