
import React from "react";
import styled from "styled-components";

import { exists, roomCapacity } from "./helpers";
import { useModal } from "./modals/modals";
import AddRoomModal from './modals/add_room_modal';


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

const MemberList = ({members, users}) => {
  return (
    <span>
      {members.map(member => {
        const first_name = member.user.first_name;
        const last_name = member.user.last_name;
        return first_name + " " + last_name;
      })}
    </span>
  )
}

export const RoomCard = (props) => {
  const {room_ops} = props
  const isMyRoom = () => {
    return exists(props.members, ({user}) => props.me.id == user.id);
  }
  const canEnter = () => !isMyRoom() && roomCapacity(props.available_beds) > props.members.length
  const canLeave = () => isMyRoom()
  const canUnlock = () => {
    const isLocked = props.lock != null;
    if (!isLocked)
      return false;
    const hasLockPackword = 'password' in props.lock
    return hasLockPackword;
  }
  const canLock = () => {
    const isNotLocked = props.lock == null;
    return isNotLocked && isMyRoom();
  }
  const canDelete = () => {
    return props.permissions.canDeleteRoom;
  }
  const canEdit = () => {
    return props.permissions.canEditRoom;
  }

  const [openModal, closeModal] = useModal()
  const openEditModal = () => 
    openModal(AddRoomModal, {
      data: props,
      closeModal,
      submit: data => room_ops.edit_room(props.id, data)
    }) 
  const lock = () => {
    room_ops.lock(props.id);
  }

  return (
    <div className="col s12 xl6">
      <div className={ isMyRoom() ? "card teal lighten-3" : "card" }>
        <div className="card-content">
            <span className="card-title grey-text text-darken-4"> {props.name} 
            <Members 
              beds={props.available_beds}
              members={props.members}
            />
            </span>
            <p> {canUnlock() ? "Password: " + props.lock.password : ""} </p>
        </div>
        <div className="card-reveal">
          <span className="card-title grey-text text-darken-4">{props.name}<i className="material-icons right">close</i></span>
          <p> 
            Members: {props.members.length == 0 ? "-" : <MemberList users={props.users} members={props.members}/> } <br/>
            Description: {props.description}
          </p>
        </div>
        <div className="card-action">
          { canEnter() ? <a href="#" onClick={() => room_ops.join(props.id)}> enter </a> : '' }
          { canLeave() ? <a href="#" onClick={() => room_ops.leave(props.id)}> leave </a> : '' }
          { canUnlock() ? <a href="#" onClick={() => room_ops.unlock(props.id)}> unlock </a> : '' }
          { canLock() ? <a href="#" onClick={lock}> lock </a> : '' }
          { canDelete() ? <a href="#" onClick={() => room_ops.delete(props.id) }> delete </a> : ''}
          { canEdit() ? <a href="#" onClick={openEditModal}> edit </a> : ""}
          <a href="javascript:void(0)" className="activator right" style={{"marginRight": 0}}> more </a>
        </div>
      </div>
    </div>
  )
}
