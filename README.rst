NOTE: this is all old and out of date

=============================
packrat
=============================


A single interface for managing apt, yum, and zypper repos.

Documentation
-------------

The full documentation is at https://github.emcrubicon.com/packrat/packrat/wiki.

Quickstart
----------

Setup setting.py::

    By default the database will be a sqlite3 db called 'db.sqlite3' which will be placed in the same director as manage.py, modify the default database to change that.
    By default the files will be uploaded to 'file', this is set by MEDIA_ROOT, and the URLs to thoes files are prefixed by MEDIA_URL, in production MEDIA_URL should be an alias in the apache config to MEDIA_ROOT

Setup Database::

    python manage.py migrate
    python manage.py addsuperuser
    < follow the prompts >

    If you would like some example data, run this following the migrate and addsuperuser
    python manage.py loaddata example_data.json

Setup File Store location::

    files will be upaded to MEDIA_ROOT as mencioned above, make sure you have proper permissions to this folder.

Run the project locally for debugging::

    python manage.py runserver

When running in production, make sure the settings.py is updated to put the database and the files in a proper spot, not in BASE_DIR

Features
--------

* TODO
