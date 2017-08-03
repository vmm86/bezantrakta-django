<?php
// Импорт массива с ID залов в городе этого сайта из конфига сайта
$stages = $config->sb_stages;

// Фабрика для создания инстанса SBGS
$sbgs = GetSBGS($SBGS_host, $SBGS_user, $SBGS_password, $SBGS_mode);

function clearPlace($event_id, $sector_id, $row, $seat) {
    global $sbgs;
    $info = $sbgs->GetState(array(array('event_id' => $event_id, 'sector_id' => $sector_id, 'row' => $row, 'seat' => $seat)));
    $session = $info["$sector_id-$row-$seat"]['session'];
    $reservation_id = $info["$sector_id-$row-$seat"]['reservation_id'];
    return $sbgs->ClearReservation(array(array('event_id' => $event_id, 'sector_id' => $sector_id, 'row' => $row, 'seat' => $seat, 'session'=>$session, 'reservation_id' => $reservation_id)));
}

switch ($_REQUEST['action']) {
    case 'list-sectors':
        $event_id = $_REQUEST['event_id'] + 0;
        $sectors = $sbgs->GetSectors($event_id);
        $data = array_values($sectors);
        $json = true;
        break;
    case 'list-reservations':
        $event_id = $_REQUEST['event_id'] + 0;
        $sector_id = $_REQUEST['sector_id'] + 0;
        $reservations = array_filter($sbgs->GetSectorState($event_id, $sector_id), function($a) {return $a['state'] == 'P';});
        $data = array_values($reservations);
        $json = true;
        break;
    case 'clear-places':
        $event_id = $_REQUEST['event_id'] + 0;
        $sector_id = $_REQUEST['sector_id'] + 0;
        foreach($_POST['place'] as $key=>$val)
            foreach ($val as $key2=>$val2)
                clearPlace($event_id, $sector_id, $key, $key2);

        header("Location: ?");
        break;
    default:
        $events = $sbgs->GetEvents();

        // Из массива событий в СБ удаляются все события, которые проходят не в залах в городе этого сайта
        foreach ($events as $event) {
            if ( !array_key_exists($event['stage_id'], $stages) ) {
                unset($events[$event['id']]);
            }
        }

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
            <tfoot><tr><td colspan="4"><button name="action" id="button-clear" value="clear-places">Освободить указанные места</button></td></tr></tfoot>
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
        $.get("?action=list-reservations&event_id=" + event_id + "&sector_id=" + sector_id, function(data) {
            $("#places").html("");
            for (var i in data) {
                var item = data[i];
                var input = '<input type="checkbox" name="place[' + item.row + '][' + item.seat + ']">';
                $("#places").append('<tr><td>' + input + '</td><td>' + item.row + '</td><td>' + item.seat + '</td><td>' + item.price + '</td><td>' + item.reservation_id + '</td><td>' + item.session + '</td></tr>');
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