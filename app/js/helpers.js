
export const exists = (arr, f) =>
  arr.reduce((acc, el) => f(el) | acc, false)

export const map_of_arr = (arr, key_fun) =>
  arr.reduce((acc, el) => { acc[key_fun(el)] = el; return acc; }, {});

export const map_obj_as_arr = (obj, fun) =>
  Object.keys(obj).map(key => fun(obj[key], key))

export const map_obj_as_obj = (obj, fun) => {
  const result = {};
  Object.keys(obj).forEach(key => {
    result[key] = fun(obj[key], key)
  });
  return result;
}

export const formatDate = isoDate => new Date(isoDate).toLocaleString('en-GB', {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short'
});

export const roomCapacity = beds => beds.single + beds.double * 2

export const roomFullness = room => room.members.length / roomCapacity(room.available_beds)
