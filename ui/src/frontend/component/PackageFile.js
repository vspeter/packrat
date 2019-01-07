import React from 'react';
import CInP from './cinp';
import TagDialog from './TagDialog';
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
                                     tags: pkgFile.tags,
                                     deprocated: ( pkgFile.deprocated_at == null ) ? '' : 'Deprocated',
                                     failed: ( pkgFile.failed_at == null ) ? '' : 'Failed',
                                     deprocated_at: pkgFile.deprocated_at,
                                     failed_at: pkgFile.failed_at,
                                     } );
          }
          this.setState( { packageFile_list: packageFile_list } );
        } );
    }
  }

  deprocate = ( id ) =>
  {
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

  fail = ( id ) =>
  {
    this.props.packrat.fail( id ).
    then( ( data ) =>
    {
      this.update( this.props );
    },
    ( err ) =>
    {
      alert( 'Error Failing: ' + JSON.stringify( err ) );
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
              <TagDialog disabled={ packageFile.failed_at != null || packageFile.deprocated_at != null } id={ this.props.id } packrat={ this.props.packrat } update={ () => { this.update( this.props ) } }/>
              <Button disabled={ packageFile.failed_at != null || packageFile.deprocated_at != null } onClick={ () => this.deprocate( this.props.id ) }>Deprocate</Button>
              <Button disabled={ packageFile.failed_at != null || packageFile.deprocated_at != null } onClick={ () => this.fail( this.props.id ) }>Fail</Button>
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
                  <tr><th>Tags</th><td>{ packageFile.tags }</td></tr>
                  <tr><th>Tag List</th><td><ul>{ packageFile.tag_list.map( ( item, index ) => <li key={ index }><Link to={ '/tag/' + CInP.extractIds( item ) }>{ item }</Link></li> ) }</ul></td></tr>
                  <tr><th>Created By</th><td>{ packageFile.created_by }</td></tr>
                  <tr><th>Deprocated By</th><td>{ packageFile.deprocated_by }</td></tr>
                  <tr><th>Deprocated At</th><td>{ packageFile.deprocated_at }</td></tr>
                  <tr><th>Failed By</th><td>{ packageFile.failed_by }</td></tr>
                  <tr><th>Failed At</th><td>{ packageFile.failed_at }</td></tr>
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
            <TableCell>Tags</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Arch</TableCell>
            <TableCell>Flags</TableCell>
            <TableCell>Actions</TableCell>
          </TableHead>
          { this.state.packageFile_list.map( ( item ) => (
            <TableRow key={ item.id } >
              <TableCell><Link to={ '/packagefile/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.version }</TableCell>
              <TableCell>{ item.tags }</TableCell>
              <TableCell>{ item.type }</TableCell>
              <TableCell>{ item.arch }</TableCell>
              <TableCell>{ item.failed } { item.deprocated }</TableCell>
              <TableCell>
                <TagDialog disabled={ item.failed_at != null || item.deprocated_at != null } id={ item.id } packrat={ this.props.packrat } update={ () => { this.update( this.props ) } }/>
                <Button disabled={ item.failed_at != null || item.deprocated_at != null } onClick={ () => this.deprocate( item.id ) }>Deprocate</Button>
                <Button disabled={ item.failed_at != null || item.deprocated_at != null } onClick={ () => this.fail( item.id ) }>Fail</Button>
              </TableCell>
            </TableRow>
          ) ) }
        </Table>
    );
  }
};

export default PackageFile;
