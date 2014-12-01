(function()
{
  var app = angular.module( 'gui', [ 'ui.bootstrap' ] );

  app.controller( 'DetailController', [ '$http', '$location', function( $http, $location )
  {
    this.menu_tab = 'mirror';
    this.mode = '';
    this.detail_uri = '';
    this.data = Object;{}
    this.trail_list_mode = [ 'Top' ];
    this.trail_list_uri = [ null ];

    this.select = function( mode, uri, trail_action )
    {
      if( trail_action === false )
      {
        this.trail_list_mode = [ 'Top', mode ];
        this.trail_list_uri = [ null, uri ];
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
        success( function( data, status, headers, config )
          {
            config.cntrl.data = data;
            if( mode == 'repo' )
            {
              $http.get( uri + 'packages/?format=json', { 'cntrl': config.cntrl } ).
              success( function( data, status, headers, config )
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

  app.controller( 'MirrorController', [ '$scope', '$http', function( $scope, $http )
  {
    $scope.mirror_list = [];

    $scope.load = function()
    {
      var url = '/api/v1/mirror/?format=json';
      $http.get( url, {} ).
        success( function( data )
        {
          $scope.mirror_list = data.objects;
          for ( var i = 0; i < $scope.mirror_list.length; i++ )
          {
            var repo_list = $scope.mirror_list[i].repo_list;
            $scope.mirror_list[i].repo_list = [];
            for ( var j = 0; j < repo_list.length; j++ )
            {
              $http.get( repo_list[j] + '?format=json', { 'mirror': $scope.mirror_list[i] } ).
                success( function( data, status, headers, config )
                  {
                    config.mirror.repo_list.push( data );
                  }
                );
            }
          }
        }
      );
    };

    $scope.load();

  } ] );

  app.controller( 'PackageController', [ '$scope', '$http', function( $scope, $http )
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
