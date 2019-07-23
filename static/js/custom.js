// preloader
// $(":button[type='submit']").click(function(){
//     $('.preloader').toggle(); // set duration in brackets
// });



// select multiple validation
function select_validation() {
    if ($(":selected").length < 2) {
        swal({text: "Select at least two proteins!", button: false});
        return false;
    } else {
        return true;
    }
}