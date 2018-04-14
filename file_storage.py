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

	def delete_file(self):
		os.unlink( self.get_upload_path() )

	def resource_exists(self):
		return os.path.lexists( self.get_upload_path() )

	def upload_chunk(self, offset, data):
		upload_file_path = self.get_upload_path()
		try:
			f = open( upload_file_path, "r+b")
		except IOError:
			f = open( upload_file_path, "wb")
		finally:
			f.seek( offset )
			f.write(data)
			f.close()

	def finish_upload(self, filename):
		path = os.path.join( self.upload_folder, filename)
		os.rename( self.get_upload_path(), path)
		return path