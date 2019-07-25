
import React from "react";

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

export default SearchBar;
