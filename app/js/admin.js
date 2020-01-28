
import React from "react";
import ReactDOM from "react-dom";
import RoomsView from "./room";
import { ModalRoot, ModalProvider } from "./modals/modals";

const Rooms = () => (
  <ModalProvider>
    <ModalRoot />
    <RoomsView isAdminView={true}/>
  </ModalProvider>
)

ReactDOM.render(
  (<Rooms />),
  document.getElementById('rooms_tab')
);


