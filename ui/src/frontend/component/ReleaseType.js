import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class ReleaseType extends React.Component
{
  state = {
      releasetype_list: [],
      releasetype: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { releasetype_list: [], releasetype: null } );
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
          this.setState( { releasetype: data } );
        } );
    }
    else
    {
      props.getList()
        .then( ( result ) =>
        {
          var releasetype_list = [];
          for ( var name in result.data )
          {
            var releasetype = result.data[ name ];
            name = CInP.extractIds( name )[0];
            releasetype_list.push( { name: name,
                              description: releasetype.description,
                              level: releasetype.level,
                              created: releasetype.created,
                              updated: releasetype.updated,
                            } );
          }

          this.setState( { releasetype_list: releasetype_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var releasetype = this.state.releasetype;
      return (
        <div>
          <h3>ReleaseType Detail</h3>
          { releasetype !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ releasetype.name }</td></tr>
                  <tr><th>Description</th><td>{ releasetype.description }</td></tr>
                  <tr><th>Level</th><td>{ releasetype.level }</td></tr>
                  <tr><th>Change Control Required</th><td>{ releasetype.change_control_required }</td></tr>
                  <tr><th>Created</th><td>{ releasetype.created }</td></tr>
                  <tr><th>Updated</th><td>{ releasetype.updated }</td></tr>
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
          <TableCell>Description</TableCell>
          <TableCell>Level</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.releasetype_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/releasetype/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.description }</TableCell>
            <TableCell>{ item.level }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default ReleaseType;
