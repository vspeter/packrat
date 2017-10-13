import React from 'react';
import CInP from './cinp';
import AddPackageDialog from './AddPackageDialog';
import PackageFile from './PackageFile';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Package extends React.Component
{
  state = {
      package_list: [],
      package: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { package_list: [], package: null } );
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
          this.setState( { package: data } );
        } );
    }
    else
    {
      props.getList()
        .then( ( result ) =>
        {
          var package_list = [];
          for ( var name in result.data )
          {
            var package_ = result.data[ name ];
            name = CInP.extractIds( name )[0];
            package_list.push( { name: name,
                              created: package_.created,
                              updated: package_.updated,
                            } );
          }

          this.setState( { package_list: package_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var package_ = this.state.package;
      return (
        <div>
          <h3>Package Detail</h3>
          { package_ !== null &&
            <div>
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ package_.name }</td></tr>
                  <tr><th>Deprocated Count</th><td>{ package_.deprocated_count }</td></tr>
                  <tr><th>Created</th><td>{ package_.created }</td></tr>
                  <tr><th>Updated</th><td>{ package_.updated }</td></tr>
                </tbody>
              </table>
              <h3>Files</h3>
              <PackageFile package_id={ this.props.id } getList={ this.props.packrat.getPackageFileList } packrat={ this.props.packrat } />
            </div>
          }
        </div>
      );
    }

    return (
      <div>
        <AddPackageDialog packrat={ this.props.packrat } update={ () => { this.update( this.props ) } }/>
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell>Name</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableHead>
          { this.state.package_list.map( ( item ) => (
            <TableRow key={ item.name } >
              <TableCell><Link to={ '/package/' + item.name }>{ item.name }</Link></TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </Table>
      </div>
    );

  }
};

export default Package;
