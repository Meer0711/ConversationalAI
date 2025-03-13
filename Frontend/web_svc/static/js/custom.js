function submitForm($this) {
    $("#id_processing").show();
    let formId = $this.attr("id");
    let reload = $this.data("reload");
    var formData = new FormData($("#"+formId)[0]);
    $.ajax({
        url: $this.attr("action"),
        type: $this.attr("method"),
        processData: false,
        contentType: false,
        data: formData,
        success: function(response) {
            $("#id_processing").hide();
            if (reload){
                location.reload();
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#id_processing").hide();
            let errorResponse = XMLHttpRequest.responseJSON.detail;
            swal(errorResponse, {icon: "error"});
        }
    });
    return false;
};