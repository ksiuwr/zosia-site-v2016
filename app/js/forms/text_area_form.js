
import React from 'react';
import { form } from './forms';

const TextAreaForm = form("", (props) => {
  const onChange = e => {
    props.onChange(e.target.value);
  };

  return (
    <div className="input-field col s12">
      <textarea id={props.name} className="materialize-textarea" value={props.value} onChange={onChange}/>
      <label htmlFor={props.name}>{props.name}</label>
    </div>
  )
})

export default TextAreaForm;
