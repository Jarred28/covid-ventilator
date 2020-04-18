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
    $("input[name='serial_number']").val($(e.relatedTarget).data('serial-number'));
    $('select[name="quality"]').val($(e.relatedTarget).data('quality'));
    $("input[name='ventilator_model.manufacturer']").val($(e.relatedTarget).data('model-manufacturer'));
    $("input[name='ventilator_model.model']").val($(e.relatedTarget).data('model'));
    $("input[name='ventilator_model.monetary_value']").val($(e.relatedTarget).data('monetary-value'));
  } else {
    $("#input-method").val('');
    $("input[name='serial_number']").val('');
    $('select[name="quality"]').val('');
    $("input[name='ventilator_model.manufacturer']").val('');
    $("input[name='ventilator_model.model']").val('');
    $("input[name='ventilator_model.monetary_value']").val('');
  }
});
