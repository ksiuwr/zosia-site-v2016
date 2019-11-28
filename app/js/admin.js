
import React from "react";
import ReactDOM from "react-dom";
import RoomsView from "./room";
import { ModalRoot, ModalProvider } from "./modals/modals";

const Rooms = () => (
  <ModalProvider>
    <ModalRoot />
    <RoomsView permissions={{
      canAddRoom: true,
      canDeleteRoom: true,
      canEditRoom: true,
    }}/>
  </ModalProvider>
)

ReactDOM.render(
  (<Rooms />),
  document.getElementById('rooms_tab')
);


