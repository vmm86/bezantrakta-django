<?php
class SBGS {
    var $xmlTemplate;
    var $soapClient;
    var $customerInfo = null;

    # Для фильтрации автоосвобождённых мест
    function GetStagehallState($event_id, $session = false, $places_order = array()) {
        $sectors = $this->GetSectors($event_id);
        $places_sectors = array();
        foreach ($sectors as $sector_id=>$sector)
            $places_sectors = $places_sectors + $this->GetPlaces($event_id, $sector_id);
        // Проверяем только указанные в заказе места $places_order, а не все места зала $places_sectors - так работает гораздо быстрее
        $places_known = $this->GetState(array_map("_clean_data", $places_order));
        $places_available = $this->GetPlacesAvailable($event_id);
        $places_merged = array();
        foreach ($places_sectors as $id=>$info) {
            if (isset($places_known[$id])) {
                $place = $places_known[$id];
                $status = (isset($place['status'])) ? $place['status'] : ((isset($place['gateStatus'])) ? $place['gateStatus'] : 'FRE');
                switch ($status) {
                    case 'SEL':
                        $place['state'] = ($place['session'] == $session) ? 'S' : 'O';
                        break;
                    case 'RES':
                        $place['state'] = 'P';
                        break;
                    case 'SOL':
                    case 'OTH': // WTF? Не было такого в документации. Похоже на место, проданное через шлюз. Считаем недоступным.
                    case 'SOT': // сейм шит
                        $place['state'] = 'E';
                        break;
                    default:
                        $place['state'] = 'F';
                }
            } elseif (isset($places_available[$id]) && isset($places_available[$id]['price'])) {
                $place = $places_available[$id];
                $place['state'] = 'F';
            } else {
                $place = $info;
                if (!isset($place['price'])) $place['price'] = 0;
                $place['state'] = 'E';
            }
            $places_merged[$id] = $place;
        }

        return $places_merged;
    }

}

// Интерфейс одинаковый (пользователи класса используют SetCustomerInfo, затем SetReservation и так далее)

?>
