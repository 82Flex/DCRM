/*
DCRM - Darwin Cydia Repository Manager
Copyright (C) 2017  WU Zheng <i.82@me.com> & 0xJacky <jacky-943572677@qq.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
$(function() {
    $(".search-btn").click(function() {
        var $input =  $(".search-input");
        if ($(".search").hasClass("active")) {
            var value = $(".search-input").val();
            if (value == "" || value == "null" || value == "NULL") {
                $(".search").removeClass("active");
                $input.hide();
                $(".links").show();
            } else {
                $("#search-form").submit();
            }
        } else {
            $("#search-form").show();
            $input.show();
            $(".search").addClass("active");
            $(".links").hide();
        }
    });
});