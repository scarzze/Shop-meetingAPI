import os
import cloudinary
import cloudinary.uploader
from typing import Optional, Dict, Any
from werkzeug.datastructures import FileStorage

class CloudinaryUploader:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )

    def upload_file(self, file: FileStorage, folder: str = None, public_id: str = None) -> Dict[str, Any]:
        """
        Upload a file to Cloudinary
        Returns dictionary containing 'url' and 'public_id'
        """
        try:
            if not file:
                raise ValueError("No file provided")

            upload_params = {
                "resource_type": "auto",
                "folder": folder
            }
            
            if public_id:
                upload_params["public_id"] = public_id

            upload_result = cloudinary.uploader.upload(file, **upload_params)
            
            return {
                "url": upload_result["secure_url"],
                "public_id": upload_result["public_id"]
            }
        except Exception as e:
            raise Exception(f"Error uploading file to Cloudinary: {str(e)}")

    def delete_file(self, public_id: str) -> bool:
        """
        Delete a file from Cloudinary using its public_id
        Returns True if successful, False otherwise
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            raise Exception(f"Error deleting file from Cloudinary: {str(e)}")

    def update_file(self, file: FileStorage, old_public_id: str, folder: str = None) -> Dict[str, Any]:
        """
        Update a file in Cloudinary by deleting the old one and uploading the new one
        Returns dictionary containing new 'url' and 'public_id'
        """
        self.delete_file(old_public_id)
        return self.upload_file(file, folder)

# Create a singleton instance
cloudinary_uploader = CloudinaryUploader()