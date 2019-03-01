import React from 'react';
import { Dialog, Input, Button } from 'react-toolbox';

class LoginDialog extends React.Component
{
  state = {
      active: false,
      logged_in: false,
      username: '',
      password: ''
  };

  show = () =>
  {
    this.setState( { active: true } );
  };

  close = () =>
  {
    this.setState( { password: '', active: false } );
  };

  handleChange = ( name, value ) => {
    this.setState( { ...this.state, [name]: value } );
  };

  login = () => {
    this.props.packrat.login( this.state.username, this.state.password ).then(
      ( data ) =>
      {
        this.setState( { password: '', logged_in: true } );
        this.close();
      }, ( err ) =>
      {
        if( err.reason == 'Invalid Request' && err.detail == 'Invalid Login' )
        {
          alert( 'Invalid Username/Password' );
          this.setState( { password: '' } );
        }
        else
        {
          this.props.packrat.cinp.server_error_handler( 'Error with Login', JSON.stringify( err ) );
        }
      }
    )
  }

  logout = () => {
    this.props.packrat.logout().then(
      ( data ) =>
      {
        this.setState( { username: '', password: '', logged_in: false } );
        this.close();
      }, ( err ) =>
      {
        this.props.packrat.cinp.server_error_handler( 'Error with Logout', JSON.stringify( err ) );
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
          title='Login'
        >
        <Input type='text' label='Username' name='username' value={ this.state.username } onChange={ this.handleChange.bind( this, 'username' ) } maxLength={ 100 } />
        <Input type='password' label='Password' name='password' value={ this.state.password } onChange={ this.handleChange.bind( this, 'password' ) } maxLength={ 100 } />
        <Button onClick={ this.login }>Login</Button>
        </Dialog>
        { this.state.logged_in ? <Button onClick={ this.logout } raised>{ this.state.username } - Logout</Button> : <Button onClick={ this.show } raised>Login</Button> }
      </div>
);
  }
};

export default LoginDialog;
