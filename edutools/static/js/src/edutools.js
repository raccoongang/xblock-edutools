/* Javascript for EduToolsXBlock. */
function EduToolsXBlock(runtime, element) {
    var setResultUrl = runtime.handlerUrl(element, 'set_edutools_result');
    $(function ($) {
        var $elem = $(element);
        var $notification = $elem.find('.notification-submit');
        var $icon = $notification.find('.icon');
        var $submit = $elem.find('button.submit');

        $elem.find('#result-form').submit(function(e) {
            e.preventDefault();
            var $input = $(e.target).find('input#result');

            if ($input.val()) {
                $notification.addClass('hidden');
                $submit.attr('disabled', true);
                $.ajax({
                    url: setResultUrl,
                    type: 'POST',
                    dataType: 'json',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        result: $input.val()
                    }),
                    success: function(data) {
                        $notification.find('.notification-message').html(data.msg);

                        if (data.success) {
                            $notification.removeClass('error');
                            $notification.addClass('success');
                            $icon.removeClass('fa-close');
                            $icon.addClass('fa-check');
                        } else {
                            $notification.removeClass('success');
                            $notification.addClass('error');
                            $icon.removeClass('fa-check');
                            $icon.addClass('fa-close');
                        }
                        $notification.removeClass('hidden');
                        $submit.attr('disabled', false);
                    }
                });
            }
        });
    });
}
