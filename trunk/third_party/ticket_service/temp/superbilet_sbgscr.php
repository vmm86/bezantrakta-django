<?php
function clearPlace($event_id, $sector_id, $row, $seat) {
    $info = $sbgs->GetState(array(array('event_id' => $event_id, 'sector_id' => $sector_id, 'row' => $row, 'seat' => $seat)));
    $session = $info["$sector_id-$row-$seat"]['session'];
    $order_id = $info["$sector_id-$row-$seat"]['order_id'];
    return $sbgs->ClearReservation(array(array('event_id' => $event_id, 'sector_id' => $sector_id, 'row' => $row, 'seat' => $seat, 'session'=>$session, 'order_id' => $order_id)));
}

switch ($_REQUEST['action']) {
    case 'list-sectors':
        $event_id = int($_REQUEST['event_id']);
        $sectors = $sbgs->GetSectors($event_id);
        $data = array_values($sectors);
        $json = true;
        break;
    case 'list-reserve':
        $event_id = int($_REQUEST['event_id']);
        $sector_id = int($_REQUEST['sector_id']);
        $reservations = array_filter($sbgs->GetSectorState($event_id, $sector_id), function($a) {return $a['state'] == 'P';});
        $data = array_values($reservations);
        $json = true;
        break;
    case 'clear-seats':
        $event_id = int($_REQUEST['event_id']);
        $sector_id = int($_REQUEST['sector_id']);
        foreach($_POST['place'] as $key=>$val)
            foreach ($val as $key2=>$val2)
                clearPlace($event_id, $sector_id, $key, $key2);
        header("Location: ?");
        break;
    default:
        $events = $sbgs->GetEvents();

        $html = true;
}



if ($html) {
    header("Content-Type: text/html; charset=utf-8");
?>
<!DOCTYPE html>
<html><head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Освобождение брони</title>
</head><body>
    <form name="clear" method="post">
        <label for="select-event">Событие:</label>
        <select name="event_id" id="select-event">
            <option>Выберите...</option>
<?php
    foreach ($events as $event)
        echo "            <option value=\"$event[id]\">$event[name] ($event[date] $event[time])</option>\n";
?>
        </select>
        <label for="select-sector">Сектор:</label>
        <select name="sector_id" id="select-sector">
        </select>
        <span id="loading" style="display: none; background-color: #fcc;">Подождите, загружается информация...</span>
        <table>
            <caption>Текущие брони</caption>
            <thead><tr>
                <th></th><th>Ряд</th><th>Место</th><th>Стоимость</th><th>ID</th><th>Сессия</th>
            </tr></thead>
            <tbody id="places"></tbody>
            <tfoot><tr><td colspan="4"><button name="action" id="button-clear" value="clear-seats">Освободить указанные места</button></td></tr></tfoot>
        </table>
    </form>
    <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
    <script>
var event_id  = undefined;
var sector_id = undefined;
$(document).ready(function(){
    $("#select-event").change(function(){
        event_id = $(this).val();
        $('#loading').show();
        $.get("?action=list-sectors&event_id=" + event_id, function(data) {
            $("#select-sector").html("<option><i>Выберите...</i></option>");
            for (var i in data) {
                var item = data[i];
                $("#select-sector").append('<option value="' + item.id + '">' + item.name + '</option>');
            }
            $('#loading').hide();
        });
    });
    $("#select-sector").change(function(){
        sector_id = $(this).val();
        $('#loading').show();
        $.get("?action=list-reserve&event_id=" + event_id + "&sector_id=" + sector_id, function(data) {
            $("#places").html("");
            for (var i in data) {
                var item = data[i];
                var input = '<input type="checkbox" name="place[' + item.row + '][' + item.seat + ']">';
                $("#places").append('<tr><td>' + input + '</td><td>' + item.row + '</td><td>' + item.seat + '</td><td>' + item.price + '</td><td>' + item.order_id + '</td><td>' + item.session + '</td></tr>');
            }
            $('#loading').hide();
        });
    });
});
    </script>
</body></html>
<?php
} // if $html

if ($json) {
    header("Content-Type: application/json; charset=utf-8");
    echo json_encode($data);
} // if $json

?>