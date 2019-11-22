
import React from "react";
import ReactDOM from "react-dom";
import RoomView from "./room";
import styled from "styled-components";
import { ModalRoot, ModalProvider } from "./modals/modals";
import RoomsView from "./room";

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
    <div id="blog" className="col s12">
      <ul className="collection">
        <a href="/blog/create" className="collection-item">Add blog post</a>
      </ul>
    </div>
  )
}

const Zosia = () => {
  return (
    <div id="zosia" className="col s12">
      <ul className="collection">
        <a href="/conferences/" className="collection-item">Conferences</a>
        <a href="/bus/" className="collection-item">Bus</a>
        <a href="/accounts/organizations/" className="collection-item">Organizations</a>
        <a href="/conferences/export_data/" className="collection-item"> Export data</a>
      </ul>
    </div>
  )
}

const Sponsors = () => {
  return (
    <div id="sponsors" className="col s12">
      <ul className="collection">
        <a href="/sponsors/" className="collection-item">Sponsors</a>
        <a href="/sponsors/create" className="collection-item">Add sponsor</a>
      </ul>
    </div>
  )
}

const QA = () => (
  <div id="qa" className="col s12">
    <ul className="collection">
      <a href="/questions/all/" className="collection-item">Q&A</a>
      <a href="/questions/add/" className="collection-item">Q&A add</a>
    </ul>
  </div>
)

const Lectures = () => (
  <div id="lectures" className="col s12">
    <ul className="collection">
      <a href="/lectures/all" className="collection-item">Lectures</a>
      <a href="/lectures/create" className="collection-item">Add lecture</a>
      <a href="/lectures/schedule/update/" className="collection-item">Update schedule</a>
    </ul>
  </div>
)

const Rooms = () => (
  <RoomsView permissions={{
    canAddRoom: true,
    canDeleteRoom: true,
    canEditRoom: true,
  }}/>
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
    "rooms": {
      component: Rooms,
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
                  className={view_id === current_view ? "active" : ""}
                  onClick={() => setView(view_id)}
                >
                  {views[view_id].name}
                </a>
              </li>)}
          </ul>
        </div>

      </div>
      <div className="row">
        <ModalProvider>
          <ModalRoot />
          <Component></Component>
        </ModalProvider>
      </div>
    </div>
  )
}

ReactDOM.render(
  (<AdminView />),
  document.getElementById('react-root')
);


