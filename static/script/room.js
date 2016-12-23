// TODO:
// 5. Refresh button + interval + callback instead of page reload
// 6. Reduce request amount (return new data from join)
const Links = (props) => {
  let {globals, room, can_join} = props;
  let {inside, owns, is_locked, people} = room;
  let {can_room, join, join_password, join_unlock, try_unlock, show_people} = globals;
  let has_people = people && people.length > 0;
  let join_link = <a />;
  let show_people_link = <a />;
  if(can_room) {
    if(can_join) {
      if(is_locked) {
        join_link = <a href="#" onClick={join_password(room)}> Join </a>;
      } else {
        if(!inside) {
          if(has_people) {
            join_link = <a onClick={join_unlock(room)} href="#"> Join </a>;
          } else {
            join_link = <a onClick={join(room)} href="#"> Join </a>;
          }
        }
      }
    }
    if(owns) {
      if(is_locked) {
        join_link = <a href="#" onClick={try_unlock}> Unlock </a>;
      } else {
        join_link = <a />;
      }
    }
  }
  if(has_people) {
    show_people_link = <a href='#' onClick={show_people(room)}> Members</a>;
  }
  return (
      <div className="card-action">
        {join_link}
        {show_people_link}
      </div>
  );
};

const Card = ({room, globals}) => {
  let {inside, name, owns, free_places, description, capacity, is_locked, join} = room;
  let can_join = free_places > 0;
  let color = 'blue-grey';
  let status = <p>Free</p>;
  if(is_locked) {
    status = <p>Locked</p>;
    color = 'brown';
  }
  if(free_places < capacity) {
    status = <p>Occupied</p>;
  }
  if(!can_join) {
    status = <p>Cannot join</p>;
    color = 'grey';
  }
  if(inside) {
    status = <p>Your room</p>;
    color = 'teal';
  }
  if(owns) {
    color = 'green';
    status = <p>Password {owns}</p>;
  }
  return (
      <div className="col s6 m4">
      <div className={"card darken-2 " + color} >
          <div className="card-content white-text">
      <span className="card-title">Room {name}</span>
      <p>{description}</p>
      {status}
      <p> Places: {free_places || 0} / {capacity}</p>
          </div>
      <Links room={room} globals={globals} can_join={can_join}/>
        </div>
      </div>
  );
};

class MaterializeCSSModal extends React.Component {
  constructor(props) {
    super(props);
    let {close, children} = props;
    this.close = close;
    this.children = children;
  }

  componentDidMount() {
    let id = this.ref;
    $(id).modal({
      'complete': this.close
    });
    $(id).modal('open');
  }

  render() {
    return (
        <div className="modal" ref={(ref) => {this.ref = ref;}}>
          {this.children}
        </div>
    );
  };
}

const SimpleModal = () => {
  return (
    <div>
      <div className="modal-content">
      <h4>Modal Header</h4>
      <p>A bunch of text</p>
      </div>
      <div className="modal-footer">
      <a href="#!" className=" modal-action modal-close waves-effect waves-green btn-flat">Agree</a>
      </div>
    </div>
  );
};

const UnlockModal = ({unlock}) => {
  return (
      <div>
      <div className="modal-content">
      <h4>Unlock room</h4>
      <p>Unlocking room means anybody will be able to join.</p>
      <p> Are you sure?</p>
      </div>
      <div className="modal-footer">
      <a href="#!" onClick={unlock} className=" modal-action modal-close waves-effect waves-green btn-flat">Unlock</a>
      </div>
      </div>
  );
};

const PasswordModal = ({args, try_join}) => {
  let ref = null;
  let grab_input_and_try_join = () => {
    let prepared = try_join(args, {'password': ref.value});
    prepared();
  };
  return (
      <div>
      <div className="modal-content">
      <h4>Join room</h4>
      </div>
      <div className="modal-footer">
      <div>
      Password:
      <div className="input-field inline">
      <input ref={(input)=>{ref=input;}} id="password" type="password" className="validate" />
      <label htmlFor="password" data-error="wrong" data-success="right">Password</label>
      </div>
      </div>

      <a href="#!" onClick={grab_input_and_try_join} className=" modal-action modal-close waves-effect waves-green btn-flat">Join</a>
      </div>
      </div>
  );
};

