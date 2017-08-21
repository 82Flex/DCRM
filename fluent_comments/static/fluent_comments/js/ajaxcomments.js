(function($)
{
    var scrollElement = 'html, body';
    var active_input = '';

    // Settings
    var COMMENT_SCROLL_TOP_OFFSET = 40;
    var PREVIEW_SCROLL_TOP_OFFSET = 20;
    var ENABLE_COMMENT_SCROLL = true;


    if($ == null) {
        throw Error("jQuery needs to be loaded before ajaxcomments.js");
    }

    $(document).ready(function()
    {
        var commentform = $('form.js-comments-form');
        if( commentform.length > 0 )
        {
            // Detect last active input.
            // Submit if return is hit, or any button other then preview is hit.
            commentform.find(':input').focus(setActiveInput).mousedown(setActiveInput);
            commentform.submit(onCommentFormSubmit);
        }


        // Bind events for threaded comment reply
        if($.fn.on) {
            // jQuery 1.7+
            $('body').on('click', '.comment-reply-link', showThreadedReplyForm);
        }
        else {
            $('.comment-reply-link').live('click', showThreadedReplyForm);
        }

        $('.comment-cancel-reply-link').click(cancelThreadedReplyForm);

        var $all_forms = $('.js-comments-form');
        $all_forms
          .each(function(){
            var $form = $(this);
            var object_id = $form.attr('data-object-id');  // Supported in all jQuery versions.
            $form.wrap('<div class="js-comments-form-orig-position" id="comments-form-orig-position-' + object_id + '"></div>');
          });

        // HACK HACK HACK
        // Restore the parent-id when the server is unable to do so.
        // See if the comment-form can be found near to the current list of comments.
        var $all_comment_divs = $("#comments");
        var $all_broken_comment_divs = $("#comments-None");
        $all_broken_comment_divs.each(function(){
            var node = this.parentNode;
            for(var i = 0; i < 4; i++) {
                var $form = $(node).find('.js-comments-form');
                if($form.length) {
                    var target_object_id = $form.attr('data-object-id');
                    if(target_object_id) {
                        $(this).attr('id', 'comments-' + target_object_id).attr('data-object-id', target_object_id);
                    }
                    break;
                }

                node = node.parentNode;
                if(! node) break;
            }
        });

        // Find the element to use for scrolling.
        // This code is much shorter then jQuery.scrollTo()
        $('html, body').each(function()
        {
            // See which tag updates the scrollTop attribute
            var $rootEl = $(this);
            var initScrollTop = $rootEl.attr('scrollTop');
            $rootEl.attr('scrollTop', initScrollTop + 1);
            if( $rootEl.attr('scrollTop') == initScrollTop + 1 )
            {
                scrollElement = this.nodeName.toLowerCase();
                $rootEl.attr('scrollTop', initScrollTop);  // Firefox 2 reset
                return false;
            }
        });


        // On load, scroll to proper comment.
        var hash = window.location.hash;
        if( hash.substring(0, 2) == "#c" )
        {
            var id = parseInt(hash.substring(2));
            if( ! isNaN(id))   // e.g. #comments in URL
                scrollToComment(id, 1000);
        }
    });


    function setActiveInput()
    {
        active_input = this.name;
    }


    function onCommentFormSubmit(event)
    {
        event.preventDefault();  // only after ajax call worked.
        var form = event.target;
        var preview = (active_input == 'preview');

        ajaxComment(form, {
            onsuccess: (preview ? null : onCommentPosted),
            preview: preview
        });
        return false;
    }


    function scrollToComment(id, speed)
    {
        if( ! ENABLE_COMMENT_SCROLL ) {
            return;
        }

        // Allow initialisation before scrolling.
        var $comment = $("#c" + id);
        if( $comment.length == 0 ) {
            if( window.console ) console.warn("scrollToComment() - #c" + id + " not found.");
            return;
        }

        if( window.on_scroll_to_comment && window.on_scroll_to_comment({comment: $comment}) === false )
            return;

        // Scroll to the comment.
        scrollToElement( $comment, speed, COMMENT_SCROLL_TOP_OFFSET );
    }


    function scrollToElement( $element, speed, offset )
    {
        if( ! ENABLE_COMMENT_SCROLL ) {
            return;
        }

        if( $element.length )
            $(scrollElement).animate( {scrollTop: $element.offset().top - (offset || 0) }, speed || 1000 );
    }


    function onCommentPosted( comment_id, object_id, is_moderated, $comment )
    {
        var $message_span;
        if( is_moderated )
            $message_span = $("#comment-moderated-message-" + object_id).fadeIn(200);
        else
            $message_span = $("#comment-added-message-" + object_id).fadeIn(200);

        setTimeout(function(){ scrollToComment(comment_id, 1000); }, 1000);
        setTimeout(function(){ $message_span.fadeOut(500) }, 4000);
    }


    function showThreadedReplyForm(event) {
        event.preventDefault();

        var $a = $(this);
        var comment_id = $a.attr('data-comment-id');
        var $comment = $a.closest('.comment-item');
        var at = $($a.parent()).find("p").text();

        removeThreadedPreview();
        $('.js-comments-form').appendTo($comment);
        $($comment.find('#id_parent')[0]).val(comment_id);
        $($comment.find('#id_comment')[0]).val('@'+at+' ');
        $($comment.find('.emoji-wysiwyg-editor')[0]).html('@'+at);
    }


    function cancelThreadedReplyForm(event) {
        if(event)
            event.preventDefault();

        var $form = $(event.target).closest('form.js-comments-form');
        resetForm($form);
        removeThreadedPreview();
    }

    function removeThreadedPreview() {
        // And remove the preview (everywhere! on all comments)
        var $previewLi = $('li.comment-preview');
        if($previewLi.length == 0)
            return false;

        var $ul = $previewLi.parent();
        if($ul.children('li').length == 1)
            $ul.remove();  // the preview was the only node.
        else
            $previewLi.remove();

        return true
    }

    function resetForm($form) {
        var object_id = $form.attr('data-object-id');
        $($form[0].elements['comment']).val('');  // Wrapped in jQuery to silence errors for missing elements.
        $($form[0].elements['parent']).val('');   // Reset parent field in case threaded comments are used.
        $("textarea[name='comment']").val();
        $('.emoji-wysiwyg-editor').html('');
        $form.appendTo($('#comments-form-orig-position-' + object_id));
    }


    /*
      Based on django-ajaxcomments, BSD licensed.
      Copyright (c) 2009 Brandon Konkle and individual contributors.

      Updated to be more generic, more fancy, and usable with different templates.
     */
    var previewAutoAdded = false;

    function ajaxComment(form, args)
    {
        var onsuccess = args.onsuccess;
        var preview = !!args.preview;

        if (form.commentBusy) {
            return false;
        }

        form.commentBusy = true;
        var $form = $(form);
        var comment = $form.serialize() + (preview ? '&preview=1' : '');
        var url = $form.attr('action') || './';
        var ajaxurl = $form.attr('data-ajax-action');

        // Add a wait animation
        if( ! preview )
            $('#comment-waiting').fadeIn(1000);

        // Use AJAX to post the comment.
        $.ajax({
            type: 'POST',
            url: ajaxurl || url,
            data: comment,
            dataType: 'json',
            success: function(data) {
                form.commentBusy = false;
                removeWaitAnimation($form);
                removeErrors($form);

                if (data.success) {
                    var $added;
                    if( preview )
                        $added = commentPreview(data);
                    else
                        $added = commentSuccess($form, data);

                    if( onsuccess )
                        args.onsuccess(data.comment_id, data.object_id, data.is_moderated, $added);
                }
                else {
                    commentFailure(data);
                }
            },
            error: function(xhr, textStatus, ex) {
                form.commentBusy = false;
                removeWaitAnimation($form);

                response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to post comment data!");    // can't yet rely on $.ajaxError

                // Submit as non-ajax instead
                //$form.unbind('submit').submit();
            }
        });

        return false;
    }

    function commentSuccess($form, data)
    {
        // Clean form
        resetForm($form);

        // Show comment
        var had_preview = removePreview(data);
        var $new_comment = addComment(data);

        if( had_preview )
            // Avoid double jump when preview was removed. Instead refade to final comment.
            $new_comment.hide().fadeIn(600);
        else
            // Smooth introduction to the new comment.
            $new_comment.hide().show(600);

        return $new_comment;
    }

    function addComment(data)
    {
        // data contains the server-side response.
        var $newCommentTarget = addCommentWrapper(data, '')
        $newCommentTarget.append(data['html']).removeClass('empty');
        return $("#c" + data.comment_id);
    }

    function addCommentWrapper(data, for_preview)
    {
        var parent_id = data['parent_id'];
        var object_id = data['object_id'];
        var $parent;
        if(parent_id) {
            $parent = $($("#c" + parseInt(parent_id)).parent()).parent('li.comment-wrapper');
        }
        else {
            $parent = getCommentsDiv(object_id);
        }

        if(data['use_threadedcomments']) {
            // Each top-level of django-threadedcomments starts in a new <ul>
            // when you use the comment.open / comment.close logic as prescribed.
            var $commentUl = $parent.children('ul');
            if( $commentUl.length == 0 ) {
                var $form = $parent.children('.js-comments-form');
                if($form.length > 0) {
                    // Make sure to insert the <ul> before the comment form.
                    $form.before('<ul class="comment-list-wrapper"></ul>')
                    $commentUl = $parent.children('ul');
                }
                else {
                    $parent.append('<ul class="comment-list-wrapper"></ul>');
                    $commentUl = $parent.children('ul:last');
                }
            } else {
                if (!parent_id) {
                    $parent.append('<ul class="comment-list-wrapper"></ul>');
                    $commentUl = $parent.children('ul:last');
                }
            }

            if(for_preview) {
              // Reuse existing one if found. This is used for the preview.
              var $previewLi = $commentUl.find('li.comment-preview');
              if($previewLi.length == 0) {
                  $commentUl.append('<li class="comment-wrapper comment-preview"></li>');
                  $previewLi = $commentUl.find('li.comment-preview');
              }
              return $previewLi;
            }
            else {
                // Just add a new one!
                $commentUl.append('<li class="comment-wrapper"></li>');
                return $commentUl.children('li:last');
            }
        }
        else {
            return $parent;
        }
    }

    function commentPreview(data)
    {
        var object_id = data['object_id'];
        var parent_id = data['parent_id'];
        var $comments = getCommentsDiv(object_id);

        if(data['use_threadedcomments']) {
            var $newCommentTarget = addCommentWrapper(data, true);
            $previewarea = $newCommentTarget;
        }
        else {
            // Allow to explicitly define in the HTML (for regular comments only)
            var $previewarea = $comments.find(".comment-preview-area");

            if( $previewarea.length == 0 ) {
                // For regular comments, if previewarea is not explicitly added to the HTML,
                // include a previewarea in the comments. This should at least give the same markup.
                $comments.append('<div class="comment-preview-area"></div>').addClass('has-preview');
                $previewarea = $comments.children(".comment-preview-area");
                previewAutoAdded = true;
            }
        }

        var had_preview = $previewarea.hasClass('has-preview-loaded');
        $previewarea.html('<div class="comment-preview">' + data.html + '</div>').addClass('has-preview-loaded');
        if( ! had_preview )
            $previewarea.hide().show(600);

        // Scroll to preview, but allow time to render it.
        setTimeout(function(){ scrollToElement( $previewarea, 500, PREVIEW_SCROLL_TOP_OFFSET ); }, 500);
    }

    function commentFailure(data)
    {
        var form = $('form#comment-form-' + data.object_id)[0];

        // Show mew errors
        for (var field_name in data.errors) {
            if(field_name) {
                var $field = $(form.elements[field_name]);

                // Twitter bootstrap style
                $field.after('<span class="js-errors">' + data.errors[field_name] + '</span>');
                $field.closest('.control-group').addClass('error');  // Bootstrap 2
                $field.closest('.form-group').addClass('has-error'); // Bootstrap 3
            }
        }
    }

    function removeErrors($form)
    {
        $form.find('.js-errors').remove();
        $form.find('.control-group.error').removeClass('error');  // Bootstrap 2
        $form.find('.form-group.has-error').removeClass('has-error');  // Bootstrap 3
    }

    function getCommentsDiv(object_id)
    {
        var selector = "#comments-" + object_id;
        var $comments = $(selector);
        if( $comments.length == 0 )
            alert("Internal error - unable to display comment.\n\nreason: container " + selector + " is missing in the page.");
        return $comments;
    }

    function removePreview(data)
    {
        var object_id = data['object_id'];
        var $comments_list = $('#comments-' + object_id);

        if(data['use_threadedcomments']) {
            return removeThreadedPreview();
        }
        else {
            var $previewarea = $comments_list.find(".comment-preview-area");
            var had_preview = $previewarea.hasClass('has-preview-loaded');

            if( previewAutoAdded )
                $previewarea.remove();  // make sure it's added at the end again later.
            else
                $previewarea.html('');

            // Update classes. allowing CSS to add/remove margins for example.
            $previewarea.removeClass('has-preview-loaded');
            $comments_list.removeClass('has-preview');

            return had_preview;
        }
    }

    function removeWaitAnimation($form)
    {
        // Remove the wait animation and message
        $form.find('.comment-waiting').hide().stop();
    }

})(window.jQuery);
