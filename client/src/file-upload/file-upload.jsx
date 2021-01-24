import React from 'react';
import PropTypes from 'prop-types';

import FileService, { EVENTS } from './file-service';
import Preview from './preview';

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
  service = null;

  componentDidMount() {
    this.service = new FileService(this.props.url);
    this.service.register(EVENTS.FILE_ADDED, this.handleFileServiceEvents);
    this.service.register(EVENTS.UPLOAD_COMPLETE, this.handleFileServiceEvents);
    this.service.register(EVENTS.UPLOAD_FAILED, this.handleFileServiceEvents);
  }

  handleFileServiceEvents = (event, file) => {
    console.log(event, file);
    this.setState({ files: this.service.files });
  };

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

    [...files].forEach(this.service.process);
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
          <Preview key={file.id} file={file} />
        ))}

      </div>
    );
  }
};

export default FileUpload;
