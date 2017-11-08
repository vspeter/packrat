import os

from django.conf import settings

from cinp.server_common import Response


def files_handler( request ):  # For Dev only!!
  filename = request.uri[7: ]

  try:
    source_file = open( os.path.join( settings.MEDIA_ROOT, filename ), 'rb' )
  except FileNotFoundError:
    return Response( 404, data='file "{0}" not found'.format( filename ), content_type='text' )

  return Response( 200, data=source_file, content_type='bytes' )
