odoo.define('employee_purchase_request.orders', function (require) {
"use strict";
    var rpc = require('web.rpc');
    var session = require('web.session');

    $(document).ready(function() {
//        $("#search_order").on("keyup", function() {
//            var value = $(this).val().toLowerCase();
//            $("#order_table tr#order").filter(function() {
//              $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
//            });
//        });

//        $("#order_filter").on("click", "a", function(e){
//            e.preventDefault();
//            $('#order_filter > li > a').removeClass('selected');
//            $(this).addClass('selected');
//            var $this = $(this).parent();
//            var selectedFilter = $this.data("value");
//            if(selectedFilter == 'All'){
//                $("#order_list #order_table.table-body tr").filter(function() {
//                  $(this).toggle($(this).text().indexOf(selectedFilter) == -1)
//                });
//            }
//            else{
//                $("#order_list #order_table.table-body tr").filter(function() {
//                  $(this).toggle($(this).text().indexOf(selectedFilter) > -1)
//                });
//            }
//        });

        $('.change-qty').on('click', function(ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $input = $("input#quantity");
            var limit = $('input#amount_to_buy').val();
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || limit);
            var previousQty = parseFloat($input.val() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;

            if (newQty !== previousQty) {
                $input.val(newQty).trigger('change');
            }
            return false;
        });

        $('input#quantity').on('change', function(ev){
            var tax = $('#tax_id');
            if (tax.val()) {
                if (!ev.isDefaultPrevented()) {
                    ev.preventDefault();
                    rpc.query({
                        model: 'res.currency',
                        method: "browse",
                        args: [
                            [parseInt($('#currency').val())], parseInt($('#currency').val())
                        ],
                    }).then(function (result) {
                        var currency = result;
                    });
                    rpc.query({
                        model: 'res.users',
                        method: "browse",
                        args: [
                            [session.uid], session.uid
                        ],
                    }).then(function (result) {
                        var user = result;
                    });
                    rpc.query({
                        model: 'account.tax',
                        method: "compute_all",
                        args: [
                            [parseInt(tax.val())],
                            parseFloat($('#price').val()), currency,
                            parseInt($('#quantity').val()), parseInt($('#product_template_id').val()),
                            user.partner_id
                        ],
                    }).then(function(taxes){
                            $('#amount_untaxed .oe_currency_value').text(taxes['total_excluded']);
                            var amount_tax = 0
                            $.each(taxes['taxes'], function( index, value ) {
                                amount_tax = amount_tax + value['amount'];
                            });
                            $('#amount_tax .oe_currency_value').text(amount_tax);
                            $('#amount_total .oe_currency_value').text(taxes['total_included']);
                    });
                }
            }
        });

        $('input.attrib').on('change', function(){
            if (!ev.isDefaultPrevented()) {
                ev.preventDefault();
                $(ev.currentTarget).closest("form").submit();
            }
        });


        $('#product_template_id').on('change input', function(ev){
            const productInp = $('#product_template_id')
            if (productInp.val()) {
                if (!ev.isDefaultPrevented()) {
                    ev.preventDefault();
                    $(ev.currentTarget).closest("form").submit();
                }
            }
        });

        $('.attrib').on('change input', function(ev){
            const productInp = $('.attrib')
            if (productInp.val()) {
                if (!ev.isDefaultPrevented()) {
                    ev.preventDefault();
                    $(ev.currentTarget).closest("form").submit();
                }
            }
        });

        $('#vendor_id').on('change input', function(ev){
            const productInp = $('#vendor_id')
            if (productInp.val()) {
                if (!ev.isDefaultPrevented()) {
                    ev.preventDefault();
                    $(ev.currentTarget).closest("form").submit();
                }
            }
        });

        let boxes = document.querySelectorAll(".box");
        Array.from(boxes, function(box) {
            box.addEventListener("click", function() {
                var $this = $(this)
                var vendor_id = $this.data('id');
                var vendor_price = $this.data('price');
                $('#vendor_id').val(vendor_id).trigger('change');
            });
        });

        $('#attachment').on('change input', function(ev){
           /* Attached file size check. Will Bontrager Software LLC, https://www.willmaster.com */
           var UploadFieldID = "attachment";
           var MaxSizeInBytes = 5242880;
           var fld = document.getElementById(UploadFieldID);
           if( fld.files && fld.files.length == 1 && fld.files[0].size > MaxSizeInBytes )
           {
              alert("The file size must be no more than " + parseInt(MaxSizeInBytes/1024/1024) + "MB");
              $('#attachment').val(null);
              return false;
           }
           return true;
       });

/*
        $("#button_submit").keydown(function(event) {
            event.preventDefault();
//            $('#submit_form').append('<input type="hidden" name="form_submit" value="true" /> ');
//            $('#submit_form').submit();
             $('#submit_form').trigger('submit', [{'form_submit': true}]);
//             $("#form_submit").val(true);
//             $("#submit_form").off("submit");
//             self.submit();
        });*/
//
        /*$("#submit_form").on("submit", function (e) {
            e.preventDefault();//stop submit event
            var self = $(this);//this form
            console.log(self);
            console.log(e);
            $("#submit_form").off("submit");//need form submit event off.
            self.submit();//submit form
        });*/


    });
});