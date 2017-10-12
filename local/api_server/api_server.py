#!/usr/bin/env python3
import os

os.environ.setdefault( 'DJANGO_SETTINGS_MODULE', 'packrat.settings' )

import django
django.setup()

import sys
import logging

from gunicorn.app.base import BaseApplication
from cinp.server_werkzeug import WerkzeugServer
from cinp.django_file_handler import upload_handler

from packrat.User.models import getUser
from packrat.files_handler import files_handler

DEBUG = True


class GunicornApp( BaseApplication ):
  def __init__( self, application, options=None ):
    self.options = options or {}
    self.application = application
    super().__init__()

  def load_config( self ):
    for ( key, value ) in self.options.items():
      self.cfg.set( key.lower(), value )

  def load( self ):
    return self.application

if __name__ == '__main__':
  logging.basicConfig()
  logger = logging.getLogger()
  logger.setLevel( logging.DEBUG )
  logger.info( 'Starting up...' )

  logger.debug( 'Creating Server...' )
  app = WerkzeugServer( root_path='/api/v1/', root_version='1.0', debug=DEBUG, get_user=getUser, cors_allow_list=[ '*' ] )
  logger.debug( 'Registering Models...' )

  app.registerNamespace( '/', 'packrat.User' )
  app.registerNamespace( '/', 'packrat.Repos' )

  app.registerPathHandler( '/upload', upload_handler )
  app.registerPathHandler( '/files', files_handler )  # TODO: In prod  this should be handeled by the static web server

  logger.info( 'Validating...' )
  app.validate()

  logger.info( 'Starting Server...' )
  GunicornApp( app, { 'bind': '0.0.0.0:8888', 'loglevel': 'info', 'workers': 10 } ).run()
  logger.info( 'Server Done...' )
  logger.info( 'Shutting Down...' )
  logger.info( 'Done!' )
  logger.shutdown()
  sys.exit( 0 )
