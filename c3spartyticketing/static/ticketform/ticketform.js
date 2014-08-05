$(document).ready(function(){

  // hide/show representation
  if( !$('#ticket_gv-1').is(':checked') ) {
    $('#item-rep-type').closest('.panel-default').hide();
  }
  $('#ticket_gv-0, #ticket_gv-1, #ticket_gv-2').change(function() {
    if( $('#ticket_gv-1').is(':checked') ) {
      $('#item-rep-type').closest('.panel-default').show();
    } else {
      $('#item-rep-type').closest('.panel-default').hide();
    }
  })

  // hide/show tshirt
  if( !$('#ticket_tshirt').is(':checked') ) {
    $('#item-tshirt-type').closest('.panel-default').hide();
  }
  $('#ticket_tshirt').change(function() {
    if( $(this).is(':checked') ) {
      $('#item-tshirt-type').closest('.panel-default').show();
    } else {
      $('#item-tshirt-type').closest('.panel-default').hide();
    }
  })

  // bc: buffet only when attended
  if( !$('#ticket_bc-0').is(':checked') ) {
    $('#ticket_bc-1').prop('checked', false);
    $('#ticket_bc-1').prop('disabled', true);
  }
  $('#ticket_bc-0').change(function() {
    if( $(this).is(':checked') ) {
      $('#ticket_bc-1').prop('disabled', false);
    } else {
      $('#ticket_bc-1').prop('checked', false);
      $('#ticket_bc-1').prop('disabled', true);
    }
  })

  // all-inclusive
  $('#ticket_gv-0, #ticket_bc-0, #ticket_bc-1, #ticket_tshirt').closest('label').addClass('all-inclusive-emph')
  $('#item-ticket_bc, #item-ticket_gv, #item-ticket_tshirt').css('border', '0px solid transparent')
  $('#ticket_all').change(function() {
    if( $(this).is(':checked') ) {
      allinc_on()
    } else {
      allinc_off()
    }
  })
  if( $('#ticket_all').is(':checked') ) {
    $('#ticket_all').change()
  }
  $('#item-ticket_gv .ticket_types_input, '
    +'#item-ticket_bc .ticket_types_input, '
    +'#ticket_tshirt').change(function(){
    if( !$('#ticket_tshirt').is(':checked') 
      || !$('#ticket_bc-0').is(':checked')
      || !$('#ticket_bc-1').is(':checked')
      || !$('#ticket_gv-0').is(':checked') ) {
      $('#ticket_all').prop('checked', false);
      allinc_off()
    } else {
      $('#ticket_all').prop('checked', true);
      allinc_on()
    }
  })

  // enable fields on submit
  $('#deform').submit(function( event ) {
    $('input').prop('disabled', false);
  });

  function allinc_on(){
    $('#ticket_gv-0').prop('checked', true);
    $('#ticket_bc-0').prop('checked', true);
    $('#ticket_bc-1').prop('disabled', false)
    $('#ticket_bc-1').prop('checked', true);
    $('#ticket_tshirt').prop('checked', true);
    $('#item-ticket_bc, #item-ticket_gv, #item-ticket_tshirt').animate(
      { 
        'paddingLeft': 20, 
        'marginLeft': 10, 
        'borderLeftWidth': '3px', 
        'borderLeftColor': '#3276b1'
      }, 600, function() {}
    )
    $('.all-inclusive-hide').animate(
      { 'opacity': 0.4 }, 600, function() {}
    )
    $('#req-ticket_all, .all-inclusive-emph').animate(
      { 'color': '#3276b1' }, 600, function() {}
    )
    $('#ticket_all').prop('disabled', true)
    $('#item-tshirt-type').closest('.panel-default').show();
  }

  function allinc_off(){
    $('#item-ticket_bc, #item-ticket_gv, #item-ticket_tshirt').animate(
      { 
        'paddingLeft': 0, 
        'marginLeft': 0, 
        'borderLeftWidth': '0px',
        'borderLeftColor': 'transparent'
      }, 600, function() {}
    )
    $('.all-inclusive-hide').animate(
      { 'opacity': 1 }, 600, function() {}
    )
    $('#req-ticket_all, .all-inclusive-emph').animate(
      { 'color': '#333333' }, 600, function() {}
    )
    $('#ticket_all').prop('disabled', false)
    if( !$('#ticket_tshirt').is(':checked') ) {
      $('#item-tshirt-type').closest('.panel-default').hide();
    }
  }

})