import React from 'react';
import PropTypes from 'prop-types';

import { readAsDataURL } from './read-as-data-url';

import './styles.scss';


class FileUpload extends React.Component {

  static propTypes = {
    url: PropTypes.string.isRequired,
  };

  state = {
    dragging: false,
    files: [],
  };
  files = [];

  handleDragEnter = (event) => {
    event.preventDefault();
    event.stopPropagation();

    this.setState({ dragging: true });
  };

  handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();

    this.setState({ dragging: true });
  };

  handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();

    this.setState({ dragging: false });
  };

  handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    this.setState({ dragging: false });

    const dt = event.dataTransfer;
    const files = dt.files;

    [...files].forEach(async (file) => {
      const id = Math.random();
      const dataURL = await readAsDataURL(file);

      const fileObj = {
        id,
        dataURL,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading',
        error: null,
      };

      this.files.push(fileObj);

      this.setState({
        files: JSON.parse(JSON.stringify(this.files)),
      });

      const formData = new FormData();

      formData.append('document', file);

      fetch(this.props.url, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      })
        .then(resp => resp.json())
        .then(data => {
          fileObj.status = 'complete';
          fileObj.url = data.URL;

          this.setState({
            files: JSON.parse(JSON.stringify(this.files)),
          });
        })
        .catch(err => {
          console.error(err);
          fileObj.status = 'error';
          fileObj.error = `${err}`;

          this.setState({
            files: JSON.parse(JSON.stringify(this.files)),
          });
        });
    });
  }

  render() {
    const dropZoneClasses = [
      (this.state.dragging) ? 'bg-primary' : 'bg-info',
      'text-white',
      'text-center',
      'p-5',
      'rounded',
    ];

    return (
      <div className="file-uploader">

        <div
          className={dropZoneClasses.join(' ')}
          onDragEnter={this.handleDragEnter}
          onDragOver={this.handleDragOver}
          onDragLeave={this.handleDragLeave}
          onDrop={this.handleDrop}
        >
          <div className="h3 mb-0">Drag files here.</div>
        </div>

        {this.state.files.map(file => (
          <div className="row m-3" key={file.id}>
            <div className="col-2">
              <img src={file.dataURL} className="mr-3" alt={file.name} style={{maxWidth: '100%'}} />
            </div>
            <div className="col">
              <h5 className="mt-0">{file.name}</h5>
              {file.status === 'uploading' ? (
                <p>Uploading...</p>
              ) : ''}
              {file.status === 'complete' ? (
                <p><a href={file.url}>Complete</a></p>
              ) : ''}
              {file.status === 'error' ? (
                <div className="alert alert-danger" role="alert">
                  {file.error}
                </div>
              ) : ''}
            </div>
          </div>
        ))}

      </div>
    );
  }
};

export default FileUpload;
