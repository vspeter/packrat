import React from 'react';
import { Dialog, Button } from 'react-toolbox';

class TagMapDialog extends React.Component
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
          title='Tag Map'
        >
        Nice looking Map here
        <Button onClick={ this.close }>Close</Button>
        </Dialog>
        <Button onClick={ this.show }>View Tag Map</Button>
      </div>
);
  }
};

export default TagMapDialog;
