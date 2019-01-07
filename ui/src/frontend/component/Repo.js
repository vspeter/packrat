import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';

class Repo extends React.Component
{
  state = {
      repo_list: [],
      repo: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { repo_list: [], repo: null } );
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
          this.setState( { repo: data } );
        } );
    }
    else
    {
      props.getList()
        .then( ( result ) =>
        {
          var repo_list = [];
          for ( var name in result.data )
          {
            var repo = result.data[ name ];
            name = CInP.extractIds( name )[0];
            repo_list.push( { name: name,
                              description: repo.description,
                              created: repo.created,
                              updated: repo.updated,
                            } );
          }

          this.setState( { repo_list: repo_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var repo = this.state.repo;
      return (
        <div>
          <h3>Repo Detail</h3>
          { repo !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ repo.name }</td></tr>
                  <tr><th>Description</th><td>{ repo.description }</td></tr>
                  <tr><th>Fieldsystem Directory</th><td>{ repo.filesystem_dir }</td></tr>
                  <tr><th>Distro Versions</th><td><ul>{ repo.distroversion_list.map( ( item, index ) => <li key={ index }><Link to={ '/distroversion/' + CInP.extractIds( item ) }>{ item }</Link></li> ) }</ul></td></tr>
                  <tr><th>Manager Type</th><td>{ repo.manager_type }</td></tr>
                  <tr><th>Tag</th><td><Link to={ '/tag/' + CInP.extractIds( repo.tag ) }>{ repo.tag }</Link></td></tr>
                  <tr><th>Show Only the Latest</th><td>{ repo.show_only_latest }</td></tr>
                  <tr><th>Created</th><td>{ repo.created }</td></tr>
                  <tr><th>Updated</th><td>{ repo.updated }</td></tr>
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
        { this.state.repo_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/repo/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.description }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Repo
