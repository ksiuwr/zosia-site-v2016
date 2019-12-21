const getLogoInput = () => {
  const labels = Array.from(document.getElementsByTagName("label"));
  const maybe_logo_label = labels.filter(label => label.textContent == "Path to logo")[0];
  if (!maybe_logo_label)
  {
    console.error("No label for path to logo");
    return;
  }
  const logo_label = maybe_logo_label;
  return logo_label.parentElement;
}

const createChooseFromS3Link = (onclick) => {
  const choose_from_s3_link = document.createElement("a");
  choose_from_s3_link.textContent = "Choose file from S3";
  choose_from_s3_link.href = "javascript:void(0)";
  choose_from_s3_link.onclick = onclick
  return choose_from_s3_link;
}

const initS3Modal = (onAdd, paretElement) => {
  const add_s3_modal = document.getElementById("choose_logo");
  M.Modal.init(add_s3_modal, {})[0];

  const choose_logo_for_sponsor = document.getElementById("choose_logo_for_sponsor");
  choose_logo_for_sponsor.onclick = () => {
    const select_logo = document.getElementById("select_logo");
    onAdd(select_logo.value, paretElement);
    const instance = M.Modal.getInstance(add_s3_modal);
    instance.close();
  }
  return add_s3_modal;
}

const chooseLogo = (name, paretElement) => {
  if (name != "") {
    const path_to_logo_input = document.getElementById("id_path_to_logo");
    path_to_logo_input.value = name;
    paretElement.children[1].classList.add("active")
  }
}

const allowChoosingLogos = () => {
  const logo_input = getLogoInput();
  const add_s3_modal = initS3Modal(chooseLogo, logo_input);
  const add_s3_link = createChooseFromS3Link(() => M.Modal.getInstance(add_s3_modal).open());
  logo_input.append(add_s3_link);
}

$(document).ready(function() {
  allowChoosingLogos();
});
