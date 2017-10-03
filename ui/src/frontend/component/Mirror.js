import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Mirror extends React.Component
{
  state = {
      mirror_list: [],
      mirror: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { mirror_list: [], mirror: null } );
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
          this.setState( { mirror: data } );
        } );
    }
    else
    {
      props.getList()
        .then( ( result ) =>
        {
          var mirror_list = [];
          for ( var name in result.data )
          {
            var mirror = result.data[ name ];
            name = CInP.extractIds( name )[0];
            mirror_list.push( { name: name,
                              description: mirror.description,
                              created: mirror.created,
                              updated: mirror.updated,
                            } );
          }

          this.setState( { mirror_list: mirror_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var mirror = this.state.mirror;
      return (
        <div>
          <h3>Mirror Detail</h3>
          { mirror !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ mirror.name }</td></tr>
                  <tr><th>Description</th><td>{ mirror.description }</td></tr>
                  <tr><th>Created</th><td>{ mirror.created }</td></tr>
                  <tr><th>Updated</th><td>{ mirror.updated }</td></tr>
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
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.mirror_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/mirror/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.description }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Mirror;
