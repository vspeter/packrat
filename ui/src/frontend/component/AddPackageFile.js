import React from 'react';
import { Input, Button, BrowseButton, Chip, Avatar, Dropdown } from 'react-toolbox';

class AddPackageFile extends React.Component
{
  state = {
      package_file: '',
      justification: '',
      provenance: '',
      distro_version: '',
      distro_version_list: [],
      upload_handle: null,
      file_size: '',
      file_name: '',
      file: null,
      upload_disabled: false,
      save_disabled: true
  };

  handleChange = ( name, value ) =>
  {
    this.setState( { ...this.state, [ name ]: value } );
  };

  uploadChange = ( event ) =>
  {
    var file = event.target.files[0]
    this.setState( { file_size: file.size, file_name: file.name, file: file } );
  };

  versionChange = ( value ) =>
  {
    this.setState( { distro_version: value } )
  };

  upload = () =>
  {
    this.props.packrat.uploadFile( this.state.file ).then(
      ( data ) =>
      {
        this.setState( { upload_handle: data } );
        this.props.packrat.distroversionOptions( this.state.upload_handle ).then(
          ( data ) =>
          {
            var version_list = [];
            for ( var key in data.data )
            {
              version_list.push( { value: data.data[ key ], label: data.data[ key ] } );
            }
            this.setState( { distro_version_list: version_list, distro_version: data.data[0], upload_disabled: true, save_disabled: false } );
          },
          ( err ) =>
          {
            if( err.reason == 'Invalid Request' )
            {
              this.props.packrat.cinp.server_error_handler( 'Error Getting Distro Versions', JSON.stringify( err.detail ) );
            }
            else
            {
              this.props.packrat.cinp.server_error_handler( 'Error Getting Distro Versions', JSON.stringify( err ) );
            }
          }
        )
      },
      ( err ) =>
      {
        if( err.reason == 'Invalid Request' )
        {
          this.props.packrat.cinp.server_error_handler( 'Error Uploading File', JSON.stringify( err.detail ) );
        }
        else
        {
          this.props.packrat.cinp.server_error_handler( 'Error Uploading File', JSON.stringify( err ) );
        }
      }
    );
  };

  save = () =>
  {
    this.props.packrat.createPackageFile( this.state.upload_handle, this.state.justification, this.state.provenance, this.state.distro_version ).
    then( ( data ) =>
    {
      this.resetFields();
      alert( 'Package File Added' );
    },
    ( err ) =>
    {
      this.props.packrat.cinp.server_error_handler( 'Error Creating Package File', JSON.stringify( err ) );
    } );
  };

  resetFields = () =>
  {
    this.setState( {
          package_file: '',
          justification: '',
          provenance: '',
          distro_version: '',
          distro_version_list: [],
          upload_handle: null,
          file_size: '',
          file_name: '',
          file: null,
          upload_disabled: false,
          save_disabled: true
        } );
  };

  render()
  {
    return (
      <div>
        <BrowseButton icon="file_upload" label="Chose File" onChange={ this.uploadChange } disabled={ this.state.upload_disabled }/><br/>
        <Chip><Avatar style={{  backgroundColor: 'deepskyblue' }} icon="timelapse" />{ this.state.file_size }</Chip>
        <Chip><Avatar style={{  backgroundColor: 'deepskyblue' }} icon="folder" />{ this.state.file_name }</Chip><br/>
        <Button onClick={ this.upload } disabled={ this.state.upload_disabled }>Upload</Button>
        <Dropdown auto onChange={ this.versionChange } source={ this.state.distro_version_list } value={ this.state.distro_version } />
        <Input type='text' label='Provenance' name='provenance' value={ this.state.provenance } onChange={ this.handleChange.bind( this, 'provenance' ) } />
        <Input type='text' label='Justification' name='justification' value={ this.state.justification } onChange={ this.handleChange.bind( this, 'justification' ) } />
        <Button onClick={ this.save } disabled={ this.state.save_disabled }>Save</Button>
        <Button onClick={ this.resetFields }>Reset</Button>
      </div>
    );
  }
};

export default AddPackageFile
