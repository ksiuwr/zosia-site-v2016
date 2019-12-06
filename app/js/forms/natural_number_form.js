
import React from 'react';
import { form } from './forms';

const NaturalNumberForm = form(0, (props) => {
  const onChange = e => {
    props.onChange(e.target.value);
  }
  return (
    <div className="input-field col s3">
      <input id={props.name} type="number" min="0" className="validate" value={props.value} onChange={onChange}/>
      <label htmlFor={props.name}>{props.name}</label>
    </div>
  )
});

export default NaturalNumberForm;
