import React from 'react';
import CInP from './cinp';
import TagMapDialog from './TagMapDialog';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Tag extends React.Component
{
  state = {
      tag_list: [],
      tag: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { tag_list: [], tag: null } );
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
          this.setState( { tag: data } );
        } );
    }
    else
    {
      props.getList()
        .then( ( result ) =>
        {
          var tag_list = [];
          for ( var name in result.data )
          {
            var tag = result.data[ name ];
            name = CInP.extractIds( name )[0];
            tag_list.push( { name: name,
                             created: tag.created,
                             updated: tag.updated,
                            } );
          }

          this.setState( { tag_list: tag_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var tag = this.state.tag;
      return (
        <div>
          <h3>Tag Detail</h3>
          { tag !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ tag.name }</td></tr>
                  <tr><th>Change Control Required</th><td>{ tag.change_control_required ? 'Yes' : 'No' }</td></tr>
                  <tr><th>Required Tags</th><td><ul>{ tag.required_list.map( ( item, index ) => <li key={ index }><Link to={ '/tag/' + CInP.extractIds( item ) }>{ item }</Link></li> ) }</ul></td></tr>
                  <tr><th>Created</th><td>{ tag.created }</td></tr>
                  <tr><th>Updated</th><td>{ tag.updated }</td></tr>
                </tbody>
              </table>
            </div>
          }
        </div>
      );
    }

    return (
      <div>
        <TagMapDialog packrat={ this.props.packrat } />
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell>Name</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableHead>
          { this.state.tag_list.map( ( item ) => (
            <TableRow key={ item.name } >
              <TableCell><Link to={ '/tag/' + item.name }>{ item.name }</Link></TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </Table>
      </div>
    );

  }
};

export default Tag;
