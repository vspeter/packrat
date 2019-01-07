import CInP from './cinp';

class Packrat
{
  constructor( host )
  {
    this.cinp = new CInP( host );
  };

  login = ( username, password ) =>
  {
    return new Promise( ( resolve, reject ) =>
    {
      this.cinp.call( '/api/v2/Auth/User(login)', { 'username': username, 'password': password } ).then(
        ( response ) =>
        {
          this.cinp.setAuth( username, response.data );
          resolve();
        },
        ( error ) =>
        {
          reject( error );
        }
      ).catch( ( error ) =>
        {
          reject(  error );
        } );
    } );
  };

  logout = () =>
  {
    return new Promise( ( resolve, reject ) =>
    {
      this.cinp.call( '/api/v2/Auth/User(logout)', {} ).then(
        ( response ) =>
        {
          this.cinp.setAuth();
          resolve();
        },
        ( error ) =>
        {
          reject( error );
        }
      ).catch( ( error ) =>
        {
          reject(  error );
        } );
    } );
  };

  keepalive = () => {};

  getPackageList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v2/Package/Package' );
  };

  getPackageFileList = ( _package ) =>
  {
    return this.cinp.getFilteredObjects( '/api/v2/Package/PackageFile', 'package', { package: '/api/v2/Package/Package:' + _package + ':' } );
  };

  getRepoList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v2/Repo/Repo' );
  };

  getMirrorList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v2/Repo/Mirror' );
  };

  getDistroVersionList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v2/Attrib/DistroVersion' );
  };

  getTagList = () =>
  {
    return this.cinp.getFilteredObjects( '/api/v2/Attrib/Tag' );
  };

  getPackage = ( id ) =>
  {
    return this.cinp.get( '/api/v2/Package/Package:' + id + ':' );
  };

  getPackageFile = ( id ) =>
  {
    return this.cinp.get( '/api/v2/Package/PackageFile:' + id + ':' );
  };

  getRepo = ( id ) =>
  {
    return this.cinp.get( '/api/v2/Repo/Repo:' + id + ':' );
  };

  getMirror = ( id ) =>
  {
    return this.cinp.get( '/api/v2/Repo/Mirror:' + id + ':' );
  };

  getDistroVersion = ( id ) =>
  {
    return this.cinp.get( '/api/v2/Attrib/DistroVersion:' + id + ':' );
  };

  getTag = ( id ) =>
  {
    return this.cinp.get( '/api/v2/Attrib/Tag:' + id + ':' );
  };

  createPackage = ( name ) =>
  {
    return this.cinp.create( '/api/v2/Package/Package', { 'name': name } );
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
    return this.cinp.call( '/api/v2/Pakcage/PackageFile(distroversion_options)', { file: file_handle } );
  };

  createPackageFile = ( file_handle, justification, provenance, distroversion ) =>
  {
    return this.cinp.call( '/api/v2/Repo/PackageFile(create)', { file: file_handle, justification: justification, provenance: provenance, distroversion: distroversion } );
  };

  tag = ( id, tag_id, change_control_id ) =>
  {
    return this.cinp.call( '/api/v2/Package/PackageFile:' + id + ':(tag)', { tag: '/api/v2/Attrib/Tag:' + tag_id + ':', change_control_id: change_control_id } );
  };

  deprocate = ( id ) =>
  {
    return this.cinp.call( '/api/v2/Package/PackageFile:' + id + ':(deprocate)' );
  };

  fail = ( id ) =>
  {
    return this.cinp.call( '/api/v2/Package/PackageFile:' + id + ':(fail)' );
  };
}

export default Packrat;
