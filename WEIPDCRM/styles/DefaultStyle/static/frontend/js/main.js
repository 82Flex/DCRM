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

function show_search() {
    $("#search-form").show();
    $("#search-input").show();
    $("#icon").attr("onclick", "do_search()");
    $(".links").hide();
}

function do_search() {
    var input = $("#search-input").val();
    if (input == "" || input == "null" || input == "NULL") {
        $("#search-input").hide();
        $("#icon").attr("onclick", "show_search()");
        $(".links").show();
    } else {
        $("#search-form").submit();
    }
}