const Man = ({name}) => {
  return <p>{name}</p>;
};

const MembersModal = ({args}) => {
  let {people, name} = args;
  let people_view = people.map(({name}, i) => { return <Man key={i} name={name} />;});
  return (
      <div className="modal-content">
      <h4>Members of room {name}</h4>
      {people_view}
      </div>
  );
};

class Main extends React.Component {
  constructor(props) {
    super(props);
    let {rooms, csrf, urls} = props;
    this.state = {
      rooms,
      csrf,
      urls
    };
  }

  sortRooms(rooms) {
    return _(rooms).sortBy(({id}) => { return id; });
  }

  refresh() {
    $.getJSON(this.state.urls.status, (data) => {
      data.rooms = this.sortRooms(data.rooms);
      this.setState(data);
    });
  }

  shouldComponentUpdate(nextProps, nextState) {
    if(window.DeepDiff) {
      let delta = DeepDiff.diff(this.state, nextState);
      if(delta) {
        log.debug('Change:');
        delta.map((ch)=> { log.debug(ch.path, ch.kind, ch.rhs);});
      }
    } else {
      log.debug('State:', this.state);
    };
    return true;
  }

  join_password(room) {
    return () => {
      this.setState({'modal': {'type': 'password', 'args': room }});
    };
  }

  join({join}, opts) {
    opts = opts || {};
    let {password, lock} = opts;
    return () => {
      log.debug('Joining', join, 'with', {password, lock});
      $.post(join, {'csrfmiddlewaretoken': this.state.csrf, password, lock}, (data) => {
        log.info('Room join', data);
        this.refresh();
      }).catch((err) => {
        log.error(err);
        Materialize.toast(err.responseJSON['status'], 4000, 'red darken-4');
      });
    };
  }

  unlock() {
    $.post(this.state.urls.unlock, {'csrfmiddlewaretoken': this.state.csrf}, (data) => {
      log.info('Room unlock', data);
      this.refresh();
    });
  }

  try_unlock() {
    this.setState({'modal': {'type': 'unlock'}});
  }

  componentDidMount() {
    this.refresh();
    this.interval = setInterval(this.refresh.bind(this), 1000*60);
  }

  show_people(room) {
    return () => {
      this.setState({'modal': {'type': 'members', 'args': room }});
    };
  }

  close_modal() {
    this.setState({'modal': null});
  }

  modal() {
    let modal = this.state.modal;
    if(modal) {
      let wrapped = <SimpleModal />;
      switch(modal.type) {
      case 'unlock':
        wrapped = <UnlockModal unlock={this.unlock.bind(this)} />;
        break;
      case 'members':
        wrapped = <MembersModal args={modal.args}/>;
        break;
      case 'password':
        wrapped = <PasswordModal args={modal.args} try_join={this.join.bind(this)}/>;
        break;
      };
      return <MaterializeCSSModal close={this.close_modal.bind(this)}> {wrapped} </MaterializeCSSModal>;
    };
    return <div />;
  }

  render () {
    let {has_room, rooms, can_room, urls, csrf} = this.state;
    let globals = {can_room};
    globals.join = this.join.bind(this);
    globals.try_unlock = this.try_unlock.bind(this);
    globals.show_people = this.show_people.bind(this);
    globals.join_password = this.join_password.bind(this);
    globals.join_unlock = (arg) => { return this.join(arg, {'lock': false}); };
    let rooms_view = rooms.map((room) => { return(<Card key={room.id} room={room} globals={globals} />); });
    let modal = this.modal();
    return (
        <div>
          {modal}
          <div className="section flexbox center-items-horizontal full-height">
            <div className="container">
              <div className="row">
                {rooms_view}
              </div>
            </div>
          </div>
        </div>
    );
  };
}
