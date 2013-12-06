$(function(){

  var ul = $('#upload ul');

  $('#drop .message a').click(function(){
    $('#id_lovefile').click();
  });

  $('#drop').on('dragleave', function (e) {
    $(e.target).removeClass('hover')
  });

  $('#drop').on('dragenter', function (e) {
    $(e.target).addClass('hover')
  });


  var fuzzyFunc = null;
  var fuzzy = 0.0;

  // Initialize the jQuery File Upload plugin
  $('#upload').fileupload({

    // This element will accept file drag/drop uploading
    dropZone: $('#drop'),

    // This function is called when a file is added to the queue;
    // either via the browse button, or via drag/drop:
    add: function (e, data) {
      $("#drop").removeClass('hover')
      $("#drop .message").empty().append('<strong>Awesome! Uploading new release</strong>');

      // Append the file name and file size
      console.log(data.files[0].name);
      console.log(data.files[0].size);

      // Initialize the knob plugin
      $('#knob').show().knob();

      // Automatically upload the file once it is added to the queue
      var jqXHR = data.submit();

      $('#upload').fileupload('disable');
    },

    progress: function(e, data){
      // Calculate the completion percentage of the upload
      var progress = parseInt(data.loaded / data.total * 100, 10);

      console.log(progress);

      // Update the hidden input field and trigger a change
      // so that the jQuery knob plugin knows to update the dial
      if (progress >= 95 && fuzzyFunc == null) {
        fuzzyFunc = setInterval(function() {
          fuzzy = fuzzy + 0.2;
          $('#knob').val(Math.min(50 + fuzzy, 98)).change();
        }, 500);
      }

      $('#knob').val(Math.min(progress / 2) + fuzzy, 98).change();

      if (progress == 100){
        clearInterval(fuzzyFunc);
        $('#knob').val(progress).change();
        $("#drop .message").empty().append("<strong>All Done! We're doing some extra work to get your release ready");
        
        // TODO: Create redirect
        setInterval(function() {
          window.location.href = $('#id_next').val();
        }, 500);
      }
    },

    fail:function(e, data){
      // Something has gone wrong!
      $("#drop .message").empty().append('<strong class="error">Uh oh, something went wrong. Refresh and try again. :(</strong>');
    }

  });

  // Prevent the default action when a file is dropped on the window
  $(document).on('drop dragover', function (e) {
    e.preventDefault();
  });

  // Helper function that formats the file sizes
  function formatFileSize(bytes) {
    if (typeof bytes !== 'number') {
      return '';
    }

    if (bytes >= 1000000000) {
      return (bytes / 1000000000).toFixed(2) + ' GB';
    }

    if (bytes >= 1000000) {
      return (bytes / 1000000).toFixed(2) + ' MB';
    }

    return (bytes / 1000).toFixed(2) + ' KB';
  }

});
