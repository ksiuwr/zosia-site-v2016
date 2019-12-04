
import React from 'react';
import Modal from './materialize_modal';
import { useForm } from '../forms/forms';
import TextForm from '../forms/text_form';

const EnterLockedRoomModal = props => {
  const {submit, data} = props
  const [FormInput, formValue, setValue] = useForm(TextForm);
  
  return (
    <Modal closeModal={props.closeModal}>
      <div className="modal-content">
        <h4>Enter locked room {data.name}</h4>
        <div className="row">
          <FormInput name="Password" value={formValue} onChange={setValue}></FormInput>
        </div>
      </div>
      <div className="modal-footer">
        <a href="#!" className="modal-close waves-effect waves-green btn-flat" onClick={() => submit(formValue)}>
          Enter
        </a>
      </div>
    </Modal>
  );
}

export default EnterLockedRoomModal;
