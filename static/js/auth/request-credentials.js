var entities = [];

$('.entity-selector').change(function () {
    var value = $(this).val();
    if (!value) {
        $('#selected-entity').addClass('d-none');
    } else {
        var valueSegs = value.split('_');
        $('#selected-entity .title').text(valueSegs[0]);
        $('#hospitalName').val(valueSegs[2]);
        $('#selected-entity .btn-add-association').data('id', valueSegs[1]);
        $('#selected-entity').removeClass('d-none');
    }
});

$('.btn-add-association').click(function () {
    var id = $(this).data('id');
    var name = $('#hospitalName').val();
    var entityType = $('#selected-entity .title').text();

    var duplicated = entities.find(function(entity) {
        return entity.id === id && entity.type === entityType;
    });

    if (duplicated) return;

    entities.push({
        id: id,
        name: name,
        type: entityType
    });

    var newEntityRow = $('#tblEntity .entity-row-template').clone();
    newEntityRow.find('.type').text(entityType);
    newEntityRow.find('.name').text(name);
    newEntityRow.find('.btn-cancel').data('id', id);
    newEntityRow.find('.actions').append(
        '<input type="hidden" name="entity_id" required><br>' +
        '<input type="hidden" name="entity_type" required>'
    );
    newEntityRow.find('input[name="entity_id"]').val(id);
    newEntityRow.find('input[name="entity_type"]').val(entityType);
    newEntityRow.removeClass('entity-row-template');
    $('#tblEntity tbody').append(newEntityRow);
    newEntityRow.removeClass('d-none');
    $('#tblEntity .no-entity').addClass('d-none');
});

$(document).on('click', '#tblEntity .btn-cancel', function () {
    var id = $(this).data('id');
    var type = $(this).closest('type').text();
    var idx = entities.findIndex(function(entity) {
        return entity.id === id && entity.type === type;
    });
    entities.splice(idx, 1);
    $(this).closest('tr').remove();
    if (entities.length === 0) {
        $('#tblEntity .no-entity').removeClass('d-none');
    }
});
