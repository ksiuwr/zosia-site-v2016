
import React from 'react';
import { form } from './forms';

const TextForm = form("", (props) => {
  const onChange = e => {
    props.onChange(e.target.value);
  };

  React.useEffect(() => {
    M.updateTextFields();
  }, []);

  return (
    <div className="input-field col s12">
      <input 
        id={props.name} type="text" className="validate" value={props.value} 
        onChange={onChange}
      />
      <label htmlFor={props.name}>{props.name}</label>
    </div>
  )
});

export default TextForm;
