import React from 'react';
import PropTypes from 'prop-types';


class Preview extends React.Component {

  static propTypes = {
    file: PropTypes.object.isRequired,
  };

  render() {
    const file = this.props.file;

    return (
      <div className="row m-3">
        <div className="col-2">
          <img src={file.dataURL} className="mr-3 preview" alt={file.name} />
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
              {file.error.message ? file.error.message : `${file.error}`}
            </div>
          ) : ''}
        </div>
      </div>
    );
  }
}

export default Preview;
