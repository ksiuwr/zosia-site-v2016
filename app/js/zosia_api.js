
const root = location.protocol + '//' + location.host;

const get = uri => {
    return fetch(root + uri, {
        method: 'GET',
    })
    .then(response => response.json());
}

const post = (uri, json) => {
    return fetch(root + uri, {
        method: 'POST',    
        body: json, // string or object
        headers: {
          'Content-Type': 'application/json'
        }
    })
    .then(response => response.json());
}

const get_rooms = () => get('/api/v1/rooms')
const get_room = (id) => get('/api/v1/rooms/' + id)
const join_room = (id, user_id) => post('/api/v1/rooms/' + id + '/join', { user_id })
const leave_room = (id, user_id) => post('/api/v1/rooms/' + id + '/leave', { user_id })
const hide_room = (id) => post('/api/v1/rooms/' + id + '/join', {})
const unhide_room = (id) => post('/api/v1/rooms/' + id + '/join', {})
const lock_room = (id, user_id) => post('/api/v1/rooms/' + id + '/lock', { user_id })
const unlock_room = (id, user_id) => post('/api/v1/rooms/' + id + '/unlock', { user_id })

export default { get_rooms };
