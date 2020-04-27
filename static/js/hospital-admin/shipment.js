$('#changeShipmentStatusModal').on("show.bs.modal", function (e) {
  $(".modal-title").html($(e.relatedTarget).data('title'));
  $("#single-modal-form").attr('action', '' + $(e.relatedTarget).data('action'));
  if ($(e.relatedTarget).data('method') === 'PUT') {
    $("#input-method").val($(e.relatedTarget).data('method'));
    $('select[name="status"]').val($(e.relatedTarget).data('status'));
  }
});

$('#shipmentStatusUpdate').on("show.bs.modal", function (e) {
  $("#shipment_id").attr('value', $(e.relatedTarget).data('shipment-id'));
  let action = $(e.relatedTarget).data('action');
  $("#action").attr('value', action);
  if (action === 'approve') {
    $("#modal-question").html('Do you want to approve this request?');
  } else {
    $("#modal-question").html('Do you want to deny this request?');
  }
});