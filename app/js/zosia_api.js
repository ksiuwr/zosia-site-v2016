import { resolve } from "path";

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
    }).then(response => {
        if (response.ok) {
            return response.json().then(json => Promise.resolve(json));
        }

        return response.json().then(json => Promise.reject({
            'status': response.status,
            'body': json
        }));
    });
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
    }).then(response => {
        if (response.ok) {
            return response.json().then(json => Promise.resolve(json));
        }

        return response.json().then(json => Promise.reject({
            'status': response.status,
            'body': json
        }));
    });
}

const delete_ = (uri, json) => {
    return fetch(root + uri, {
        method: 'DELETE',
        body: JSON.stringify(json), // string or object
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        }
    }).then(response => {
        if (response.ok) {
            return response.json().then(json => Promise.resolve(json), () => Promise.resolve(""));
        }

        return response.json().then(json => Promise.reject({
            'status': response.status,
            'body': json
        }));
    });
}

const put = (uri, json) => {
    return fetch(root + uri, {
        method: 'PUT',
        body: JSON.stringify(json),
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/json',
        }
    }).then(response => {
        if (response.ok) {
            return response.json().then(json => Promise.resolve(json));
        }

        return response.json().then(json => Promise.reject({
            'status': response.status,
            'body': json
        }));
    });
}

const get_me = () => get('/api/v1/users/me');
const me_id = () => get_me().then(({ id }) => id)

export const me = {
    id: me_id,
    info: get_me,
    room: get_my_room,
    join_room: (room, password) => me_id().then(id => join_room(room, id, password)),
    leave_room: (room) => me_id().then(id => leave_room(room, id)),
    lock_room: (room) => me_id().then(id => lock_room(room, id)),
    unlock_room: (room) => me_id().then(id => unlock_room(room, id)),
}

export const get_users = () => get('/api/v1/users/')
export const get_rooms = () => get('/api/v2/rooms/')
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

export const get_my_room = (json) => get('/api/v2/rooms/mine')
export const create_room = (json) => post('/api/v2/rooms/', convert_room_to_api(json))
export const delete_room = (id) => delete_('/api/v2/rooms/' + id + '/', {})
export const edit_room = (id, json) => put('/api/v2/rooms/' + id + '/', convert_room_to_api(json))
export const get_room = (id) => get('/api/v2/rooms/' + id)
export const join_room = (id, user, password) => post('/api/v2/rooms/' + id + '/member/', { user, password })
export const leave_room = (id, user) => delete_('/api/v2/rooms/' + id + '/member/', { user })
export const get_users_room = () => get('/api/v2/rooms/members')
export const hide_room = (id) => post('/api/v2/rooms/' + id + '/hidden/', {})
export const unhide_room = (id) => delete_('/api/v2/rooms/' + id + '/hidden/', {})
export const lock_room = (id, user) => post('/api/v2/rooms/' + id + '/lock/', { user })
export const unlock_room = (id, user) => delete_('/api/v2/rooms/' + id + '/lock/', {})
export const add_organization = name => post('/api/v1/users/organizations/', { name })
export const get_organizations = name => get('/api/v1/users/organizations/')

