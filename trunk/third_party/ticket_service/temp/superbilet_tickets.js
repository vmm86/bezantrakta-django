// if(!("contains" in String.prototype))
//     String.prototype.contains = function(str, startIndex) { return -1 !== String.prototype.indexOf.call(this, str, startIndex); };

// Изменение состояния места (при клике на нём)
function changeState(event) {
    event.preventDefault();

    var place = $(this);
    var placeData = place.data("place");
    var placeClass = place.attr("class");
    var sector_id = placeData[0];
    var row = placeData[1];
    var seat = placeData[2];

    $.post("index.php?option=com_afisha&controller=event&task=ticketaction", {
        "event_id": event_id,
        "sector_id": sector_id,
        "row": row,
        "seat": seat,
        "action": action
    }, updateStates);
}

// Обновление вывода списка билетов в заказе
var countChosen = 0;
var totalSum = 0;

function updateBasket(sector_id, row, seat, action, price) {
    var sectorName = (sector_names[sector_id]) ? sector_names[sector_id] + " " : "";

    var id = "chosen-ticket-"+event_id+"-"+sector_id+"-"+row+"-"+seat;
    if (action == "select") {
        countChosen += 1;
        totalSum += price;
        $("#chosen-tickets").append("<li id=\"" + id + "\">" + sectorName + "ряд " + row + " место " + seat + " цена " + price + "</li>");
    } else if (action == 'free') {
        countChosen -= 1;
        totalSum -= price;
        $("#"+id).remove();
    }

    $("#count-chosen").html(countChosen);
    $("#total-sum").html(Math.round(totalSum*100)/100);

    if (countChosen == 0) {
        $("#overall-text, #buy-tickets").hide();
        $("#no-tickets, #no-overall, #buy-tickets-inactive").show();
    } else {
        $("#overall-text, #buy-tickets").show();
        $("#no-tickets, #no-overall, #buy-tickets-inactive").hide();
    }
}

// Обновление состояния всех мест и самого заказа (при инициализации зала или по клику на каком-либо месте)
function updateStates(data) {
    if (data) {
        // console.log('Data exists:', data);
        data = JSON.parse(data);
    } else {
        console.log('No data:', data);
        return;
    }

    if (data.states)
        // .stagehall изменено на #tickets, чтобы работали клики по добавляемым на лету схемам отдельных секторов в больших залах
        // Блок, к которому применяется .on(), НЕ должен генерироваться уже после загрузки страницы, будучи при этом родителем для вновь генерируемых элементов
        $("#tickets .seat").each(function(){
            var place = $(this);
            var placeData = place.data("place");
            var sector_id = placeData[0];
            var row = parseInt(placeData[1], 10);
            var seat = parseInt(placeData[2], 10);
            var _id = sector_id + "-" + row + "-" + seat;

            if (data.states[_id]) {
                var price = parseFloat(data.states[_id].price, 10);
                var color = parseInt(data.states[_id].color, 10);
                var state = data.states[_id].state;
                place.attr("class", "seat state" + state + " color" + color);
                if (state == "E")
                    place.removeAttr("title");
                else
                    place.attr("title", "ряд " + row + "\nместо " + seat + "\nцена " + price + "");
                updateBasket(sector_id, row, seat, data.action, price);
            } else
                if (data.action == "refresh") {
                    place.attr("class", "seat stateE");
                    place.removeAttr("title");
                }
        });

}
