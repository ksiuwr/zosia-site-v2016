
import React from "react";

import {useModal} from "./modals";
import {Modal} from "./materialize_modal";
import RoomsView from "./room";
import { create_room } from "./zosia_api";
import { create } from "domain";

const form = (defaultValue, input) => {
  return {
    default: defaultValue,
    Input: input,
  }
}

const composeForms = (forms, parametrized_component) => {
  const defaultValue = {};
  Object.keys(forms).forEach(name => defaultValue[name] = forms[name].default);
  const inputs = Object.keys(forms).map(name => forms[name].Input)
  return form(defaultValue, parametrized_component(inputs));
}

const NaturalNumberForm = form(0, (props) => {
  const onChange = e => {
    props.onChange(e.target.value);
  }
  return (
    <div className="input-field col s3">
      <input id={props.name} type="number" min="0" className="validate" value={props.value} onChange={onChange}/>
      <label htmlFor={props.name}>{props.name}</label>
    </div>
  )
});

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

const TextAreaForm = form("", (props) => {
  const onChange = e => {
    props.onChange(e.target.value);
  };

  return (
    <div className="input-field col s12">
      <textarea id={props.name} className="materialize-textarea" value={props.value} onChange={onChange}/>
      <label htmlFor={props.name}>{props.name}</label>
    </div>
  )
})

const TextForm = form("", (props) => {
  const onChange = e => {
    props.onChange(e.target.value);
  };

  React.useEffect(() => {
    M.updateTextFields();
  }, []);

  return (
    <div className="input-field col s12">
      <input 
        id={props.name} type="text" className="validate" value={props.value} 
        onChange={onChange}
      />
      <label htmlFor={props.name}>{props.name}</label>
    </div>
  )
});

const CheckboxForm = form(false, (props) => {
  const onChange = e => {
    console.log(e.target.checked);
    props.onChange(e.target.checked);
  }
  return (
    <div className="col s12">
      <p>
        <label>
          <input type="checkbox" checked={props.value} onChange={onChange}/>
          <span>{props.name}</span>
        </label>
      </p>
    </div>
  )
});
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
  }
)

const useForm = form => {
  const [value, setValue] = React.useState(form.default);
  return [form.Input, value, setValue]
}


const AddRoomModal = props => {
  const [FormInput, formValue, setValue] = useForm(RoomForm);
  const submit = () => {
    create_room(formValue); 
  }
  
  return (
    <Modal closeModal={props.closeModal}>
      <div className="modal-content">
        <h4>Add Room</h4>
        <div className="row">
          <FormInput name="" value={formValue} onChange={setValue}></FormInput>
        </div>
      </div>
      <div className="modal-footer">
        <a href="#!" className="modal-close waves-effect waves-green btn-flat" onClick={submit}>
          Add
        </a>
      </div>
    </Modal>
  );
}

const SearchBar = (props) =>
{
  React.useEffect(() => {
    const elems = document.querySelectorAll('#sorting');
    const instances = M.FormSelect.init(elems, {})
  }, []);

  const [openModal, closeModal] = useModal()
  
  return (
    <div className="col s12">
      <ul style={{height: "50px", lineHeight: "45px"}}>
        <li style={{float: "left", margin: "5px", marginTop: "12px"}}>
            <i className="material-icons black-text">search</i>
        </li>
        <li style={{float: "left", margin: "5px"}}>
          <input type="text" placeholder="search" onChange={props.onSearch}/>
        </li>
        <li className="hide-on-med-and-down"style={{float: "left", margin: "5px"}}>
          <label>
            <input type="checkbox" onChange={props.onShowFullRoomsToggle} defaultChecked={true}/>
            <span> Show full rooms </span>
          </label>
        </li>
        <li className="hide-on-med-and-down" style={{float:"left", margin: "5px"}}>
          <a href="#" className="waves-effect waves-light btn" onClick={() => openModal(AddRoomModal, {closeModal})}> Add room </a>
        </li>
        <li className="hide-on-small-only" style={{float: "right", margin: "5px"}}>
          <select id="sorting" onChange={props.onSortingStrategyChange}>
            <option value="1">Sort by room numbers</option>
            <option value="2">Sort by fullness</option>
          </select>
        </li>
      </ul>
    </div>
  )
}

export default SearchBar;
