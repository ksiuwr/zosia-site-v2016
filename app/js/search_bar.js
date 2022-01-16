
import React from "react";

import { useModal } from "./modals/modals";
import RoomPropertiesModal from './modals/room_properties_modal';
import { create_room } from "./zosia_api";
import { apiErrorToast, roomingSuccessToast } from "./toasts";
import { escapeHtml } from "./helpers";


const SearchBar = (props) =>
{
  React.useEffect(() => {
    const elems = document.querySelectorAll('#sorting');
    const instances = M.FormSelect.init(elems, {})
  }, []);

  const [openModal, closeModal] = useModal()

  const add_room = () =>
    openModal(RoomPropertiesModal, {
        closeModal,
        submit: data => create_room(data).then(
            roomingSuccessToast(room => "You've added room " + escapeHtml(room.name) + "."),
            apiErrorToast
        )
    })

  return (
    <div>
    { props.isAdminView ?
    <div className="col s12">
      <ul style={{height: "50px", lineHeight: "45px", margin: 0}}>
        <li style={{float:"left", margin: "5px"}}>
          <a href="#" className="waves-effect waves-light btn" onClick={add_room}> Add room </a>
        </li>
      </ul>
    </div> : "" }
    <div className="col s12">
      <ul style={{height: "50px", lineHeight: "45px", "marginTop": 0}}>
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
        <li className="hide-on-small-only" style={{float: "right", margin: "5px"}}>
          <select id="sorting" onChange={props.onSortingStrategyChange}>
            <option value="room_numbers">Sort by room numbers</option>
            <option value="fullness">Sort by fullness</option>
          </select>
        </li>
      </ul>
    </div>
    </div>
  )
}

export default SearchBar;
