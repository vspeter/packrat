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

  getRepoList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/Repo' );
  };

  getMirrorList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/Mirror' );
  };

  getRepo = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Repo/Repo:' + id + ':' );
  };

  getMirror = ( id ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/Mirror:' + id + ':' );
  };

}

export default Packrat;
