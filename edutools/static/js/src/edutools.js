/* Javascript for EduToolsXBlock. */
function EduToolsXBlock(runtime, element) {
    var setResultUrl = runtime.handlerUrl(element, 'set_edutools_result');
    $(function ($) {
        $(element).find('#result-form').submit(function(e) {
            e.preventDefault();
            var input = $(e.target).find('input#result');

            if (input.val()) {
                $.ajax({
                    url: setResultUrl,
                    type: 'POST',
                    dataType: 'json',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        result: input.val()
                    }),
                    success: function(data) {
                        console.log(data);
                    }
                });
            }
        });
    });
}
