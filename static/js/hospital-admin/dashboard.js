$('#file1').on('change', function () {
  var files = $(this)[0].files;
  if (files.length > 0) {
    $('.fallback').text(files[0].name);
    $('#closeBtn').removeClass('d-none');
  } else {
    $('.fallback').text('No file selected');
    $('#closeBtn').addClass('d-none');
  }
});

$('body').on('click', '#closeBtn', function() {
  $('#file1')[0].value = '';
  $('.fallback').text('No file selected');
  $(this).addClass('d-none');
});

$('#singleVentilatorModal').on("show.bs.modal", function (e) {
     $(".modal-title").html(''+ $(e.relatedTarget).data('title'));
     if ($(e.relatedTarget).data('method') === 'PUT') {
        $("#input-method").attr('value', '' + $(e.relatedTarget).data('method'));
        $("#input-id").attr('value','' + $(e.relatedTarget).data('id'));
        $($("input[name='model_num']")).attr('value', '' + $(e.relatedTarget).data('model-num'));
        $($('option[value=' + $(e.relatedTarget).data('state') + ']')).attr('selected', 'selected');
     };
});