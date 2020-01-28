
import React from "react";
import TextForm from './text_form';
import TextAreaForm from './text_area_form';
import CheckboxForm from './checkbox_form';
import NaturalNumberForm from './natural_number_form';
import { composeForms } from './forms';

const BedsForm = composeForms({ single: NaturalNumberForm, double: NaturalNumberForm},
  ([SingleInput, DoubleInput]) => props => {
    const onChange = name => val => {
      props.onChange({...props.value, [name]: val});
    }

    return (
      <div>
        <SingleInput value={props.value["single"]} name={ props.name + "Single" } onChange={onChange("single")}/>
        <DoubleInput value={props.value["double"]} name={ props.name + "Double" } onChange={onChange("double")}/>
      </div>
    )
  
})

const RoomForm = composeForms(
  {
    name: TextForm,
    description: TextAreaForm,
    available_beds: BedsForm,
    beds: BedsForm,
    hidden: CheckboxForm,
  },
  ([NameInput, DescriptionInput, AvailableBedsInput, BedsInput, HiddenInput]) => props => {
    const onChangeAvailableBeds = available_beds => {
      const beds = {
        single: Math.max(props.value.beds.single, available_beds.single),
        double: Math.max(props.value.beds.double, available_beds.double),
      }
      props.onChange({...props.value, available_beds, beds});
    }

    const onChangeBeds = beds => {
      const available_beds = {
        single: Math.min(props.value.available_beds.single, beds.single),
        double: Math.min(props.value.available_beds.double, beds.double),
      }
      props.onChange({...props.value, available_beds, beds});
    }

    const onChange = name => val => {
      props.onChange({...props.value, [name]: val});
    }

    return (
      <div>
        <NameInput value={props.value["name"]} name={"Name"} onChange={onChange("name")}/>
        <DescriptionInput value={props.value["description"]} name={"Description"} onChange={onChange("description")}/>
        <AvailableBedsInput value={props.value["available_beds"]} name={"AvailableBeds"} onChange={onChangeAvailableBeds}/>
        <BedsInput value={props.value["beds"]} name={"Beds"} onChange={onChangeBeds}/>
        <HiddenInput value={props.value["hidden"]} name={"Hidden"} onChange={onChange("hidden")}/>
      </div>
    )
  })

  export default RoomForm;
