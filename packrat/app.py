from cinp.server_werkzeug import WerkzeugServer
from cinp.django_file_handler import upload_handler

from packrat.User.models import getUser
# from packrat.files_handler import files_handler


def get_app( debug ):
  app = WerkzeugServer( root_path='/api/v1/', root_version='1.0', debug=debug, get_user=getUser, cors_allow_list=[ '*' ] )

  app.registerNamespace( '/', 'packrat.User' )
  app.registerNamespace( '/', 'packrat.Repos' )

  app.registerPathHandler( '/api/upload', upload_handler )
  # app.registerPathHandler( '/files', files_handler )  # TODO: In prod  this should be handeled by the static web server

  app.validate()

  return app
