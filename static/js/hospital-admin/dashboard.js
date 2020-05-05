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


function onStatusChangeLabelModifications(value) {
  if (value == "Arrived") {
    $("#single-modal-form select[name='arrived_code']").closest('.form-group').removeClass('d-none');
    $("#single-modal-form select[name='unavailable_code']").closest('.form-group').addClass('d-none');
  } else if (value == "Unavailable") {
    $("#single-modal-form select[name='unavailable_code']").closest('.form-group').removeClass('d-none');
    $("#single-modal-form select[name='arrived_code']").closest('.form-group').addClass('d-none');
  } else {
    $("#single-modal-form select[name='arrived_code']").closest('.form-group').addClass('d-none');
    $("#single-modal-form select[name='unavailable_code']").closest('.form-group').addClass('d-none');
  }
}

$("select[name='status']").on('change', function() { onStatusChangeLabelModifications(this.value) });

$('#singleVentilatorModal').on("show.bs.modal", function (e) {
  $("#single-modal-form .modal-title").html($(e.relatedTarget).data('title'));
  $("#single-modal-form").attr('action', '' + $(e.relatedTarget).data('action'));
  if ($(e.relatedTarget).data('method') === 'PUT') {
    $("#input-method").val($(e.relatedTarget).data('method'));
    $('#single-modal-form .modal-body .create-template').remove();
    if ($('#single-modal-form .modal-body .update-template').length === 0) {
      var $updateForm = $('.update-template').clone();
      $('#single-modal-form .modal-body').append($updateForm);
      $updateForm.removeClass('d-none');
    }
    $("#single-modal-form input[name='serial_number']").val($(e.relatedTarget).data('serial-number'));
    $('#single-modal-form select[name="quality"]').val($(e.relatedTarget).data('quality'));
    $("#single-modal-form input[name='ventilator_model.manufacturer']").val($(e.relatedTarget).data('model-manufacturer'));
    $("#single-modal-form input[name='ventilator_model.model']").val($(e.relatedTarget).data('model'));
    $("#single-modal-form input[name='ventilator_model.monetary_value']").val($(e.relatedTarget).data('monetary-value'));
    $("#single-modal-form select[name='status']").val($(e.relatedTarget).data('status'));
    $("#single-modal-form select[name='unavailable_code']").val($(e.relatedTarget).data('unavailable-code') === 'None' ? '' : $(e.relatedTarget).data('unavailable-code'));
    $("#single-modal-form select[name='arrived_code']").val($(e.relatedTarget).data('arrived-code'));
    onStatusChangeLabelModifications($("#single-modal-form select[name='status']")[0].value);
  } else {
    $("#input-method").val('');
    $('#single-modal-form .modal-body .update-template').remove();
    if ($('#single-modal-form .modal-body .create-template').length === 0) {
      var $createForm = $('.create-template').clone();
      $('#single-modal-form .modal-body').append($createForm);
      $createForm.removeClass('d-none');
    }
    $("#single-modal-form input[name='serial_number']").val('');
    $('#single-modal-form select[name="quality"]').val('');
    $("#single-modal-form input[name='ventilator_model.manufacturer']").val('');
    $("#single-modal-form input[name='ventilator_model.model']").val('');
    $("#single-modal-form input[name='ventilator_model.monetary_value']").val('');
  }
});

