import React from 'react';
import { Dialog, Input, Button } from 'react-toolbox';

class TagDialog extends React.Component
{
  state = {
      active: false,
      disabled: false,
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

  tag = () => {
    this.props.packrat.tag( this.props.id, this.state.name ).then(
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
          title='Tag'
        >
        <Input type='text' label='Tag Name' name='name' value={ this.state.name } onChange={ this.handleChange.bind( this, 'name' ) } maxLength={ 10 } />
        <Button onClick={ this.tag }>Tag</Button>
        </Dialog>
        <Button disabled={ this.props.disabled } onClick={ this.show }>Tag</Button>
      </div>
);
  }
};

export default TagDialog;
