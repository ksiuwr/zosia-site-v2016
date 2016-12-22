const Links = ({globals, owns, is_locked, can_join, id}) => {
  let {can_room, join, unlock} = globals;
  if(!can_room) {
    return (<div />);
  }
  let join_link = <a />;
  if(can_join) {
    if(is_locked) {
      join_link = <a href="#"> Join with password </a>;
    } else {
      join_link = <a onClick={join(id)} href="#"> Join </a>;
    }
  }
  if(owns) {
    if(is_locked) {
      join_link = <a href="#" onClick={unlock}> Unlock </a>;
    } else {
      join_link = <a />;
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
      <div className={"card darken-1 " + color} >
          <div className="card-content white-text">
      <span className="card-title">Room {name}</span>
      <p>{description}</p>
      <p> Places: {free_places || 0} / {capacity}</p>
          </div>
      <Links owns={owns} id={join} globals={globals} is_locked={is_locked} can_join={can_join}/>
        </div>
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

  sortRooms() {
    this.setState({
      'rooms': _(this.state.rooms).sortBy(({id}) => { return id; })
    });
    log.debug('Rooms', this.state.rooms);
  }

  refresh() {
    $.getJSON(this.state.urls.status, (data) => {
      this.setState(data);
      this.sortRooms();
    });
  }

  join(id) {
    let main = this;
    return () => {
      $.post(id, {'csrfmiddlewaretoken': main.state.csrf}, (data) => {
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

  render () {
    let {rooms, can_room, urls, csrf} = this.state;
    let globals = {can_room, urls, csrf};
    globals.join = this.join.bind(this);
    globals.unlock = this.unlock.bind(this);
    let rooms_view = rooms.map((room) => { return(<Card key={room.id} room={room} globals={globals} />); });
    return (
        <div className="row">
        {rooms_view}
      </div>
    );
  };
}
