import { add_organization } from "./zosia_api";
import { resolve } from "uri-js";
import { rejects } from "assert";

const getOrganizationInput = () => {
  const labels = Array.from(document.getElementsByTagName("label"));
  const maybe_org_label = labels.filter(label => label.textContent == "Organization")[0];
  if (!maybe_org_label)
  {
    console.error("No label organization");
    return;
  }
  const org_label = maybe_org_label;
  return org_label.parentElement;
}

const createAddOrgLink = (onclick) => {
  const add_org_link = document.createElement("a");
  add_org_link.textContent = "Add organization";
  add_org_link.href = "javascript:void(0)";
  add_org_link.onclick = onclick
  return add_org_link;
}

const setProgressType = (name) => {
  const progress_type = document.getElementById("progress_type");
  progress_type.className = name;
}

const clearErrors = () => {
  const name_error = document.getElementById("name_error");
  name_error.innerText = "";
}

const appendError = (error) => {
  const name_error = document.getElementById("name_error");
  const error_paragraph = document.createElement("p");
  error_paragraph.innerText = error;
  name_error.appendChild(error_paragraph);
}

const resetOrgModal = () => {
  setProgressType("");
  const org_name = document.getElementById("org_name");
  org_name.value = "";
}

const initAddOrgModal = (onAdd) => {
  const add_org_modal = document.getElementById("add_org");
  M.Modal.init(add_org_modal, {
    onCloseEnd: () => {
      resetOrgModal();
    },
  })[0];

  const add_org_accept = document.getElementById("add_org_accept");
  add_org_accept.onclick = () => {
    const org_name = document.getElementById("org_name");
    setProgressType("indeterminate");
    clearErrors();
    onAdd(org_name.value)
      .then(() => {
        const instance = M.Modal.getInstance(add_org_modal);
        instance.close();
        resetOrgModal();
      }, () => {
        setProgressType("");
      });
  }
  return add_org_modal;
}

const addOrgToSelect = (id, name) => {
  const new_org_option = document.createElement("option");
  new_org_option.value = id;
  new_org_option.innerText = name;

  const org_select = document.getElementsByName('organization')[0];
  org_select.append(new_org_option);
  org_select.value = id;

  const elems = document.querySelectorAll('select');
  M.FormSelect.init(elems, {});
}

const addOrg = (name) => {
  return add_organization(name)
    .then(json => {
      const org_name = json.name + " (" + json.user.first_name + " " + json.user.last_name + ")";
      addOrgToSelect(json.id, org_name);
      return Promise.resolve();
    }, ({json, status}) => {
        json.name.forEach(appendError);
        return Promise.reject();
      }
    );
  }

const allowAddingOrgs = () => {
  const add_org_modal = initAddOrgModal(addOrg);
  const add_org_link = createAddOrgLink(() => M.Modal.getInstance(add_org_modal).open());

  const org_input = getOrganizationInput();
  org_input.append(add_org_link);
}

$(document).ready(function() {
  allowAddingOrgs();
});
