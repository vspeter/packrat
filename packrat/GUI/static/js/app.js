(function()
{
  var app = angular.module( 'gui', [ 'ui.bootstrap' ] );

  app.controller( 'MenuController', [function()
  {
    this.mode = 'mirror';

    this.select = function( mode )
    {
      this.mode = mode;
    };

    this.isSelected = function( value )
    {
      return this.mode == value;
    };

  } ] );

  app.controller( 'DetailController', [ '$http', function( $http )
  {
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
        this.trail_list_mode.push( mode );
        this.trail_list_uri.push( uri );
      }
      else if( trail_action === 0 )
      {
        this.mode = '';
        this.detail_uri = '';
        this.trail_list_mode = [ 'Top' ];
        this.trail_list_uri = [ null ];
        return;
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
