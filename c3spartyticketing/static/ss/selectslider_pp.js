$(function() {
    var select = $( "#donation_choice_pp" );
    var theslider = $( "#slider-div-donation_choice_pp" ).slider({
        range: "max",
        min: 1,
        max: 10,
        value: 1,
        slide: function( event, ui ) {
            //alert('sider alert!');
            select[ 0 ].selectedIndex = ui.value - 1;
            //$( "#donation_choice_pp" ).val( this.selectedIndex );
        }
    });
    $( "#donation_choice_pp" ).change(function() {     // if SELECT is changed...
        //alert('select was changed');
        theslider.slider( "value", this.selectedIndex + 1 );
    });
});
