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
  $(".modal-title").html($(e.relatedTarget).data('title'));
  $("#single-modal-form").attr('action', '' + $(e.relatedTarget).data('action'));
  if ($(e.relatedTarget).data('method') === 'PUT') {
    $("#input-method").val($(e.relatedTarget).data('method'));
    $("input[name='model_num']").val($(e.relatedTarget).data('model-num'));
    $('select[name="status"]').val($(e.relatedTarget).data('status'));
  } else {
    $("#input-method").val('');
    $("input[name='model_num']").val('');
    $('select[name="status"]').val('Unknown');
  }
});
