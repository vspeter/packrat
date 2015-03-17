(function()
{
  "use strict";
  var app = angular.module( 'gui', [ 'ui.bootstrap', 'cinp.service' ] );

  app.controller( 'DetailController', [ 'cinp', '$location', '$modal', '$rootScope', function( cinp, $location, $modal, $rootScope )
  {
    this.menu_tab = 'mirror';
    this.mode = '';
    this.detail_uri = '';
    this.data = Object;{}
    this.trail_list_mode = [ 'Top' ];
    this.trail_list_id = [ null ];
    this.progress = 0;

    cinp.setHost( '' );

    this.serverErrorHandler = function( msg, stack_trace )
    {
      var modalInstance = $modal.open({
        templateUrl: 'servererror_template',
        controller: 'ServerErrorCtrl',
        size: 'lg',
        resolve: { msg: function(){ return msg; }, stack_trace: function(){ return stack_trace; } }
      });
    };

    cinp.on_server_error = this.serverErrorHandler;

    $rootScope.$on( 'progress',
      function( event, descr, progress )
      {
        this.status_descr = descr;
        this.status_progress = progress;
      }
    );

    this.select = function( mode, uri, trail_action )
    {
      if( trail_action === false )
      {
        this.trail_list_mode = [ 'Top', mode ];
        this.trail_list_id = [ null, uri ];
      }
      else if( trail_action === true )
      {
        var index = this.trail_list_uri.indexOf( uri );
        if( index != -1 )
        {
          mode = this.trail_list_mode[ index ];
          uri = this.trail_list_uri[ index ];
          this.trail_list_mode = this.trail_list_mode.slice( 0, ( index + 1 ) );
          this.trail_list_uri = this.trail_list_uri.slice( 0, ( index + 1 ) );
        }
        else
        {
          this.trail_list_mode.push( mode );
          this.trail_list_uri.push( uri );
        }
      }
      else if( trail_action === 0 )
      {
        this.mode = '';
        this.detail_uri = '';
        this.trail_list_mode = [ 'Top' ];
        this.trail_list_uri = [ null ];
      }
      else if( ( typeof trail_action === 'number' ) && ( trail_action % 1 === 0 ) && ( trail_action >= 1 ) && ( trail_action < this.trail_list_mode.length ) )
      {
        mode = this.trail_list_mode[ trail_action ];
        uri = this.trail_list_uri[ trail_action ];
        this.trail_list_mode = this.trail_list_mode.slice( 0, ( trail_action + 1 ) );
        this.trail_list_uri = this.trail_list_uri.slice( 0, ( trail_action + 1 ) );
      }
      else // confused, just ignore
        return;

      $location.search( 'mode', btoa( JSON.stringify( this.trail_list_mode ) ) );
      $location.search( 'uri', btoa( JSON.stringify( this.trail_list_uri ) ) );
      $location.replace();

      if( !mode )
      {
        return;
      }

      this.mode = 'loading';
      this.detail_uri = uri;

      $http.get( uri + '?format=json', { 'cntrl': this } ).
        success(
          function( data, status, headers, config )
          {
            config.cntrl.data = data;
            if( mode == 'repo' )
            {
              $http.get( uri + 'packages/?format=json', { 'cntrl': config.cntrl } ).
              success(
                function( data, status, headers, config )
                {
                  config.cntrl.data.package_list = data.objects;
                }
              );
            }
            config.cntrl.mode = mode;
          }
        );
    };

    this.isSelected = function( value )
    {
      return this.mode == value;
    };

    this.isDetailSelected = function( value )
    {
      return this.detail_uri == value;
    };

    this.menuSelect = function( mode )
    {
      this.menu_tab = mode;
    };

    this.isMenuSelected = function( value )
    {
      return this.menu_tab == value;
    };

    var search = $location.search();

    if( search.mode && search.uri )
    {
      this.trail_list_mode = JSON.parse( atob( search.mode ) );
      this.trail_list_uri = JSON.parse( atob( search.uri ) );
      this.select( null, null, ( this.trail_list_uri.length - 1 ) );
    }

  } ] );

  app.controller( 'ServerErrorCtrl',
  function( $scope, $modalInstance, msg, stack_trace )
  {
    if( msg === '' )
    {
      $scope.msg = 'Server Error';
      $scope.other_dump = stack_trace;
    }
    else
    {
      $scope.msg = msg;
      $scope.stack_trace = stack_trace;
    }

    $scope.ok = function()
    {
      $modalInstance.close();
    };
  } );

  app.filter( 'toTrusted', [ '$sce',
  function( $sce )
  {
    return function( text )
    {
      return $sce.trustAsHtml( text );
    };
  } ] );

  app.controller( 'MirrorController', [ '$scope', 'cinp', '$rootScope',
  function( $scope, cinp, $rootScope )
  {
    $scope.mirror_list = [];
    $scope.repo_map = {};

    $scope.load = function()
    {
      cinp.list( '/api/v1/Repos/Mirror', '', {}, 0, 100 ).then(
        function( data )
        {
          cinp.getObjects( data.list, null, 100 ).
          then(
            function( objects )
            {
              var uri_list = [];
              $rootScope.$broadcast( 'progress', null );
              for( var key in objects )
                $scope.mirror_list.push( objects[ key ] );
              for( var i = 0; i < $scope.mirror_list.length; i++ )
              {
                for( var j = 0; j < $scope.mirror_list[ i ].repo_list.length; j++ )
                {
                  if( uri_list.indexOf( $scope.mirror_list[ i ].repo_list[ j ] ) == -1 )
                    uri_list.push( $scope.mirror_list[ i ].repo_list[ j ] );
                }
                $scope.mirror_list[ i ].repo_list = cinp.extractIds( $scope.mirror_list[ i ].repo_list );
              }
              cinp.getObjects( uri_list, null, 100 ).
              then(
                function( objects )
                {
                  $scope.repo_map = objects;
                },
                function( error )
                {
                  alert( "Error" + error );
                },
                function( progress )
                {
                  $rootScope.$broadcast( 'progress', 'Repo List', progress );
                }
              );
            },
            function( error )
            {
              alert( "Error" + error );
            },
            function( progress )
            {
              $rootScope.$broadcast( 'progress', 'Mirror List', progress );
            }
          );
        }.bind( this )
      );
    };

    $scope.load();

  } ] );

  app.controller( 'PackageController', [ '$scope', '$http',
  function( $scope, $http )
  {
    $scope.package_list = [];

    $scope.load = function()
    {
      var url = '/api/v1/package/?format=json';
      $http.get( url, {} ).
        success( function( data )
          {
            $scope.package_list = data.objects;
          }
        );
    };

    $scope.load();

  } ] );
}
)();
