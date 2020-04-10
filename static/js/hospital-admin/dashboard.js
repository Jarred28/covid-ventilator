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
