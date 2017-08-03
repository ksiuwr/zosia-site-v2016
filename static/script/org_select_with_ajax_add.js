$(document).ready(function(){
  // the "href" attribute of the modal trigger must specify the modal ID that wants to be triggered
  $('.modal').modal();
  (function() {
    function save_org(ev) {
      ev.stopPropagation();
      var $this = $(this);
      var url = $this.attr('data-url');
      var target = $this.attr('data-target');
      // TODO: This won't work with multiple select_with_ajax_add on one page.
      var $fields = $('#org_select_with_ajax_add_form :input');
      var data = {};
      $fields.each(function() {
        var $this = $(this);
        data[this.name] = $this.val();
      });
      data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();
      if (url && url.length > 0) {
        $.post(url, data)
        .done(function(response) {
          console.log(response);
          $(target).append('<option selected value="' + response.value + '">' + response.html + "</option>")
          console.log($(target));
          $('select').material_select();
        })
        .fail(function(response) {
          console.error(response);
        })
      } else {
        console.error("ASSERT ERROR: Empty url for select_with_ajax_add");
      }
    };
    $('#org_select_with_ajax_add_save').on('click', save_org);
  }());
});
