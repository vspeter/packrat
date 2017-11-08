import React from 'react';
import CInP from './cinp';
import AddPackageDialog from './AddPackageDialog';
import { Table, TableHead, TableRow, TableCell, Button } from 'react-toolbox';
import { Link } from 'react-router-dom';


class PackageFile extends React.Component
{
  state = {
    packageFile_list: [],
    packageFile: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { packageFile: null } );
    this.update( newProps );
  }

  update( props )
  {
    if( props.id !== undefined )
    {
      props.getDetail( props.id )
       .then( ( result ) =>
        {
          var data = result.data;
          this.setState( { packageFile: data } );
        } );
    }
    else
    {
      props.getList( props.package_id )
        .then( ( result ) =>
        {
          var packageFile_list = [];
          for( var id in result.data )
          {
            var pkgFile = result.data[ id ];
            packageFile_list.push( { id: CInP.extractIds( id ),
                                     version: pkgFile.version,
                                     type: pkgFile.type,
                                     arch: pkgFile.arch,
                                     release: pkgFile.release
                                     } );
          }
          this.setState( { packageFile_list: packageFile_list } );
        } );
    }
  }

  promote = ( id, cur_release ) =>
  {
    var rc;
    if( cur_release == 'new' )
    {
      rc = this.props.packrat.promote( id, 'dev' );
    }
    else if( cur_release == 'dev' )
    {
      rc = this.props.packrat.promote( id, 'stage' );
    }
    else if( cur_release == 'stage' )
    {
      var cc_id = window.prompt( 'Please enter the Change Control Number' );
      if( !cc_id )
        return;

      rc = this.props.packrat.promote( id, 'prod', cc_id );
    }
    else
    {
      return
    }
    rc.then(
      ( data ) =>
      {
        this.update( this.props );
      },
      ( err ) =>
      {
        alert( 'Error Promoting: ' + JSON.stringify( err ) );
      }
    )
  }

  deprocate = ( id, cur_release ) =>
  {
    if( cur_release == 'depr' )
    {
      return;
    }

    this.props.packrat.deprocate( id ).
    then( ( data ) =>
    {
      this.update( this.props );
    },
    ( err ) =>
    {
      alert( 'Error Deprocating: ' + JSON.stringify( err ) );
    }
   );
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var packageFile = this.state.packageFile;
      return (
        <div>
          <h3>PackageFile Detail</h3>
          { packageFile !== null &&
            <div>
              <Button onClick={ () => this.promote( this.props.id, this.state.packageFile.release ) }>Promote</Button>
              <Button onClick={ () => this.deprocate( this.props.id, this.state.packageFile.release ) }>Deprocate</Button>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Package</th><td><Link to={ '/package/' + CInP.extractIds( packageFile.package ) }>{ packageFile.package }</Link></td></tr>
                  <tr><th>Distro Version</th><td><Link to={ '/distroversion/' + CInP.extractIds( packageFile.distroversion ) }>{ packageFile.distroversion }</Link></td></tr>
                  <tr><th>Version</th><td>{ packageFile.version }</td></tr>
                  <tr><th>Type</th><td>{ packageFile.type }</td></tr>
                  <tr><th>Arch</th><td>{ packageFile.arch }</td></tr>
                  <tr><th>Justification</th><td>{ packageFile.justification }</td></tr>
                  <tr><th>Provenance</th><td>{ packageFile.provenance }</td></tr>
                  <tr><th>file</th><td><a href={ packageFile.file }>{ packageFile.file }</a></td></tr>
                  <tr><th>SHA256</th><td>{ packageFile.sha256 }</td></tr>
                  <tr><th>Release Type</th><td><ul>{ packageFile.release_type_list.map( ( item, index ) => <li key={ index }><Link to={ '/releasetype/' + CInP.extractIds( item ) }>{ item }</Link></li> ) }</ul></td></tr>
                  <tr><th>Release</th><td>{ packageFile.release }</td></tr>
                  <tr><th>Created</th><td>{ packageFile.created }</td></tr>
                  <tr><th>Updated</th><td>{ packageFile.updated }</td></tr>
                </tbody>
              </table>
            </div>
          }
        </div>
      );
    }

    return (
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell>Id</TableCell>
            <TableCell>Version</TableCell>
            <TableCell>Release</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Arch</TableCell>
            <TableCell>Actions</TableCell>
          </TableHead>
          { this.state.packageFile_list.map( ( item ) => (
            <TableRow key={ item.id } >
              <TableCell><Link to={ '/packagefile/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.version }</TableCell>
              <TableCell>{ item.release }</TableCell>
              <TableCell>{ item.type }</TableCell>
              <TableCell>{ item.arch }</TableCell>
              <TableCell><Button onClick={ () => this.promote( item.id, item.release ) }>Promote</Button><Button onClick={ () => this.deprocate( item.id, item.release ) }>Deprocate</Button></TableCell>
            </TableRow>
          ) ) }
        </Table>
    );
  }
};

export default PackageFile;
