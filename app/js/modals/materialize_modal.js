
import React from 'react';

let id = 0;
let getId = () => {
    id = id + 1;
    return "modal" + id.toString();
}

const Modal = props => {
  const [id, setId] = React.useState(getId());
  const footer_is_fixed = props.fixed_footer || false;
  React.useEffect(() => {
    const elems = document.querySelectorAll('#' + id);
    const instances = M.Modal.init(elems, {
        onCloseEnd: () => { props.closeModal() }
    });
    instances[0].open();
  }, [])
  return (
    <div id={id} className={footer_is_fixed ? "modal modal-fixed-footer" : "modal"} key={id}>
        {props.children}
    </div>
  )
}

export default Modal;

