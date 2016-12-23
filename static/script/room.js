// TODO:
// 1. After join password modal (unless no password)
// 2. Before unlock confirmation modal
// 3. Before join new room modal (unless empty)
// 4. Before join new room lock or not
// 5. Refresh button + interval + callback instead of page reload
// 6. Reduce request amount (return new data from join)
const Links = (props) => {
  let {globals, room, can_join} = props;
  let {inside, owns, is_locked, people} = room;
  let {can_room, join, unlock, show_people} = globals;
  let join_link = <a />;
  let show_people_link = <a />;
  if(can_room) {
    if(can_join) {
      if(is_locked) {
        join_link = <a href="#"> Join with password </a>;
      } else {
        if(!inside) {
          join_link = <a onClick={join(room)} href="#"> Join </a>;
        }
      }
    }
    if(owns) {
      if(is_locked) {
        join_link = <a href="#" onClick={unlock}> Unlock </a>;
      } else {
        join_link = <a />;
      }
    }
  }
  if(people && people.length > 0) {
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
  if(is_locked) {
    color = 'brown';
  }
  if(!can_join) {
    color = 'grey';
  }
  if(inside) {
    color = 'teal';
  }
  if(owns) {
    color = 'green';
  }
  return (
      <div className="col s6 m4">
      <div className={"card darken-2 " + color} >
          <div className="card-content white-text">
      <span className="card-title">Room {name}</span>
      <p>{description}</p>
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

  join({join}) {
    let main = this;
    return () => {
      $.post(join, {'csrfmiddlewaretoken': main.state.csrf}, (data) => {
        log.info('Room join', data);
        main.refresh();
      });
    };
  }

  unlock() {
    $.post(this.state.urls.unlock, {'csrfmiddlewaretoken': this.state.csrf}, (data) => {
      log.info('Room unlock', data);
      this.refresh();
    });
  }

  componentDidMount() {
    this.refresh();
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
      case 'members':
        wrapped = <MembersModal args={modal.args}/>;
      };
      return <MaterializeCSSModal close={this.close_modal.bind(this)}> {wrapped} </MaterializeCSSModal>;
    };
    return <div />;
  }

  render () {
    let {has_room, rooms, can_room, urls, csrf} = this.state;
    let globals = {can_room};
    globals.join = this.join.bind(this);
    globals.unlock = this.unlock.bind(this);
    globals.show_people = this.show_people.bind(this);
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
