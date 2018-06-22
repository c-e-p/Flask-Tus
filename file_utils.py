import magic

def file_is_audio(file):
	file_type = magic.from_file(file)
	return('Audio file' in file_type)

def file_is_image(file):
	file_type = magic.from_file(file)
	return ('image data' in file_type)