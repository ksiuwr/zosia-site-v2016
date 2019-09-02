
import React from "react";
import styled from "styled-components";

import { delete_room, join_room } from "./zosia_api";

const roomCapacity = beds => beds.single + beds.double * 2

const Members = ({beds, members}) => {
  const room_size = roomCapacity(beds);
  const people_in_room = members.length
  const free_capacity = room_size - people_in_room
  const tenants = [];
  React.useEffect(() => {
    var elems = document.querySelectorAll('.tooltipped');
    var instances = M.Tooltip.init(elems, {});
  })
  for (let i = 0; i < people_in_room; i++)
  {
    tenants.push(<i className="material-icons" key={i}> person </i>);
  }

  for (let i = 0; i < free_capacity; i++)
  {
    tenants.push(<i className="material-icons" key={i + people_in_room}> person_outline </i>);
  }

  return (
    <a className="right">
      {tenants}
    </a>
  )
}

export const RoomCard = (props) => {
  const canEnter = () => roomCapacity(props.available_beds) > props.members.length
  const canUnlock = () => {
    const isLocked = props.lock != null;
    if (!isLocked)
      return false;
    const hasLockPackword = 'password' in props.lock
    return hasLockPackword;
  }
  const canLock = () => {
    const isNotLocked = props.lock != null;
    const isMyRoom = props.my_room == props.uri
    return isNotLocked && isMyRoom;
  }
  const canDelete = () => {
    return true;
  }
  const canEdit = () => {
    return true;
  }
  return (
    <div className="col s12 xl6">
      <div className="card">
        <div className="card-content">
            <span className="card-title grey-text text-darken-4"> {props.name} 
            <Members 
              beds={props.available_beds}
              members={props.members}
            />
            </span>
        </div>
        <div className="card-reveal">
          <span className="card-title grey-text text-darken-4">{props.name}<i className="material-icons right">close</i></span>
          <p> 
            Members: {props.members.length == 0 ? "-" : null} <br/>
            Description: {props.description}
          </p>
        </div>
        <div className="card-action">
          { canEnter() ? <a href="#" onClick={() => join_room(props.id, 1)}> enter </a> : '' }
          { canUnlock() ? <a href="#"> unlock </a> : '' }
          { canLock() ? <a href="#"> lock </a> : '' }
          { canDelete() ? <a href="#" onClick={() => delete_room(props.id) }> delete </a> : ''}
          { canEdit() ? <a href="#" onClick={() => console.log(props) }> edit </a> : <a href="#" onClick={showDetails}> Details </a>}
          <a href="javascript:void(0)" className="activator right" style={{"margin-right": 0}}> more </a>
        </div>
      </div>
    </div>
  )
}
