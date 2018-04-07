class UploadInfo:
	def __init__(self, upload_length, upload_offset, upload_metadata, upload_filename):
		self.info = {'upload_length': upload_length, 'upload_offset': upload_offset, 'upload_metadata': upload_metadata,
			'upload_filename': upload_filename}

	def info(self):
		return self.info