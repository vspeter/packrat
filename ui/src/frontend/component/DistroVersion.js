import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class DistroVersion extends React.Component
{
  state = {
      distroversion_list: [],
      distroversion: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { distroversion_list: [], distroversion: null } );
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
          this.setState( { distroversion: data } );
        } );
    }
    else
    {
      props.getList()
        .then( ( result ) =>
        {
          var distroversion_list = [];
          for ( var name in result.data )
          {
            var distroversion = result.data[ name ];
            name = CInP.extractIds( name )[0];
            distroversion_list.push( { name: name,
                              created: distroversion.created,
                              updated: distroversion.updated,
                            } );
          }

          this.setState( { distroversion_list: distroversion_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var distroversion = this.state.distroversion;
      return (
        <div>
          <h3>DistroVersion Detail</h3>
          { distroversion !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ distroversion.name }</td></tr>
                  <tr><th>Distro</th><td>{ distroversion.distro }</td></tr>
                  <tr><th>Version</th><td>{ distroversion.version }</td></tr>
                  <tr><th>File Type</th><td>{ distroversion.file_type }</td></tr>
                  <tr><th>Release Names</th><td>{ distroversion.release_names }</td></tr>
                  <tr><th>Created</th><td>{ distroversion.created }</td></tr>
                  <tr><th>Updated</th><td>{ distroversion.updated }</td></tr>
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
          <TableCell>Name</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.distroversion_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/distroversion/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default DistroVersion;
