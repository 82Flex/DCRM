/* Cytyle - iOS Interface Cascading Style Sheet
 * Copyright (C) 2007-2013  Jay Freeman (saurik)
*/

(function() {
    var uncytyle = function(e, d) {
        e.className = e.className.replace(new RegExp('(\\s|^)' + d + '(\\s|$)'), ' ');
    };

    var find = function(e) {
        for (var item = e.target; item != null && item.nodeName != 'A'; item = item.parentNode);
        if (item != null && item.href == '')
            return null;
        return item;
    };

    if ('ontouchstart' in document.documentElement) {
        document.addEventListener('DOMContentLoaded', function() {
            FastClick.attach(document.body);

            document.addEventListener('click', function(e) {
                var item = find(e);
                if (item == null)
                    return;

                if (typeof cydia != 'undefined')
                    if (item.href.substr(0, 32) == 'http://cydia.saurik.com/package/')
                        item.href = 'cydia://package/' + item.href.substr(32);

                item.className += ' cytyle-dn';
                uncytyle(item, 'cytyle-in');
            });
        }, false);

        var timeout = null;
        var clear = function() {
            if (timeout == null)
                return;
            clearTimeout(timeout);
            timeout = null;
        };

        document.addEventListener('touchstart', function(e) {
            var item = find(e);
            if (item == null)
                return;

            uncytyle(item, 'cytyle-up');
            timeout = setTimeout(function() {
                if (timeout != null)
                    item.className += ' cytyle-in';
            }, 50);
        });

        var stop = function(e) {
            var item = find(e);
            if (item == null)
                return;

            clear();
            uncytyle(item, 'cytyle-in');
        };

        document.addEventListener('touchmove', stop);
        document.addEventListener('touchend', stop);
    } else {
        document.addEventListener('click', function(e) {
            var item = find(e);
            if (item == null)
                return;
            item.className += ' cytyle-dn';
            uncytyle(item, 'cytyle-in');
        });

        document.addEventListener('mousedown', function(e) {
            var item = find(e);
            if (item == null)
                return;

            uncytyle(item, 'cytyle-up');
            item.className += ' cytyle-in';
        });

        var stop = function(e) {
            var item = find(e);
            if (item == null)
                return;

            uncytyle(item, 'cytyle-in');
        };

        document.addEventListener('mousemove', stop);
        document.addEventListener('mouseup', stop);
    }

    var wipe = function(e) {
        var items = document.getElementsByClassName('cytyle-dn');
        for (var i = items.length, e = 0; i != e; --i) {
            var item = items.item(i - 1);
            uncytyle(item, 'cytyle-in');
            item.className += ' cytyle-up';
            uncytyle(item, 'cytyle-dn');
        }
    };

    var page = function(e) {
        window.removeEventListener('pageshow', page);
        window.addEventListener('pageshow', wipe);
    };

    if (typeof cydia != 'undefined')
        document.addEventListener("CydiaViewWillAppear", wipe);
    else if (typeof window.onpageshow != 'undefined')
        window.addEventListener('pageshow', page);
})();

if (navigator.userAgent.search(/Cydia/) == -1)
    document.write('<base target="_top"/>');
else {
    document.write('<style type="text/css"> body.pinstripe { background: none !important; } </style>');
    document.write('<base target="_blank"/>');
}

// XXX: this might just fail on Chrome everywhere, even Mac :(
// https://code.google.com/p/chromium/issues/detail?id=168646
if (navigator.userAgent.search(/Linux/) != -1)
    document.write('<style type="text/css"> p { text-rendering: optimizeSpeed !important; } </style>');

(function() {
    var cytyle = window.location.search;
    cytyle = cytyle.match(/^\?cytyle=(.*)$/);

    if (cytyle != null)
        cytyle = ' cytyle-' + cytyle[1];
    else {
        cytyle = navigator.userAgent;
        cytyle = cytyle.match(/.*; CPU (?:iPhone )?OS ([0-9_]*) like Mac OS X[;)]/);
        cytyle = cytyle == null ? '7.0' : cytyle[1].replace(/_/g, '.');
        cytyle = parseInt(cytyle);
        cytyle = cytyle >= 7 ? ' cytyle-flat' : ' cytyle-faux';
    }

    var body = document.documentElement;
    body.className += cytyle;

    if (window.devicePixelRatio && devicePixelRatio >= 2) {
        var test = document.createElement('div');
        test.style.border = '.5px solid transparent';
        body.appendChild(test);
        if (test.offsetHeight == 1)
            body.className += ' cytyle-hair';
        body.removeChild(test);
    }
})();

(function() {
    var update = function() {
        if (window.parent != window)
            parent.postMessage({cytyle: {name: "iframe-y", value: document.body.scrollHeight}}, "*");
    };

    window.addEventListener('message', function(event) {
        var message = event.data.cytyle;
        if (message == undefined)
            return;

        switch (message.name) {
            case "iframe-y":
                var height = message.value;
                var iframes = document.getElementsByTagName("iframe");
                if (iframes.length != 1)
                    return;
                var iframe = iframes.item(0);
                iframe.style.height = height + 'px';
                update();
            break;
        }
    }, false);

    window.addEventListener('load', update, false);
})();

(function() {
    var text = document.createElement("span");
    text.appendChild(document.createTextNode("My"));

    var block = document.createElement("div");
    block.style.display = "inline-block";
    block.style.height = "0px";
    block.style.width = "1px";

    var div = document.createElement("div");
    div.id = 'cytyle-metric';
    div.style.lineHeight = "normal";

    div.appendChild(text);
    div.appendChild(block);

    var body = document.documentElement;
    body.appendChild(div); try {
        var full = text.offsetHeight;

        var style = div.currentStyle;
        if (typeof style == 'undefined')
            style = window.getComputedStyle(div, null);
        var font = parseInt(style.fontSize);

        block.style.verticalAlign = "baseline";
        var base = block.offsetTop - text.offsetTop;
        // XXX: on iOS 3 I am unable to do this?
        if (base == 0)
            base = 14;
    } finally {
        body.removeChild(div);
    }

    var top = base - font * 0.75;

    //var down = (font - base) / font / 2;
    //alert(down + "em = (" + font + " - " + base + ") / " + font + " / 2");
    var down = ((full - (base - top)) / 2 - top) / font;
    //alert(down + "em = ((" + full + " - (" + base + " - " + top + ")) / 2 - " + top + ") / " + font);

    //var over = 4.0; // Modern
    //var over = 2.5; // Legacy
    //var over = 3.5; // Chrome
    //var over = 3.0; // Medium
    //var desc = font * 0.25;
    //var down = (desc - over) / font;

    document.write('<style type="text/css"> p, input[type="password"], input[type="text"], select { top: ' + down + 'em; } </style>');
})();
