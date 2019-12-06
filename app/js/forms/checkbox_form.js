
import React from 'react';
import { form } from './forms';

const CheckboxForm = form(false, (props) => {
  const onChange = e => {
    props.onChange(e.target.checked);
  }
  return (
    <div className="col s12">
      <p>
        <label>
          <input type="checkbox" checked={props.value} onChange={onChange}/>
          <span>{props.name}</span>
        </label>
      </p>
    </div>
  )
});

export default CheckboxForm;
