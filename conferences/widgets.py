from django.forms.widgets import Select
from django.utils.html import conditional_escape, format_html, html_safe
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.shortcuts import reverse


MODAL_TRIGGER = """
<a class="waves-effect waves-light btn-flat col s1" href="#modal1"><i class="material-icons">add</i></a>
"""


MODAL_BODY = """
 <!-- Modal Structure -->
  <div id="modal1" class="modal">
    <div class="modal-content">
      <h4>Add your organization</h4>
      <p>Others won't see your organization until it's accepted by admin.</p>
      <div class="col s12" id="select_with_ajax_add">
          <div class="row">
            <div class="col s12">
              Your organization name:
              <div class="input-field inline">
                <input name="name" id="org-name" type="text" class="validate"/>
                <label for="org-name" data-error="wrong" data-success="right">name</label>
              </div>
          </div>
      </div>
    </div>
    <div class="modal-footer">
      <a href="#!" data-url="{}" data-target="#org-select" id="org-save"
        class="modal-action modal-close waves-effect waves-green btn-flat">Add</a>
    </div>
  </div>
"""


class SelectWithAjaxAdd(Select):
    class Media:
        js = ('script/select_with_ajax_add.js',)

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs=attrs, choices=choices)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        attrs['class'] = attrs.get('class', '') + ' col s11'
        final_attrs = self.build_attrs(attrs, name=name)
        # TODO: generate new id
        output = ['<div class="row">', format_html('<select id="org-select" {}>', flatatt(final_attrs))]
        options = self.render_options([value])
        if options:
            output.append(options)
        output.append('</select>')
        # TODO: trans
        # TODO: generate new id
        output.append(MODAL_TRIGGER)
        output.append('</div>')
        # TODO: trans
        # TODO: a id
        # TODO: Move text to initializer
        # TODO: Move url to initializer
        output.append(MODAL_BODY.format(reverse('create_organization')))
        return mark_safe('\n'.join(output))
