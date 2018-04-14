import unittest
from s3_storage import S3Storage

class TestAuthBlueprint(unittest.TestCase):
	def test_create_class(self):
		storage = S3Storage('test_folder')
		self.assertEqual(storage.upload_folder, 'test_folder')

	def test_no_file(self):
		storage = S3Storage('ourchive-test-bucket')
		response = storage.file_exists('fakefile.txt')
		self.assertEqual(False, response)

	def test_real_file(self):
		storage = S3Storage('ourchive-test-bucket')
		response = storage.file_exists('realfile.txt')
		self.assertEqual(True, response)
		self.assertEqual('realfile.txt', storage.filename)