odoo.define('my_table_extension.resource_page', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;
var rpc = require('web.rpc');

$(document).ready(function() {
    $('#multi-select-feature,#multi-select-cuisine,#multi-select-tag,#multi-select-lounge,#multi-select-categories').multiselect();

    var $input_elements = $('form#form_data').find('input');
    var $select_elements = $('form#form_data').closest('select');
    var $multi_select = $('.multi-select').find('button.multiselect');

    $.each($select_elements, function( index, select ) {
        if (!select.hasAttribute("disabled")){
            select.setAttribute("disabled", true);
        }
    });
    $.each($multi_select, function( index, multi ) {
        if (!multi.hasAttribute("disabled")){
            multi.setAttribute("disabled", true);
            $("button.multiselect").addClass("disabled");
       }
    });

    $(".btn-edit").click(function() {
        $(".btn-save").removeClass("d-none") //display save and cancel button
        $(".btn-cancel").removeClass("d-none")
        $(".oe_edit_only").removeClass("d-none")
        $(".btn-edit").addClass("d-none")
        $(".btn-request").addClass("d-none")
        $(".oe_readonly").addClass("d-none")

        $.each($input_elements, function( index, input ) {
            input.removeAttribute("readonly");
        });

        $.each($select_elements, function( index, select ) {
            select.removeAttribute("disabled");
        });

        $.each($multi_select, function( index, multi ) {
            multi.removeAttribute("disabled");
            $("button.multiselect").removeClass("disabled");
        });
    });

    $(".btn-cancel").click(function() {
        location.reload(true);
    });

    $('.img-wrap .oe_delete').on('click', function() {
        if (!confirm("Do you want to delete")){
          return false;
        }
        var id = $(this).closest('.img-wrap').find('img').data('id');
        var name = $(this).closest('.img-wrap').find('img').data('name');
        var delete_ids = []
        delete_ids.push($("#delete_images").val());
        delete_ids.push(id);
        $("#delete_images").val(delete_ids);
        $(this).closest('.img-wrap').addClass('d-none');
    });
    $('.btn-request').on('click', function(e) {
        var $btn = $(this);
        $btn.prop('disabled', true);
        rpc.query({
                model: 'business.resource',
                method: 'action_request_to_publish',
                args: [[parseInt(e.currentTarget.getAttribute('id'))]]
            })
            .then(function(result){
                if(result == 'success'){
                    var $message = "Your request is successful. Will get back to you soon."
                    $('.fill_field_error').find('.container').text($message);
                    $('.fill_field_error').addClass('alert-success');
                    $('.fill_field_error').addClass('show');
                }
                else{
                    var $message = "Please fill the data for "+ result;
                    $('.fill_field_error').find('.container').text($message);
                    $('.fill_field_error').addClass('alert-danger');
                    $('.fill_field_error').addClass('show');

                }
            }).always(function() {
                $btn.prop('disabled', false);
            });
        return false;

    });
    $('div#v-pills-tab a.nav-link').on('click', function(e) {
        $('#v-pills-messages-all').removeClass('show');
        $('#v-pills-messages-all').removeClass('active');
        $('a#v-pills-messages-all-tab').removeClass('active');
        $('a#v-pills-messages-all-tab').attr('aria-selected', 'false');
        var messages_all = $('a#v-pills-messages-all-tab').attr('aria-selected');
        var messages = $('a#v-pills-messages-tab').attr('aria-selected');
        if (messages_all == 'false' && messages == 'true'){
            $('#v-pills-messages').addClass('show');
            $('#v-pills-messages').addClass('active');
        }
    });

    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#imgPreview').attr('src', e.target.result);
            }

            reader.readAsDataURL(input.files[0]);
        }
    }

    $("#imgInput").change(function(){
        readURL(this);
    });

    $('#add-button').on('click', function(e) {
        $('#product_popup')[0].reset();
        $("#form-wrapper").css('display',"block");
        $("#form-div").css('display', "block");
        $('#product_id').val('');
    });

    $('.edit-action').on('click', function(e) {
        $("#form-wrapper").css('display',"block");
        $("#form-div").css('display', "block");
        var $product = $(this).attr('data-product');
        $('#product_id').val($product);
        $('#product_name').val($(this).attr('data-name'));
        $('#product_description').val($(this).attr('data-description'));
        $('#product_price').val($(this).attr('data-price'));
        $('#category').val($(this).attr('data-categ'));
    });

    $('#close-form,#form-wrapper').on('click', function(e) {
        $("#form-wrapper").css('display',"none");
        $("#form-div").css('display', "none");
    });

    // Cancel appointment button
    var deleteBtn = $(".delete-action");
    if (deleteBtn && deleteBtn.length > 0) {
        deleteBtn.on("click", function (event) {
            var isConfirmed = confirm(_t("Are you sure you want to cancel this appointment?"))
            if (isConfirmed) {
                var resourceID = parseInt($(this).attr('data-resource'));
                var productID = parseInt($(this).attr('data-product'));
                rpc.query({
                    model: "business.resource",
                    method: "write",
                    args: [[resourceID], {'suggested_product_ids': [[3, productID]]}]
                }).then(function (res) {
                    window.location.reload()
                });
            };
        });
    };

    $("#form_data #search").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#form_data #t01.table-body tr").filter(function() {
          $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });


    /*Subscription Dashboard*/

    $(".month_selection").on('change', function(event) {
        var month = $('.month_selection').val();
        var year = $('.year').val();
        rpc.query({
                model: 'business.resource',
                method: 'compute_resource_appointment_details',
                args: [1, month, year]
            })
            .then(function (results){
                $('#monthly_appointment').html(results['monthly_appointment']);
                $('#pre_order_appointment').html(results['pre_order_appointment']);
                $('#normal_appointment').html(results['normal_appointment']);
                $('#subscription_amount').html(results['subscription_amount']);
            });
    });

});
});