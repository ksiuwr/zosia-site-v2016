
import React from 'react';
import { map_obj_as_arr, map_obj_as_obj } from '../helpers.js'

export const form = (defaultValue, input) => {
  return {
    default: defaultValue,
    Input: input,
  }
}

export const composeForms = (forms, parametrized_component) => {
  const defaultValue = 
    map_obj_as_obj(forms, form => form.default);
  const inputs = map_obj_as_arr(forms, form => form.Input) 
  return form(defaultValue, parametrized_component(inputs));
}

export const useForm = form => {
  const [value, setValue] = React.useState(form.default);
  return [form.Input, value, setValue]
}
