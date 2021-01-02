$(window).load(function() {
    var content_height = 30 + $("#left_box").height();
    $("main").height(content_height * 2);
    console.log(content_height);
});