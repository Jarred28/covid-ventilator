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
    var unavailable_label = ""
    var arrived_label = ""
    $("label").each(function(index) {
        if ($(this)[0].innerHTML.indexOf("Unavailable") !== -1) {
            unavailable_label = $(this)
        }
        if ($(this)[0].innerHTML.indexOf("Arrived") !== -1) {
            arrived_label = $(this)
        }
    })
    if (value == "Arrived") {
      unavailable_label.hide()
      arrived_label.show()
      $("select[name='arrived_code']").show()
      $("select[name='unavailable_code']").hide()
    } else if (value == "Unavailable") {
      unavailable_label.show()
      arrived_label.hide()
      $("select[name='unavailable_code']").show()
      $("select[name='arrived_code']").hide()
    } else {
      arrived_label.hide()
      unavailable_label.hide()
      $("select[name='arrived_code']").hide()
      $("select[name='unavailable_code']").hide()
    }
}

$("select[name='status']").on('change', function() { onStatusChangeLabelModifications(this.value) });

$('#singleVentilatorModal').on("show.bs.modal", function (e) {
  $(".modal-title").html($(e.relatedTarget).data('title'));
  $("#single-modal-form").attr('action', '' + $(e.relatedTarget).data('action'));
  if ($(e.relatedTarget).data('method') === 'PUT') {
    $("#input-method").val($(e.relatedTarget).data('method'));
    $("#createSerializer").hide();
    $("#updateSerializer").show();
    $("input[name='serial_number']").val($(e.relatedTarget).data('serial-number'));
    $('select[name="quality"]').val($(e.relatedTarget).data('quality'));
    $("input[name='ventilator_model.manufacturer']").val($(e.relatedTarget).data('model-manufacturer'));
    $("input[name='ventilator_model.model']").val($(e.relatedTarget).data('model'));
    $("input[name='ventilator_model.monetary_value']").val($(e.relatedTarget).data('monetary-value'));
    $("select[name='status']").val($(e.relatedTarget).data('status'));
    $("select[name='unavailable_code']").val($(e.relatedTarget).data('unavailable-code') === 'None' ? '' : $(e.relatedTarget).data('unavailable-code'));
    $("select[name='arrived_code']").val($(e.relatedTarget).data('arrived-code'));
    onStatusChangeLabelModifications($("select[name='status']")[0].value);
  } else {
    $("#input-method").val('');
    $("#updateSerializer").hide();
    $("#createSerializer").show();
    $("input[name='serial_number']").val('');
    $('select[name="quality"]').val('');
    $("input[name='ventilator_model.manufacturer']").val('');
    $("input[name='ventilator_model.model']").val('');
    $("input[name='ventilator_model.monetary_value']").val('');
  }
});

