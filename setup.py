#!/usr/bin/env python3

import glob
from distutils.core import setup
from distutils.command.build_py import build_py
from setuptools import find_packages
import os


class custom_build( build_py ):
    def run( self ):
      # build_py.run( self )
      # get .pys
      for package in self.packages:  # derived from build_py.run
        package_dir = self.get_package_dir(package)
        modules = self.find_package_modules(package, package_dir)
        for (package_, module, module_file) in modules:
          assert package == package_
          if os.path.basename( module_file ).endswith( '_test.py' ) or os.path.basename( module_file ) == 'tests.py':
            continue
          self.build_module(module, module_file, package)

      # get.htmls
      for src in glob.glob( 'packrat/templates/*/' ) + [ 'packrat/templates/' ]:
        src_dir = src[:-1]
        build_dir = '%s/%s' % ( self.build_lib, src_dir )
        for filename in glob.glob( '%s/*.html' % src_dir ):
          filename = os.path.basename( filename )
          target = os.path.join(build_dir, filename)
          self.mkpath(os.path.dirname(target))
          self.copy_file(os.path.join(src_dir, filename), target, preserve_mode=False)

      # other files
      for filename in []:
        src_dir = os.path.dirname( filename )
        build_dir = '%s/%s' % ( self.build_lib, src_dir )
        filename = os.path.basename( filename )
        target = os.path.join(build_dir, filename)
        self.mkpath(os.path.dirname(target))
        self.copy_file(os.path.join(src_dir, filename), target, preserve_mode=False)

      # other dirs
      for src in []:
        src_dir = src[:-1]
        build_dir = '%s/%s' % ( self.build_lib, src_dir )
        for filename in glob.glob( '%s/*' % src_dir ):
          filename = os.path.basename( filename )
          target = os.path.join(build_dir, filename)
          self.mkpath(os.path.dirname(target))
          self.copy_file(os.path.join(src_dir, filename), target, preserve_mode=False)


setup( name='packrat',
       description='Packrat',
       author='Peter Howe',
       author_email='peter.howe@emc.com',
       include_package_data=True,
       packages=find_packages(),
       cmdclass={ 'build_py': custom_build }
       )
