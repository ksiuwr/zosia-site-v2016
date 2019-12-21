
import React from 'react';
import Modal from './materialize_modal';
import { useForm } from '../forms/forms';
import RoomForm from '../forms/room_form';
import { get_users, get_users_room, join_room, leave_room } from '../zosia_api';
import { map_of_arr, map_obj_as_obj } from '../helpers';

const userTag = user => user.first_name + " " + user.last_name + " #" + user.id

const MemberChip = ({member, onRemove}) => {
  return (
    <div className="chip">
      {userTag(member.user)}
      <i onClick={onRemove} className="remove material-icons">close</i>
    </div>
  )
}

const Autocomplete = props => {
  React.useEffect(() => {
    const elem = document.getElementById(props.name);
    const instance = M.Autocomplete.init(elem, {
      data: props.data,
      onAutocomplete: opt => {
        if (props.onAutocomplete(opt))
          document.getElementById(props.name).value = "";
      }
    });
  }, []);

  React.useEffect(() => {
    const elem = document.getElementById(props.name);
    M.Autocomplete.getInstance(elem).updateData(props.data);
  }, [props.data]);

  return (
    <div className="input-field col s12">
      <input type="text" id={props.name} className="autocomplete"/>
      <label htmlFor={props.name}>Add member</label>
    </div>
  );
}

const MemberInput = props => {
  const [data, setData] = React.useState(null);
  React.useEffect(() => {
    Promise.all([get_users(), get_users_room()])
      .then(([users, users_room]) => {
        setData({
          users,
          users_room
        });
        
      })
    return;
  }, []);
  const [state, setState] = React.useState(
    {
      loading: false,
      members: props.members,
      error: ""
    }
  );

  const addUser = state => id => {
    setState({
      ...state,
      loading: true,
    })
    join_room(props.room_id, id)
      .then(room => {
        if (room.members)
          setState({
            ...state,
            loading: false,
            members: room.members
          })
        else
          setState({
            ...state,
            loading: false,
            error: room
          })
      }, ({status, json}) => {
          setState({
            ...state,
            loading: false,
            error: json
          })
      })
  }

  const removeUser = state => id => {
    setState({
      ...state,
      loading: true,
    })
    leave_room(props.room_id, id)
      .then(room => {
        if (room.members)
          setState({
            ...state,
            loading: false,
            members: room.members,
            error: "",
          })
        else
          setState({
            ...state,
            loading: false,
            error: room,
          })
      }, ({status, json}) => {
          setState({
            ...state,
            loading: false,
            error: json
          })
      })
  }

  if (data)
  {
    const autocomplete_data = map_obj_as_obj(
      map_of_arr(data.users, userTag),
      (user) => null);

    const onAutocomplete = opt => {
      const user = data.users.find(el => {
        return userTag(el) == opt;
      });
      if (user)
        addUser(state)(user.id);
      else
        console.error("Unable to find user", opt);
      return true;
    }

    return (
      <div
        className="row" 
        style={state.loading ? {
          pointerEvents: "none",
          opacity: "0.5"
        } : {}}
      >
        <div className="col s12">
          <h5> Members </h5>
          <div className="progress">
            <div className={state.loading ? "indeterminate" : ""}></div>
          </div>
        </div>
        <div className="col s12">
          <Autocomplete 
            name="MemberInput" 
            data={autocomplete_data}
            onAutocomplete={onAutocomplete}
          />
          <p> {state.error} </p>
        </div>
        <div className="col s12">
          {state.members.map(member => (
            <MemberChip key={member.user.id} member={member} onRemove={() => removeUser(state)(member.user.id)}/>
          ))}
        </div>
      </div>
    );
  }
  else
    return <div style={{minHeight: '400px'}}> Loading user list. </div>
}

const RoomPropertiesModal = props => {
  const {submit, data, users} = props
  const [FormInput, formValue, setValue] = useForm(RoomForm, data);
  
  return (
    <Modal closeModal={props.closeModal}>
      <div className="modal-content">
        <h4>{data ? "Edit" : "Add"} Room</h4>
        <div className="row">
          <FormInput name="" value={formValue} onChange={setValue}></FormInput>
          {data ? <MemberInput users={users} members={data.members} room_id={data.id}/> : ""}
        </div>
      </div>
      <div className="modal-footer">
        <a href="#!" className="modal-close waves-effect waves-light btn" onClick={() => submit(formValue)}>
          Save
        </a>
      </div>
    </Modal>
  );
}

export default RoomPropertiesModal;
