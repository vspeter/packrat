var packratBuilder = {};
( function()
{
  "use strict";
  packratBuilder = function( cinp )
  {
    var packrat = { cinp: cinp };

    packrat.login = function( username, password )
    {
      var deferred = $.Deferred();

      $.when( cinp.call( '/api/v1/Auth(login)', { 'username': username, 'password': password } ) ).then(
        function( data )
        {
          deferred.resolve( data.result.value );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.logout = function( username, token )
    {
       cinp.call( '/api/v1/Auth(logout)', { 'username': username, 'token': token } );
    };

    packrat.getMirrors = function()
    {
      var deferred = $.Deferred();

      $.when( cinp.list( '/api/v1/Repos/Mirror' ) ).then(
        function( data )
        {
          $.when( cinp.getObjects( data.list, null, 100 ) ).then(
            function( data )
            {
              deferred.resolve( data );
            }
          ).fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.getRepos = function()
    {
      var deferred = $.Deferred();

      $.when( cinp.list( '/api/v1/Repos/Repo' ) ).then(
        function( data )
        {
          $.when( cinp.getObjects( data.list, null, 100 ) ).then(
            function( data )
            {
              deferred.resolve( data );
            }
          ).fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.getPackages = function()
    {
      var deferred = $.Deferred();

      $.when( cinp.list( '/api/v1/Repos/Package', null, null, 0, 200 ) ).then(
        function( data )
        {
          $.when( cinp.getObjects( data.list, null, 100 ) ).then(
            function( data )
            {
              deferred.resolve( data );
            }
          ).fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.createPackage = function( name )
    {
      var deferred = $.Deferred();

      $.when( cinp.create( '/api/v1/Repos/Package', { 'name': name } ) ).then(
        function( data )
        {
          deferred.resolve( data );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.getPackageFiles = function( package_uri )
    {
      var deferred = $.Deferred();

      $.when( cinp.list( '/api/v1/Repos/PackageFile', 'package', { 'package': package_uri }, 0, 500 ) ).then(
        function( data )
        {
          $.when( cinp.getObjects( data.list, null, 100 ) ).then(
            function( data )
            {
              deferred.resolve( data );
            }
          ).fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.promote = function( uri, to )
    {
      var deferred = $.Deferred();

      $.when( cinp.call( uri + '(promote)', { to: to } ) ).then(
        function( data )
        {
          $.when( cinp.get( uri ) ).then(
            function( data )
            {
              deferred.resolve( data );
            }
          ).fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.deprocate = function( uri )
    {
      var deferred = $.Deferred();

      $.when( cinp.call( uri + '(deprocate)' ) ).then(
        function( data )
        {
          $.when( cinp.get( uri ) ).then(
            function( data )
            {
              deferred.resolve( data );
            }
          ).fail(
            function( reason )
            {
              deferred.reject( reason );
            }
          );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    packrat.addPackageFile = function( provenance, justification, file_uri, distro_version )
    {
      var deferred = $.Deferred();

      if( !provenance.length ) // clear these out if blank.... that will force the server to send back that they are missing
        provenance = undefined;
      if( !justification.length )
        justification = undefined;
      if( !file_uri.length )
        file_uri = undefined;
      if( !distro_version.length )
        distro_version = undefined;

      $.when( cinp.call( '/api/v1/Repos/PackageFile(create)', { file: file_uri, justification: justification, provenance: provenance, version: distro_version } ) ).then(
        function( data )
        {
          deferred.resolve( data );
        }
      ).fail(
        function( reason )
        {
          deferred.reject( reason );
        }
      );

      return deferred.promise();
    };

    return packrat;
  };
} )();
