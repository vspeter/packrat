import CInP from './cinp';

class Packrat
{
  constructor( host )
  {
    this.cinp = new CInP( host );
  };

  login = () =>
  {
    this.cinp.call( '/api/v1/User/Session(login)', { 'username': username, 'password': password } )
      .then(
        function( result )
        {
          resolve( result.data );
        },
        function( reason )
        {
          reject( reason );
        }
      );
  };

  logout = () => {};
  keepalive = () => {};

  getPackageList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/Package' );
  };

  getRepoList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/Repo' );
  };

  getMirrorList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/Mirror' );
  };

  getDistroVersionList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/DistroVersion' );
  };

  getReleaseTypeList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/ReleaseType' );
  };



  getPackage = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Repo/Package:' + id + ':' );
  };

  getRepo = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Repo/Repo:' + id + ':' );
  };

  getMirror = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Repo/Mirror:' + id + ':' );
  };

  getDistroVersion = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Repo/DistroVersion:' + id + ':' );
  };

  getReleaseType = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Repo/ReleaseType:' + id + ':' );
  };

  createPackage = ( name ) =>
  {
    var rc = this.cinp.create( '/api/v1/Repo/Package', { 'name': name } );
    alert( rc );
    return rc;
  }


}

export default Packrat;
