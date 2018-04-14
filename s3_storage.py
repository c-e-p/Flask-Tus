import boto3
import botocore

class S3Storage:
	def __init__(self, upload_folder):
		self.upload_folder = upload_folder
		self.resource_id = 0
		self.parts = []
		self.s3 = boto3.resource('s3')
		self.client = boto3.client('s3')

	def file_exists(self, filename):		
		try:
			self.filename = filename
			self.s3.Object(self.upload_folder, filename).load()  
			return True  		
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				return False
			else:
				raise

	def file_is_uploaded(self, filename):
		try:
			self.s3.Object(self.upload_folder, filename).load()
			return True 		
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				return False
			else:
				raise

	def upload_file(self, resource_id, file_size):
		response = self.client.create_multipart_upload(
		    ACL='public-read',
		    Bucket='ourchive-test-bucket',
		    ContentType=self.upload_info['upload_metadata']["content_type"],
		    Key=self.upload_info['upload_filename']
		)
		self.upload_info['s3_response'] = response
		self.upload_info['part_number'] = 1
		self.upload_info['parts'] = {'Parts' :[]}

	def delete_file(self):
		response = self.client.delete_object(
		    Bucket='ourchive-test-bucket',
		    Key=self.upload_info['upload_filename']
		)
		return response

	def upload_chunk(self, offset, data):
		response = self.client.upload_part(
		    Body=data,
		    Bucket='ourchive-test-bucket',
		    Key=self.upload_info['upload_filename'],
		    PartNumber=self.upload_info['part_number'],
		    UploadId=self.upload_info['s3_response']['UploadId']
		)		
		new_part = {}
		new_part['ETag'] = response['ETag']
		new_part['PartNumber'] = self.upload_info['part_number']
		self.upload_info['parts']['Parts'].append(new_part)
		self.upload_info['part_number'] += 1
		return response

	def finish_upload(self, filename):
		response = self.client.complete_multipart_upload(
		    Bucket='ourchive-test-bucket',
		    Key=self.upload_info['upload_filename'],
		    MultipartUpload=self.upload_info['parts'],
		    UploadId=self.upload_info['s3_response']['UploadId']
		)
		return response