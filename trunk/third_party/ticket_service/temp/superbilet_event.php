<?php

class AfishaControllerEvent extends AfishaController {
    /**
     * Работа с местами в схеме зала на первом шаге заказа билетов.
     * <ul>
     * <li>Получение списка мест в конкретном событии (событие `refresh` - работает по таймауту).</li>
     * <li>Обработка выделения и освобождения мест (событие `select` или `free` - асинхронный вызов при клике по месту).</li>
     * </ul>
     */
    public function ticketAction() {
        $event_id = (int)JRequest::getVar('event_id', 0);
        $order_tag = JRequest::getVar('order_tag', null, 'COOKIE', 'STRING');

        // Получение заказа
        $this->order = getOrder($event_id, $order_tag);

        $needSaveOrder = true;
        // Действие `refresh` может изменить заказ при загрузке страницы (убрать места из других событий), или если какое-то из мест автоосвободилось
        switch ($action) {
            case 'refresh':
                // Отфильтровываем из заказа места, забронированные ранее в других событиях, 
                // и делаем эти места снова свободными для заказа
                $orderOtherEventsItems = array();
                foreach ($this->order->data as $k => $p) {
                    $needSaveOrder = false;
                    $order_keys = array_map('intval', explode('-', $k)); // разбор в массив со значениями именно int, а не str
                    if (count($order_keys) == 4 and $order_keys[0] != $event_id) {
                        $orderOtherEventsItems[] = array(
                            'event_id'  => $order_keys[0],
                            'sector_id' => $order_keys[1],
                            'row'       => $order_keys[2],
                            'seat'      => $order_keys[3],
                            'session'   => $this->order->tag
                        );
                        unset($this->order->data[$k]);
                        $needSaveOrder = true;
                    }
                }
                if ($needSaveOrder) {
                    $this->create_or_update($this->order);
                    $this->sbgs->ClearMark($orderOtherEventsItems);
                    $needSaveOrder = false;
                }
                // Отфильтровываем из заказа автоосвобождённые места
                $places = $this->sbgs->GetStagehallState($event_id, $this->order->tag, $this->orderPlaces($this->order->data));
                foreach ($places as $k => $p) {
                    $states[$k] = array(
                        'state' => $p['state'],
                        'price' => $p['price'],
                        'color' => ($p['state'] == 'F') ? $this->getColorAllocationFor($event_id, $p['price']) : 0
                    );
                    // Отфильтровываем места, которые были в заказе, вдруг они автоматически освобождены?
                    $needSaveOrder = false;
                    if (isset($this->order->data["$event_id-$k"]) && $p['state'] == 'F') {
                        unset($this->order->data["$event_id-$k"]);
                        $needSaveOrder = true;
                    }
                }
                $result = array();
                break;

            default:
                $result = array();
        }

        echo json_encode(array(
            'action'    => $action,
            'event_id'  => $event_id,
            'sector_id' => $sector_id,
            'states'    => $states,
            'order'     => $this->order->data,
            'legend'    => $this->allocations)
        );
    }

}
