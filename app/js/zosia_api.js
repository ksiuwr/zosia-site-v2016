
const root = location.protocol + '//' + location.host;

const cache = () => {
    const cached_data = {};
    const has_key = key => cached_data.hasOwnProperty(key)
    const get = key => cached_data[key]
    const store = (key, data) => {
        cached_data[key] = data;
    }
    const clear = () => {
        cached_data = {};
    }
    return {
        has_key,
        get,
        store,
        clear
    };
}

const api_cache = cache();

const get = uri => {
    return fetch(root + uri, {
        method: 'GET',
    })
    .then(response => response.json())
}

function getCSRFToken() {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, 10) == ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

const post = (uri, json) => {
    return fetch(root + uri, {
        method: 'POST',    
        body: JSON.stringify(json), // string or object
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json());
}

const delete_ = (uri) => {
    return fetch(root + uri, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
}

const put = (uri, json) => {
    return fetch(root + uri, {
        method: 'PUT',
        body: JSON.stringify(json),
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/json',
        }
    })
}


const get_me = () => get('/api/v1/users/me');
const me_id = () => get_me().then(({ id }) => id)
export const me = {
    id: me_id,
    info: get_me,
    join_room: (room) => me_id().then(id => join_room(room, id)),
    leave_room: (room) => me_id().then(id => leave_room(room, id)),
    lock_room: (room) => me_id().then(id => lock_room(room, id)),
    unlock_room: (room) => me_id().then(id => unlock_room(room, id)),
}

export const get_users = () => get('/api/v1/users/')
export const get_rooms = () => get('/api/v1/rooms/')
    .then(rooms => rooms.map(room => {
        const {
            beds_single,
            beds_double,
            available_beds_single,
            available_beds_double,
            ...room_
        } = room;
        return {
            ...room_, 
            beds: { 
                single: beds_single,
                double: beds_double,
            },
            available_beds: {
                single: available_beds_single,
                double: available_beds_double,
            },
        }
    }))

const convert_room_to_api = (room_) => {
    const { beds, available_beds, ...room} = room_
    return {
        ...room,
        beds_single: beds.single,
        beds_double: beds.double,
        available_beds_single: available_beds.single,
        available_beds_double: available_beds.double,
    }
}

export const create_room = (json) => 
    post('/api/v1/rooms/', convert_room_to_api(json))
export const delete_room = (id) => delete_('/api/v1/rooms/' + id + '/')
export const edit_room = (id, json) => 
    put('/api/v1/rooms/' + id + '/', convert_room_to_api(json))
const get_room = (id) => get('/api/v1/rooms/' + id)
export const join_room = (id, user) => post('/api/v1/rooms/' + id + '/join/', { user })
export const leave_room = (id, user) => post('/api/v1/rooms/' + id + '/leave/', { user })
export const users = () => get('/api/v1/users/');
const hide_room = (id) => post('/api/v1/rooms/' + id + '/join/', {})
const unhide_room = (id) => post('/api/v1/rooms/' + id + '/join/', {})
const lock_room = (id, user) => post('/api/v1/rooms/' + id + '/lock/', { user })
const unlock_room = (id, user) => post('/api/v1/rooms/' + id + '/unlock/', { user })

