export const EVENTS = {
  'FILE_ADDED': 'FILE_ADDED',
  'UPLOAD_COMPLETE': 'UPLOAD_COMPLETE',
  'UPLOAD_FAILED': 'UPLOAD_FAILED',
};

class FileService {
  constructor(url) {
    this._url = url;
    this._files = [];
    this._listeners = {};
  }

  register = (event, callback) => {
    if (!(event in this._listeners)) {
      this._listeners[event] = [];
    }

    this._listeners[event].push(callback);
  }

  _emit = (event, file) => {
    (this._listeners[event] || [])
      .forEach(callback => callback(event, file));
  }

  get files() {
    return JSON.parse(JSON.stringify(this._files));
  }

  _readAsDataURL = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.addEventListener('load', () => {
        resolve(reader.result);
      });

      reader.readAsDataURL(file);
    });
  };

  _upload = async (file) => {
    const formData = new FormData();

    formData.append('document', file);
    formData.append('uploadedOn', new Date(file.lastModified).toISOString());

    return fetch(this._url, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    })
      .then(async (resp) => {
        if (resp.ok) {
          return resp.json();
        } else {
          throw await resp.json();
        }
      });
  }

  process = async (file) => {
    const id = Math.random();
    const dataURL = await this._readAsDataURL(file);

    const fileObj = {
      id,
      dataURL,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      error: null,
    };

    this._files.push(fileObj);
    this._emit(EVENTS.FILE_ADDED, fileObj);

    this._upload(file)
      .then(data => {
        fileObj.status = 'complete';
        fileObj.url = data.URL;

        this._emit(EVENTS.UPLOAD_COMPLETE, fileObj);
      })
      .catch(err => {
        console.error(err);
        fileObj.status = 'error';
        fileObj.error = err;

        this._emit(EVENTS.UPLOAD_FAILED, fileObj);
      });
  }
};

export default FileService;
