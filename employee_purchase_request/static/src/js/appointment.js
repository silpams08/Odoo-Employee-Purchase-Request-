odoo.define('my_table_extension.appointment', function (require) {
"use strict";
    var rpc = require('web.rpc');
    var session = require('web.session');
    $(document).ready(function() {

        $("#search_reservation").on("keyup", function() {
            var value = $(this).val().toLowerCase();
            $("#reservation-list #t01.table-body tr").filter(function() {
              $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });

        $('.datepicker').datepicker({
            clearBtn: true,
            todayBtn: 'linked',
            format: "mm/dd/yyyy",
            autoclose: true,
            todayHighlight: true,
        });

        $("#order_filter").on("click", "a", function(e){
            e.preventDefault();
            $('#order_filter > li > a').removeClass('selected');
            $(this).addClass('selected');
            var $this = $(this).parent();
            var selectedFilter = $this.data("value");
            if(selectedFilter == 'All'){
                $("#reservation-list #t01.table-body tr").filter(function() {
                  $(this).toggle($(this).text().indexOf(selectedFilter) == -1)
                });
            }
            else{
                $("#reservation-list #t01.table-body tr").filter(function() {
                  $(this).toggle($(this).text().indexOf(selectedFilter) > -1)
                });
            }
        });


        /*var $input_elements = $('#appointment_form').find('#form_data').find('input[type=text],input[type=email]');
        $.each($input_elements, function( index, input ) {
            input.setAttribute("readonly", "true");
        });*/
        $("#searchCustomer").on("keyup", function() {
            var value = $(this).val().toLowerCase();
            $("#customer_table_select tr").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });

        $(".partner").click(function() {
            var input_class = ['partner_id', 'name', 'email', 'mobile', 'street', 'city', 'state_id', 'country_id'];
            var data = {};
            var $row = $(this).closest("tr"); // Find the row
            $.each(input_class, function( index, value ) {
                if (value == 'mobile'){
                    data[value] = "+974".concat($row.find('.'+ value).text());
                }
                else{
                    data[value] = $row.find('.'+ value).text();
                }
            });
            $.each(data, function( key, value ) {
                $('#form_data').find('#'+key).val(value);
            });
        });

        // confirm appointment button
        var confirmBtn = $(".confirm_appointment");
        if (confirmBtn && confirmBtn.length > 0) {
            confirmBtn.on("click", function (event) {
                var appointmentID = parseInt(event.currentTarget.id);
                rpc.query({
                    model: "business.appointment",
                    method: "action_portal_confirm_reservation",
                    args: [[appointmentID]],
                }).then(function (res) {
                    window.location.reload()
                });
            });
        };
        // Done appointment button
        var doneBtn = $(".done_appointment");
        if (doneBtn && doneBtn.length > 0) {
            doneBtn.on("click", function (event) {
                var appointmentID = parseInt(event.currentTarget.id);
                rpc.query({
                    model: "business.appointment",
                    method: "action_portal_done_reservation",
                    args: [[appointmentID]],
                }).then(function (res) {
                    window.location.reload()
                });
            });
        };
    });
});