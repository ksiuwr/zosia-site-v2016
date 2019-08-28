
import React from "react";
import ReactDOM from "react-dom";
import RoomView from "./room";
import styled from "styled-components";

const Users = () => {
  return (
    <div id="users" className="col s12">
        <ul className="collection">
            <a href="/user_preferences/" className="collection-item">Preferences</a>
            <a href="/accounts/mail/" className="collection-item">Email users</a>
        </ul>
    </div>
  )
}

const Blog = () => {
  return (
    <div id="blog" class="col s12">
      <ul class="collection">
        <a href="/blog/create" class="collection-item">Add blog post</a>
      </ul>
    </div>
  )
}

const Zosia = () => {
  return (
    <div id="zosia" class="col s12">
      <ul class="collection">
        <a href="/conferences/" class="collection-item">Conferences</a>
        <a href="/bus/" class="collection-item">Bus</a>
        <a href="/accounts/organizations/" class="collection-item">Organizations</a>
        <a href="/conferences/export_data/" class="collection-item"> Export data</a>
      </ul>
    </div>
  )
}

const Sponsors = () => {
  return (
    <div id="sponsors" class="col s12">
      <ul class="collection">
          <a href="/sponsors/" class="collection-item">Sponsors</a>
          <a href="/sponsors/create" class="collection-item">Add sponsor</a>
      </ul>
    </div>
  )
}

const QA = () => (
  <div id="qa" class="col s12">
    <ul class="collection">
      <a href="/questions/all/" class="collection-item">Q&A</a>
      <a href="/questions/add/" class="collection-item">Q&A add</a>
    </ul>
  </div>
)

const Lectures = () => (
  <div id="lectures" class="col s12">
    <ul class="collection">
      <a href="/lectures/all" class="collection-item">Lectures</a>
      <a href="/lectures/create" class="collection-item">Add lecture</a>
      <a href="/lectures/schedule/update/" class="collection-item">Update schedule</a>
    </ul>
  </div>
)

const Rooms = () => (
  <div id="rooms" class="col s12">
    <ul class="collection">
      <a href="/rooms/report/" class="collection-item">Rooms</a>
      <a href="/rooms/import/" class="collection-item">Add room</a>
    </ul>
  </div>
)

const AdminView = props => {
  const [current_view, setView] = React.useState("rooms");
  const views = {
    "users": { 
      component: Users,
      name: "Users"
    },
    "zosia": {
      component: Zosia,
      name: "Zosia",
    },
    "blog": {
      component: Blog,
      name: "blog",
    },
    "sponsors": {
      component: Sponsors,
      name: "Sponsors",
    },
    "qa": {
      component: QA,
      name: "Q&A",
    },
    "schedule": {
      component: Lectures,
      name: "Schedule"
    },
    "rooms" : {
      component: RoomView,
      name: "Rooms"
    },
  }
  const Component = views[current_view].component;
  return (
    <div className="container">
        <h3>Admin panel</h3>

        <div className="row">
            <div className="col s12">
                <ul className="tabs">
                {Object.keys(views).map(view_id => 
                  <li className="tab col" key={view_id}>
                    <a 
                      href="#" 
                      className={view_id === current_view ? "active" : "" }
                      onClick={() => setView(view_id)}
                    >
                      {views[view_id].name}
                    </a>
                  </li>)}
                </ul>
            </div>

        </div>
        <div className="row">
            <Component></Component>

        </div>
    </div>
  )
}

ReactDOM.render(
    (<AdminView/>),
    document.getElementById('react-root')
);


