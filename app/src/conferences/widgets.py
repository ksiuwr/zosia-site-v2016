from django.forms.utils import flatatt
from django.forms.widgets import Select
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

MODAL_TRIGGER = """
<a class="waves-effect waves-light btn-flat col s1" href="#modal1"><i 
class="material-icons">add</i></a>
"""

MODAL_BODY = """
 <!-- Modal Structure -->
  <div id="modal1" class="modal">
    <div class="modal-content">
      <h4>{header}</h4>
      <p>{helper_text}</p>
      <div class="col s12" id="org_select_with_ajax_add_form">
          <div class="row">
            <div class="col s12">
              {label}
              <div class="input-field inline">
                <input name="name" id="org-name" type="text" class="validate"/>
                <label for="org-name" data-error="wrong" data-success="right">{placeholder}</label>
              </div>
          </div>
      </div>
    </div>
    <div class="modal-footer">
      <a href="#!" data-url="{url}" data-target="#org-select" id="org_select_with_ajax_add_save"
        class="modal-action modal-close waves-effect waves-green btn-flat">Add</a>
    </div>
  </div>
"""


# NOTE: Don't try to use more than one at the same time.
class OrgSelectWithAjaxAdd(Select):
    class Media:
        js = ('script/org_select_with_ajax_add.js',)

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs=attrs, choices=choices)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        attrs['class'] = attrs.get('class', '') + ' col s11'
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<div class="row">',
                  format_html('<select id="org-select" {}>', flatatt(final_attrs))]
        options = self.render_options([value])
        if options is not None:
            output.append(options)
        output.append('</select>')
        output.append(MODAL_TRIGGER)
        output.append('</div>')
        output.append(MODAL_BODY.format(
            url=reverse('create_organization'),
            header=_('Add your organization'),
            helper_text=_("Others won't see your organization until it's accepted by admin."),
            label=_('Your organization name:'),
            placeholder=_('name')
        ))
        return mark_safe('\n'.join(output))
