
import React from 'react';
import Modal from './materialize_modal';
import { useForm } from '../forms/forms';
import RoomForm from '../forms/room_form';
import { create_room } from '../zosia_api';

const AddRoomModal = props => {
  const [FormInput, formValue, setValue] = useForm(RoomForm);
  const submit = () => {
    create_room(formValue); 
  }
  
  return (
    <Modal closeModal={props.closeModal}>
      <div className="modal-content">
        <h4>Add Room</h4>
        <div className="row">
          <FormInput name="" value={formValue} onChange={setValue}></FormInput>
        </div>
      </div>
      <div className="modal-footer">
        <a href="#!" className="modal-close waves-effect waves-green btn-flat" onClick={submit}>
          Add
        </a>
      </div>
    </Modal>
  );
}

export default AddRoomModal;
