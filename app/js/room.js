// TODO:
// 6. Reduce request amount (return new data from join)
import React from "react";
import ReactDOM from "react-dom";
import styled from "styled-components";
import { stringify } from "querystring";

const exists = (arr, f) =>
  arr.reduce((acc, el) => f(el) | acc, false)

const RoomsView = (props) =>
{
  const [rooms, setRooms] = React.useState(
    [
      {
        uri: "/rooms/2",
        name: "201",
        beds: {
          single: 4,
          double: 1,
          other: 1,
        },
        is_hidden: true,
        available_beds: {
          single: 4,
          double: 1,
          other: 0,
        },
        members: [],
        lock: {
          locked_by: {
            uri: "/users/2",
            fst_name: "Adam",
            lst_name: "Adamski",
          },
          locked_until: Date.now()
        },
        neighbours: []
      },
      {
        uri: "/rooms/1",
        name: "202",
        beds: {
          single: 4,
          double: 1,
          other: 1,
        },
        is_hidden: true,
        available_beds: {
          single: 4,
          double: 1,
          other: 0,
        },
        members: [
          {
            user: {
              uri: "/users/1",
              fst_name: "Jakub",
              lst_name: "Szczerbiński",
            },
            joined_at: Date.now(),
          }
        ],
        neighbours: []
      },
    ]
  )

  const [searchWords, setSearchWords] = React.useState([]);
  const [showFull, setShowFull] = React.useState(true);

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
    return exists(searchWords, word => room.room_number.toString().includes(word))
  })

  const filterResults = searchResults.filter(room => {
    if (showFull)
    {
      return true;
    }
    else
    {
      return room.room_size > room.people_in_room;
    }
  })

  const sortResults = filterResults.sort((lhs, rhs) => {
    return lhs.room_number - rhs.room_number
  })
  
  return (
    <div className="container">
    <div className="row">
      <SearchBar 
        onSearch={onSearch}
        onShowFullRoomsToggle={onShowFullRoomsToggle}
       />
      {sortResults.map(data => {
        return (<RoomCard my_room={'/rooms/1'} {...data}/>);
      })}
    </div>
    </div>
  )
}
const SearchBar = (props) =>
{
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
        <li className="hide-on-small-only" style={{float: "right", margin: "5px"}}>
          <select onChange={props.onSortingStrategyChange}>
            <option value="1">Sort by room numbers</option>
            <option value="2">Sort by fullness</option>
          </select>
        </li>
      </ul>
    </div>
  )
}

const OptionBar = (props) =>
{
  return (
    <div className="col s12">
      <div className="row" id="optionbar">
      </div>
    </div>
  )
}

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

const roomSizeOfBeds = beds => beds.single + beds.double * 2 + beds.other

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

const RoomCard = (props) => {
  const color = "blue-gray";
  console.log(props);
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
        { 'lock' in props && 'password' in props.lock ?
          <a href="#">Unlock </a> : '' }
        { !('lock' in props) && props.my_room == props.uri ?
          <a href="#"> lock </a> : '' }
        </div>
      </div>
    </div>
  )
}

const App = (props) => (
    <div className="container">
    <div className="row">
      <SearchBar/>
      <RoomCard
        room_number="101"
        room_size={6}
        people_in_room={2}
      />
      <RoomCard
        room_number="102"
        room_size={3}
        people_in_room={2}
      />
      <RoomCard
        room_number="103"
        room_size={2}
        people_in_room={0}
      />
      <RoomCard
        room_number="104"
        room_size={2}
        people_in_room={2}
      />
    </div>
    </div>
)

ReactDOM.render(
    (<RoomsView/>),
    document.getElementById('react-root')
);
