from flask import request, jsonify, make_response, current_app
import base64
import os
import uuid
from upload_info import UploadInfo
from file_storage import FileStorage

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

class tus_manager(object):

    def __init__(self, app=None, upload_url='/file-upload', upload_folder='uploads/', overwrite=True, upload_finish_cb=None):
        self.app = app
        self.upload_info = {}
        if app is not None:
            self.init_app(app, upload_url, upload_folder, overwrite=overwrite, upload_finish_cb=upload_finish_cb)

    def init_app(self, app, upload_url='/file-upload', upload_folder='uploads/', overwrite=True, upload_finish_cb=None):

        self.upload_url = upload_url
        self.upload_folder = upload_folder
        self.tus_api_version = '1.0.0'
        self.tus_api_version_supported = '1.0.0'
        self.tus_api_extensions = ['creation', 'termination', 'file-check']
        self.tus_max_file_size = 4294967296 # 4GByte
        self.file_overwrite = overwrite
        self.upload_finish_cb = upload_finish_cb
        self.upload_file_handler_cb = None

        self.file_storage = FileStorage(upload_folder)

        # register the two file upload endpoints
        app.add_url_rule(self.upload_url, 'file-upload', self.tus_file_upload, methods=['OPTIONS', 'POST', 'GET'])
        app.add_url_rule('{}/<resource_id>'.format( self.upload_url ), 'file-upload-chunk', self.tus_file_upload_chunk, methods=['HEAD', 'PATCH', 'DELETE'])


    def upload_file_handler( self, callback ):
        self.upload_file_handler_cb = callback
        return callback

    def tus_file_upload(self):

        response = make_response("", 200)

        if request.method == 'GET':
            metadata = {}
            for kv in request.headers.get("Upload-Metadata", None).split(","):
                (key, value) = kv.split(" ")
                metadata[key] = base64.b64decode(value)

            if metadata.get("filename", None) is None:
                return make_response("metadata filename is not set", 404)

            if self.file_storage.file_exists(metadata.get("filename")):
                response.headers['Tus-File-Name'] = metadata.get("filename")
                response.headers['Tus-File-Exists'] = True
            else:
                response.headers['Tus-File-Exists'] = False
            return response

        elif request.method == 'OPTIONS' and request.headers.get('Access-Control-Request-Method', None) is not None:
            # CORS option request, return 200
            return response

        if request.headers.get("Tus-Resumable") is not None:
            response.headers['Tus-Resumable'] = self.tus_api_version
            response.headers['Tus-Version'] = self.tus_api_version_supported

            if request.method == 'OPTIONS':
                response.headers['Tus-Extension'] = ",".join(self.tus_api_extensions)
                response.headers['Tus-Max-Size'] = self.tus_max_file_size

                response.status_code = 204
                return response

            # process upload metadata
            metadata = {}
            if request.headers.get("Upload-Metadata", None) is not None:
                for kv in request.headers.get("Upload-Metadata", None).split(","):
                    (key, value) = kv.split(" ")
                    metadata[key] = base64.b64decode(value)
            if self.file_storage.file_is_uploaded( str(metadata.get("filename")) ) and self.file_overwrite is False:
                response.status_code = 409
                return response

            file_size = int(request.headers.get("Upload-Length", "0"))
            resource_id = str(uuid.uuid4())

            info = UploadInfo(file_size, 0, request.headers.get("Upload-Metadata"), metadata.get("filename"))
            self.upload_info = info.info

            try:
                self.file_storage.upload_file(resource_id, file_size)
            except Exception as e:
                self.app.logger.error("Unable to create file: {}".format(e))
                response.status_code = 500
                return response

            response.status_code = 201
            response.headers['Location'] = '{}/{}/{}'.format(request.url_root, self.upload_url, resource_id)
            response.headers['Tus-Temp-Filename'] = resource_id
            response.autocorrect_location_header = False

        else:
            self.app.logger.warning("Received File upload for unsupported file transfer protocol")
            response.data = "Received File upload for unsupported file transfer protocol"
            response.status_code = 500

        return response

    def tus_file_upload_chunk(self, resource_id):
        print(request)
        response = make_response("", 204)
        response.headers['Tus-Resumable'] = self.tus_api_version
        response.headers['Tus-Version'] = self.tus_api_version_supported

        offset = request.headers.get('Upload-Offset')
        upload_file_path = self.file_storage.get_upload_path()

        if request.method == 'HEAD':
            response.status_code = 404
            response.headers['Upload-Offset'] = offset
            response.headers['Cache-Control'] = 'no-store'
            return response
            #offset = None
            #if offset is None:
            #    response.status_code = 404
            #    return response

            #else:
            #    response.status_code = 200
            #    response.headers['Upload-Offset'] = offset
            #    response.headers['Cache-Control'] = 'no-store'

            #    return response

        if request.method == 'DELETE':
            os.unlink( upload_file_path )

            response.status_code = 204
            return respose
        
        if request.method == 'PATCH':
            filename = self.upload_info['upload_filename']
            if filename is None or os.path.lexists( upload_file_path ) is False:
                self.app.logger.info( "PATCH sent for resource_id that does not exist. {}".format( resource_id))
                response.status_code = 410
                return response

            file_offset = int(request.headers.get("Upload-Offset", 0))
            chunk_size = int(request.headers.get("Content-Length", 0))
            file_size = self.upload_info['upload_length']

            if int(request.headers.get("Upload-Offset")) != int(self.upload_info['upload_offset']): # check to make sure we're in sync
                print(request.headers.get("Upload-Offset"))
                print(self.upload_info['upload_offset'])
                response.status_code = 409 # HTTP 409 Conflict
                return response

            try:
                f = open( upload_file_path, "r+b")
            except IOError:
                f = open( upload_file_path, "wb")
            finally:
                f.seek( file_offset )
                f.write(request.data)
                f.close()

            self.upload_info['upload_offset'] = self.upload_info['upload_offset'] + chunk_size
            response.headers['Upload-Offset'] = self.upload_info['upload_offset']
            response.headers['Tus-Temp-Filename'] = resource_id

            if file_size == self.upload_info['upload_offset']: # file transfer complete, rename from resource id to actual filename
                if self.upload_file_handler_cb is None:
                    os.rename( upload_file_path, os.path.join( self.upload_folder, filename ))
                else:
                    filename = self.upload_file_handler_cb( upload_file_path, filename ) 

                if self.upload_finish_cb is not None:
                    self.upload_finish_cb()

            return response
