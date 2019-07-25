
export const exists = (arr, f) =>
  arr.reduce((acc, el) => f(el) | acc, false)
