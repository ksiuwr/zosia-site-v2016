// TODO:
// 0. Show people in room button
// 1. After join password modal (unless no password)
// 2. Before unlock confirmation modal
// 3. Before join new room modal (unless empty)
// 4. Before join new room lock or not
// 5. Refresh button + interval + callback instead of page reload
// 6. Reduce request amount (return new data from join)
const Links = (props) => {
  let {globals, room, can_join} = props;
  let {owns, is_locked} = room;
  let {can_room, join, unlock} = globals;
  let join_link = <a />;
  if(can_room) {
    if(can_join) {
      if(is_locked) {
        join_link = <a href="#"> Join with password </a>;
      } else {
        join_link = <a onClick={join(room)} href="#"> Join </a>;
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
  return (
      <div className="card-action">
        {join_link}
      </div>
  );
};

const Card = ({room, globals}) => {
  let {name, owns, free_places, description, capacity, is_locked, join} = room;
  let can_join = free_places > 0;
  let color = 'blue-grey';
  if(is_locked) {
    color = 'brown';
  }
  if(!can_join) {
    color = 'grey';
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

class SimpleModal extends React.Component {
  componentDidMount() {
    let id = '#modal1';
    $(id).modal();
    $(id).modal('open');
  }

  render() {
    return (
        <div id="modal1" className="modal">
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
}

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
      log.debug('Change:');
      delta.map((ch)=> { log.debug(ch.path, ch.kind, ch.rhs);});
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

  modal() {
    let modal = this.state.modal;
    if(modal) {
      switch(modal.type) {
      case 'simple':
        return <SimpleModal />;
      };
    };
    return <div />;
  }

  render () {
    let {has_room, rooms, can_room, urls, csrf} = this.state;
    let globals = {can_room};
    globals.join = this.join.bind(this);
    globals.unlock = this.unlock.bind(this);
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
