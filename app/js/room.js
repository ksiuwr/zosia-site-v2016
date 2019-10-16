// TODO:
// 6. Reduce request amount (return new data from join)
import React from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";

import useInterval from "./use_interval";
import { useModal, ModalProvider, ModalRoot } from "./modals/modals";
import { exists, map_of_arr } from "./helpers";
import { get_rooms, get_users, me, delete_room } from "./zosia_api";

import { RoomCard } from "./room_card";
import SearchBar from "./search_bar";

const RoomsView = (props) =>
{
  const [state, setState] = React.useState({
    users: [],
    rooms: [],
  });
  const [searchWords, setSearchWords] = React.useState([]);
  const [showFull, setShowFull] = React.useState(true);

  const refresh = () => {
    Promise.all([get_rooms(), get_users(), me.info()])
      .then(([rooms, users_arr, info]) => {
        const users = map_of_arr(users_arr, user => user.id);
        return { rooms, users, me: info}
      })
      .then(setState);
  }

  useInterval(refresh, 1000);

  const room_ops = {
    join: (room_id) => me.join_room(room_id).then(refresh),
    leave: (room_id) => me.leave_room(room_id).then(refresh),
    delete: (room_id) => delete_room(room_id).then(refresh)
  }

  const onSearch = event =>
  {
    if (event.target.value == "")
    {
      setSearchWords([]);
    }
    else
    {
      const words = event.target.value.split(" ");
      setSearchWords(words);
    }
  }

  const onShowFullRoomsToggle = event =>
  {
    setShowFull(!showFull);
  }

  const searchResults = state.rooms.filter(room => {
    if (searchWords.length == 0)
    {
      return true;
    }
    return exists(searchWords, word => room.name.toString().includes(word))
  })

  const filteredResults = searchResults.filter(room => {
    if (showFull)
    {
      return true;
    }
    else
    {
      return 
        room.available_beds.single + room.available_beds.double * 2 > 
        room.members.length;
    }
  })

  const sortedResults = filteredResults.sort((lhs, rhs) => {
    return lhs.room_number - rhs.room_number
  })
  
  return (
    <div>
      <SearchBar 
        permissions={props.permissions}
        onSearch={onSearch}
        onShowFullRoomsToggle={onShowFullRoomsToggle}
       />
      {sortedResults.map(data => {
        return (<RoomCard permissions={props.permissions} key={data.id} me={state.me} users={state.users} room_ops={room_ops} {...data}/>);
      })}
    </div>
  )
}

ReactDOM.render(
    (
    <ModalProvider>
      <ModalRoot/>
      <div className="container">
        <div className="row">
          <RoomsView permissions={{
            canAddRoom: false,
            canDeleteRoom: false,
            canEditRoom: false,
          }}/>
        </div>
      </div>
    </ModalProvider>
    ),
    document.getElementById('react-root')
);

export default RoomsView;
