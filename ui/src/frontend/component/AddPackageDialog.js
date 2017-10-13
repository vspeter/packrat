import React from 'react';
import { Dialog, Input, Button } from 'react-toolbox';

class AddPackageDialog extends React.Component
{
  state = {
      active: false,
      name: ''
  };

  show = () =>
  {
    this.setState( { active: true } );
  };

  close = () =>
  {
    this.setState( { name: '', active: false } );
  };

  handleChange = ( name, value ) => {
    this.setState( { ...this.state, [name]: value } );
  };

  save = () => {
    this.props.packrat.createPackage( this.state.name, 10 ).then(
      ( data ) =>
      {
        alert( 'Package Created' );
        this.close();
        this.props.update();
      }, ( err ) =>
      {
        if( err.reason == 'Invalid Request' )
        {
          this.props.packrat.cinp.server_error_handler( 'Error Creating Package', JSON.stringify( err.detail ) );
        }
        else
        {
          this.props.packrat.cinp.server_error_handler( 'Error Creating Package', JSON.stringify( err ) );
        }
      }
    )
  }

  actions = [
    { label: "Close", onClick: this.close },
  ];

  render()
  {
    return (
      <div>
        <Dialog
          actions={ this.actions }
          active={ this.state.active }
          onEscKeyDown={ this.close }
          onOverlayClick={ this.close }
          title='Add Package'
        >
        <Input type='text' label='Name' name='name' value={ this.state.name } onChange={this.handleChange.bind(this, 'name')} maxLength={200} />
        <Button onClick={ this.save }>Create</Button>
        </Dialog>
        <Button onClick={ this.show }>Create Package</Button>
      </div>
);
  }
};

export default AddPackageDialog;
