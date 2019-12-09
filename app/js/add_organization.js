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

const addOrg = (name) => {
  return add_organization(name)
    .then(json => {
      const org_select = document.getElementsByName('organization')[0];
      const new_org_option = document.createElement("option");
      const org_name = json.name + " (" + json.user.first_name + " " + json.user.last_name + ")";
      new_org_option.innerText = org_name;
      new_org_option.value = json.id;
      org_select.append(new_org_option);
      const m_org_select = M.FormSelect.getInstance(org_select);
      const elems = document.querySelectorAll('select');
      const instances = M.FormSelect.init(elems, {});
      progress_type.className = "";
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

  const add_org_accept = document.getElementById("add_org_accept");
}

$(document).ready(function() {
  allowAddingOrgs();
});
