class cloudinary_uploader:
    """
    Stub implementation of cloudinary uploader for DEBUG_MODE
    """
    @staticmethod
    def upload(file_data, **options):
        """
        Mock implementation of cloudinary upload
        Returns a mock response with a secure_url
        """
        return {
            'secure_url': 'https://example.com/mock-image.jpg',
            'public_id': 'mock-image-id'
        }
