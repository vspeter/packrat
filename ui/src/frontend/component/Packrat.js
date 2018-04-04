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

  getPackageFileList = ( _package ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v1/Repo/PackageFile', 'package', { package: '/api/v1/Repo/Package:' + _package + ':' } );
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

  getPackageFile = ( id ) =>
  {
    return this.cinp.get( '/api/v1/Repo/PackageFile:' + id + ':' );
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

  createPackage = ( name, deprocated_count ) =>
  {
    return this.cinp.create( '/api/v1/Repo/Package', { 'name': name, 'deprocated_count': deprocated_count } );
  };

  uploadFile = ( file ) =>
  {
    const request = {
      method: 'POST',
      headers: {
                 'Accept': 'application/json',
                 'Content-Type': 'application/octet-stream',
                 'Content-Length': file.size,
                 'Content-Disposition': 'inline: filename="' + file.name + '"'
               },
      body: file
                   };

    return new Promise( ( resolve, reject ) =>
    {
      fetch( this.cinp.host + '/api/upload', request ).then(
        ( response ) =>
        {
          if ( response.status != 202 )
          {
            reject( 'Error uploading: ' + response );
          }
          else
          {
            response.text()
              .then( ( data ) =>
              {
                if( data )
                {
                  resolve( JSON.parse( data ).uri );
                }
                else
                {
                  reject( 'Invalid Response' );
                }
              }, ( error ) => reject( 'Error uploading: ' + error ) );
          }
        },
        ( error ) =>
        {
          reject( 'Error uploading: ' + error );
        }
      ).catch( ( error ) =>
        {
          reject( 'Error uploading: ' + error );
        } );
    } );
  };

  distroversionOptions = ( file_handle ) =>
  {
    return this.cinp.call( '/api/v1/Repo/PackageFile(distroversion_options)', { file: file_handle } );
  };

  createPackageFile = ( file_handle, justification, provenance, distroversion ) =>
  {
    return this.cinp.call( '/api/v1/Repo/PackageFile(create)', { file: file_handle, justification: justification, provenance: provenance, distroversion: distroversion } );
  };

  promote = ( id, to, change_control_id ) =>
  {
    return this.cinp.call( '/api/v1/Repo/PackageFile:' + id + ':(promote)', { to: '/api/v1/Repo/ReleaseType:' + to + ':', change_control_id: change_control_id } );
  };

  deprocate = ( id ) =>
  {
    return this.cinp.call( '/api/v1/Repo/PackageFile:' + id + ':(deprocate)' );
  };

}

export default Packrat;
