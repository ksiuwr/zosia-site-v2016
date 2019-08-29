
import React from "react";
import styled from "styled-components";

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

const roomSizeOfBeds = beds => beds == null ? 0 : beds.single + beds.double * 2 + beds.other

const Members = ({beds, members}) => {
  const room_size = roomSizeOfBeds(beds);
  const people_in_room = members.length
  const free_places = room_size - people_in_room
  const tenants = [];
  for (let i = 0; i < people_in_room; i++)
  {
    tenants.push(<i className="material-icons"> person </i>);
  }

  for (let i = 0; i < free_places; i++)
  {
    tenants.push(<i className="material-icons"> person_outline </i>);
  }

  return (
    <h5>
      {tenants}
    </h5>
  )
}

export const RoomCard = (props) => {
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
          <a href="#">Enter </a>
        { props.lock != null && 'password' in props.lock ?
          <a href="#">Unlock </a> : '' }
        { !('lock' in props) && props.my_room == props.uri ?
          <a href="#"> lock </a> : '' }
        </div>
      </div>
    </div>
  )
}
