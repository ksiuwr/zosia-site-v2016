
import React from "react";

import {useModal} from "./modals";
import {Modal} from "./materialize_modal";

const AddRoomModal = props => {
  return (
    <Modal closeModal={props.closeModal}>
      <div className="modal-content">
        <h4>Add Room</h4>
        <div className="row">
          <div className="input-field col s12">
            <input id="name" type="text" className="validate"/>
            <label htmlFor="name">Name</label>
          </div>
          <div className="input-field col s12">
            <textarea id="description" className="materialize-textarea"/>
            <label htmlFor="descrtiption">Description</label>
          </div>
          <div className="input-field col s3">
            <input id="double_beds" type="number" min="0" className="validate"/>
            <label htmlFor="double_beds">Double Beds</label>
          </div>
          <div className="input-field col s3">
            <input id="single_beds" type="number" min="0" className="validate"/>
            <label htmlFor="single_beds">Single Beds</label>
          </div>
          <div className="input-field col s3">
            <input id="availble_double_beds" type="number" className="validate"/>
            <label htmlFor="availble_double_beds">Availble Double Beds</label>
          </div>
          <div className="input-field col s3">
            <input id="availble_single_beds" type="number" min="0" className="validate"/>
            <label htmlFor="availble_single_beds">Availble Single Beds</label>
          </div>
          <div className="col s12">
            <p>
              <label>
                <input type="checkbox" />
                <span>Hidden</span>
              </label>
            </p>
          </div>
        </div>
      </div>
      <div className="modal-footer">
        <a href="#!" className="modal-close waves-effect waves-green btn-flat" onClick={()=> console.log("XDD")}>
          Add
        </a>
      </div>
    </Modal>
  );
}

const SearchBar = (props) =>
{
  React.useEffect(() => {
    const elems = document.querySelectorAll('#sorting');
    const instances = M.FormSelect.init(elems, {})
  }, []);

  const [openModal, closeModal] = useModal()
  
  return (
    <div className="col s12">
      <ul style={{height: "50px", lineHeight: "45px"}}>
        <li style={{float: "left", margin: "5px", marginTop: "12px"}}>
            <i className="material-icons black-text">search</i>
        </li>
        <li style={{float: "left", margin: "5px"}}>
          <input type="text" placeholder="search" onChange={props.onSearch}/>
        </li>
        <li className="hide-on-med-and-down"style={{float: "left", margin: "5px"}}>
          <label>
            <input type="checkbox" onChange={props.onShowFullRoomsToggle} defaultChecked={true}/>
            <span> Show full rooms </span>
          </label>
        </li>
        <li className="hide-on-med-and-down" style={{float:"left", margin: "5px"}}>
          <a href="#" className="waves-effect waves-light btn" onClick={() => openModal(AddRoomModal, {closeModal})}> Add room </a>
        </li>
        <li className="hide-on-small-only" style={{float: "right", margin: "5px"}}>
          <select id="sorting" onChange={props.onSortingStrategyChange}>
            <option value="1">Sort by room numbers</option>
            <option value="2">Sort by fullness</option>
          </select>
        </li>
      </ul>
    </div>
  )
}

export default SearchBar;
