
import React from 'react';

let id = 0;
let getId = () => {
    id = id + 1;
    return "modal" + id.toString();
}

export const Modal = props => {
  const [id, setId] = React.useState(getId());
  React.useEffect(() => {
    const elems = document.querySelectorAll('#' + id);
    const instances = M.Modal.init(elems, {
        onCloseEnd: () => { props.closeModal() }
    });
    instances[0].open();
  }, [])
  return (
    <div id={id} className="modal" key={id}>
        {props.children}
    </div>
  )
}

