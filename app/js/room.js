// TODO:
// 6. Reduce request amount (return new data from join)
import React from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";

import useInterval from "./use_interval";
import { useModal, ModalProvider, ModalRoot } from "./modals/modals";
import { exists } from "./helpers";
import { get_rooms } from "./zosia_api";

import { RoomCard } from "./room_card";
import SearchBar from "./search_bar";

const RoomsView = (props) =>
{
  const [rooms, setRooms] = React.useState([]);
  const [searchWords, setSearchWords] = React.useState([]);
  const [showFull, setShowFull] = React.useState(true);
  useInterval(() => {
    get_rooms().then(json => setRooms(json));
  }, 1000);


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

  const searchResults = rooms.filter(room => {
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
        onSearch={onSearch}
        onShowFullRoomsToggle={onShowFullRoomsToggle}
       />
      {sortedResults.map(data => {
        return (<RoomCard key={data.id} my_room={'/rooms/1'} {...data}/>);
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
          <RoomsView/>
        </div>
      </div>
    </ModalProvider>
    ),
    document.getElementById('react-root')
);

export default RoomsView;
