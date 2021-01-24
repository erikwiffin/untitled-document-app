import React from 'react';
import ReactDOM from 'react-dom';
import FileUpload from './file-upload';

const targets = document.querySelectorAll('.file-upload').forEach(target => {
  const form = target.querySelector('form');
  ReactDOM.render(<FileUpload url={form.action} />, target);
});
