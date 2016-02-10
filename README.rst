=============================
packrat
=============================

A single interface for managing apt, yum, and JSON repos.

Documentation
-------------


Setup
-----

After installing the package, first set up the Database::

  apt-get install postgresql
  su postgres
  createuser -R -S -D -P packrat   # the password should be `packrat`
  createdb -O packrat packrat
  cd /usr/local/packrat/util
  ./manage.py syncdb               # create a super user, with user/email/password that you chose, this will be needed for the admin site
  ./manage.py loaddata initial_data

You may want to tweek the apache config::

  a2dissite 000-default
  vi /etc/apache2/sites-available/packrat.conf # fix the ServerAliaz if desired
  /etc/init.d/apache2 restart

Now we can try loading our first package, goto the ip/host of your new packrat server in a browser.  Click the `UI` link. Now login, you can use your admin user/password, click on Packages, click on "Add New Package".
Enter the basename of the package you would like to store, for example the base name of `packrat_0.4-1_all.deb` is `packrat`.  Now click "Add File", enter the Provenance of the File and the Justificaion for the File and 
click "Select File", this will pop up a file selection dialog, select your package file and confirm you want to upload the file.  The select Submit.  If Packrat can not autodetect the distro that package belongs to, a dropdown
will apear and ask you to select the distro to apply the file to, if it does, select the distro and click submit again.  Now click on "Packages", then select you package base name, you should have your new file listed on the right.
click the Up Arrow to promote it to Ci, Dev, and the Stage, clicking the up arrow again will prompt you for a Change Controll number, enter the number and save, then click the up arrow again. It is now in the Production repo.  If
you click on the file drawer, it will set that file to the archive status.

On your packrat server, you should see the package file in /var/www/packrat/files.

You now need a Mirror entry for your packrat-agent to login with, in your url goto `http://< host or ip >/admin/` login with your admin user/pass, on the left click "+Add" by the Mirrors.  Give it a name, description, and a PSK
( ie a Pre Shared Key/Password) select from the Repo List which Repo Types and Release levels you would like to be sent to this mirror.

You are good to go, enjoy.

