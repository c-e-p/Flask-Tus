import os

class FileStorage:
	def __init__(self, upload_folder):
		self.upload_folder = upload_folder
		self.resource_id = 0

	def file_exists(self, filename):
		(filename_name, extension) = os.path.splitext( filename )
		return filename_name.upper() in [os.path.splitext(f)[0].upper() for f in os.listdir( os.path.dirname( self.upload_folder ))]

	def file_is_uploaded(self, filename):
		return os.path.lexists( os.path.join( self.upload_folder, filename ))

	def upload_file(self, resource_id, file_size):
		self.resource_id = resource_id
		f = open( os.path.join( self.upload_folder, resource_id ), "wb")
		f.seek( file_size - 1)
		f.write(str.encode('\0'))
		f.close()

	def get_upload_path(self):
		return os.path.join( self.upload_folder, str(self.resource_id) )
	