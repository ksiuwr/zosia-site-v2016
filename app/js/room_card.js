
import React from "react";
import styled from "styled-components";

import { delete_room, join_room } from "./zosia_api";

const Wrapper = styled.div`
  &:after {
    content: "";
    display: table;
    clear: both;
  }
  padding: 15px;
`

const Action = styled.a`
  color: #ffab40;
  margin-right: 24px;
  -webkit-transition: color .3s ease;
  transition: color .3s ease;
  text-transform: uppercase;
`;

const roomCapacity = beds => beds.single + beds.double * 2

const Members = ({beds, members}) => {
  const room_size = roomCapacity(beds);
  const people_in_room = members.length
  const free_capacity = room_size - people_in_room
  const tenants = [];
  for (let i = 0; i < people_in_room; i++)
  {
    tenants.push(<i className="material-icons" key={i}> person </i>);
  }

  for (let i = 0; i < free_capacity; i++)
  {
    tenants.push(<i className="material-icons" key={i + people_in_room}> person_outline </i>);
  }

  return (
    <h5>
      {tenants}
    </h5>
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
    <div className="col s12 m6">
      <div className="card">
        <Wrapper> 
          <div className="col s2">
            <h5> {props.name} </h5>
          </div>
          <div className="col s10 right-align">
            <Members 
              beds={props.available_beds}
              members={props.members}
            />
          </div>
        </Wrapper>
        <div className="card-action">
          { canEnter() ? <a href="#" onClick={() => join_room(props.id, 1)}> enter </a> : '' }
          { canUnlock() ? <a href="#"> unlock </a> : '' }
          { canLock() ? <a href="#"> lock </a> : '' }
          { canDelete() ? <a href="#" onClick={() => delete_room(props.id) }> delete </a> : ''}
          { canEdit() ? <a href="#" onClick={() => console.log(props) }> edit </a> : <a href="#" onClick={showDetails}> Details </a>}
        </div>
      </div>
    </div>
  )
}
