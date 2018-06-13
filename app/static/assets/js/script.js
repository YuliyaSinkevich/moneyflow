$(document).ready(function () {
    $("#main-top-navbar").on("click", "a", function (event) {
        event.preventDefault();
        var id = $(this).attr('href'),
            top = $(id).offset().top;
        $('body,html').animate({scrollTop: top}, 500);
    });

    $(".dropdown-menu li a").click(function () {
        $(this).parents(".dropdown").find('.btn').html($(this).text());
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
    });
});

