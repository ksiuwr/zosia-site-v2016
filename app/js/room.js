// TODO:
// 6. Reduce request amount (return new data from join)
import React from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";

import useInterval from "./use_interval";
import { useModal, ModalProvider, ModalRoot } from "./modals/modals";
import { exists, map_of_arr, roomCapacity, roomFullness } from "./helpers";
import { get_rooms, get_users, me, delete_room, edit_room } from "./zosia_api";

import { RoomCard } from "./room_card";
import SearchBar from "./search_bar";

const RoomsView = (props) =>
{
  const [state, setState] = React.useState({
    rooms: [],
  });
  const [searchWords, setSearchWords] = React.useState([]);
  const [showFull, setShowFull] = React.useState(true);
  const [sortingStrategy, setSortingStrategy] = React.useState("room_number");

  const refresh = () => {
    Promise.all([get_rooms(), me.info()])
      .then(([rooms, info]) => {
        return { rooms, me: info}
      })
      .then(setState);
  }

  const refresh_and_pass_arg = (arg) => {
    refresh();
    return arg;
  }

  useInterval(refresh, 60 * 1000);

  const room_ops = {
    join: (room_id) => me.join_room(room_id).then(refresh_and_pass_arg),
    leave: (room_id) => me.leave_room(room_id).then(refresh_and_pass_arg),
    delete: (room_id) => delete_room(room_id).then(refresh_and_pass_arg),
    lock: (room_id) => me.lock_room(room_id).then(refresh_and_pass_arg),
    unlock: (room_id) => me.unlock_room(room_id).then(refresh_and_pass_arg),
    edit_room: (room_id, data) => edit_room(room_id, data).then(refresh_and_pass_arg),
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

  const onSortingStrategyChange = event => {
    setSortingStrategy(event.target.value);
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
      return room.available_beds.single + room.available_beds.double * 2 > 
        room.members.length;
    }
  })

  const sortedResults = filteredResults.sort((lhs, rhs) => {
    if (sortingStrategy == "room_number")
    {
      const l_num = parseInt(lhs.name);
      const r_num = parseInt(rhs.name);

      if (l_num != NaN && r_num != NaN)
      {
        if (l_num > r_num)
          return 1;
        if (l_num < r_num)
          return -1;
      }
      
      if (lhs.name > rhs.name)
        return 1;
      
      if (lhs.name < rhs.name)
        return -1;
    }

    if (sortingStrategy == "fullness")
    {
      const f_rhs = roomFullness(rhs);
      const f_lhs = roomFullness(lhs);
      if (f_lhs > f_rhs)
        return 1
      if (f_lhs < f_rhs)
        return -1
    }
    // Fallback sorting
    return lhs.id - rhs.id
  })
  
  return (
    <div>
      <SearchBar 
        permissions={props.permissions}
        onSearch={onSearch}
        onShowFullRoomsToggle={onShowFullRoomsToggle}
        onSortingStrategyChange={onSortingStrategyChange}
       />
      {sortedResults.map(data => {
        return (
          <RoomCard 
            permissions={props.permissions}
            key={data.id} me={state.me} 
            room_ops={room_ops} 
            {...data}/>);
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
    document.getElementById('rooms_tab')
);

export default RoomsView;
