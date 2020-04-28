$('#changeShipmentStatusModal').on("show.bs.modal", function (e) {
  $(".modal-title").html($(e.relatedTarget).data('title'));
  $("#single-modal-form").attr('action', '' + $(e.relatedTarget).data('action'));
  if ($(e.relatedTarget).data('method') === 'PUT') {
    $("#input-method").val($(e.relatedTarget).data('method'));
    $('select[name="status"]').val($(e.relatedTarget).data('status'));
  }
});

$('#ventilators').change(function () {
  var value = $(this).val();
  if (value) {
    var valueSegs = value.split('_');
    var id = valueSegs[0];
    var serialNumber = valueSegs[1];
    var model = valueSegs[2];

    if ($('#ventilator_' + id).length > 0) return;
    
    var newVentRow = $('#tblVentilator .ventilator-row-template').clone();
    newVentRow.attr('id', 'ventilator_' + id);
    newVentRow.find('.serial-number').text(serialNumber);
    newVentRow.find('.model').text(model);
    newVentRow.find('.btn-cancel').data('id', id);
    newVentRow.find('.actions').append('<input type="hidden" name="ventilator_id" required>');
    newVentRow.find('input[name="ventilator_id"]').val(id);
    newVentRow.removeClass('ventilator-row-template');
    newVentRow.addClass('ventilator_row');
    $('#tblVentilator tbody').append(newVentRow);
    newVentRow.removeClass('d-none');
    $('#tblVentilator .no-ventilator').addClass('d-none');
  }
});

$(document).on('click', '#tblVentilator .btn-cancel', function() {
  var id = $(this).data('id');
  $('#ventilator_' + id).remove();
  if ($('#tblVentilator tbody tr.ventilator_row').length === 0) {
    $('#tblVentilator .no-ventilator').removeClass('d-none');
  }
});
