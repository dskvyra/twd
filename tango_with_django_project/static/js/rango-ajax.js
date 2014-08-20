$(document).ready(function() {

    $('#likes').click(function(){
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like_category', {category_id: catid}, function(data){
            $('#like_count').html(data);
            $('#likes').hide();
        });
    });

    $('#suggestion').keyup(function(){
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
            $('#cats').html(data);
        });
    });

    $('.rango-add').click(function() {
        var data_cat_id, data_title, data_url;
        data_cat_id = $(this).attr("data-catid");
        data_title = $(this).attr("data-title");
        data_url = $(this).attr("data-url");
        $.get('/rango/auto_add_page/', {category_id: data_cat_id, title: data_title, url: data_url}, function(data){
            $('#pages').html(data);
        });
    });
});