import boto3
import botocore

class S3Storage:
	def __init__(self, upload_folder):
		self.upload_folder = upload_folder
		self.resource_id = 0
		s3 = boto3.resource('s3')

	def file_exists(self, filename):		
		try:
			s3.Object(self.upload_folder, filename).load()    		
		except botocore.exceptions.ClientError as e:
    		if e.response['Error']['Code'] == "404":
        		return False
    		else:
        		raise

	def file_is_uploaded(self, filename):
		try:
			s3.Object(self.upload_folder, filename).load()    		
		except botocore.exceptions.ClientError as e:
    		if e.response['Error']['Code'] == "404":
        		return False
    		else:
        		raise

	def upload_file(self, resource_id, file_size):
		return "not implemented"

	def get_upload_path(self):
		return "not implemented"

	def delete_file(self):
		return "not implemented"

	def resource_exists(self):
		return False

	def upload_chunk(self, offset, data):
		return "not implemented"

	def finish_upload(self, filename):
		return "not implemented"