import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "packrat.settings")

from cinp.django_file_handler import FILE_STORAGE

if not os.path.isdir( FILE_STORAGE ):
  os.makedirs( FILE_STORAGE )

import django
django.setup()

from packrat.app import get_app

application = get_app( False )
