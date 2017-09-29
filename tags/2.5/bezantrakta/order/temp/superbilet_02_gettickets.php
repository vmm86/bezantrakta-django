<?php
/**
 * Вынужденная прокладка для сервиса оплаты СНГБ
 */
function sngbInitProxy() {
    $this->logger->write(
        array(
            'init_proxy_input' => $_GET
        ), 'payment_sngb'
    );

    // Получение заказа
    $event_id  = $_GET['event_id'];
    $order_tag = isset($_GET['tag']) ? $_GET['tag'] : null;

    $this->order = getOrder($event_id, $order_tag);
    #$this->logger->write(array('OrderClassName' => get_class($this->order), 'OrderClass' => $this->order));

    // Если в ответе есть ошибка
    if (isset($_GET['error'])) {
        $this->order->payment_info['error_code']    = $_GET['error'];
        $this->order->payment_info['error_message'] = $_GET['errortext'];

        $this->paymentError();
    // Если в ответе нет ошибки
    } else {
        #$this->order->event_id = $_GET['event_id'];
        #$this->order->event_info = $this->order->getEventInfo($this->order->event_id);
        $this->order->order_id = $_GET['trackid'];
        $this->order->payment_id = $_GET['paymentid'];
        // Приведение кода оплаты к integer, если строка по сути является числом (у успешной оплаты равно '00')
        $this->order->payment_info['payment_code'] = is_numeric($_GET['responsecode']) ? (int)$_GET['responsecode'] : $_GET['responsecode'];
        $this->order->payment_info['payment_status'] = $_GET['result'];

        // Удачный запрос на оплату
        if ($this->order->payment_info['payment_code'] == 0) {
            $this->logger->write(
                array(
                    'init_proxy' => 'success',
                    'tag'        => $this->order->tag,
                    'payment_id' => $this->order->payment_id
                ), 'payment_sngb'
            );

            $this->paymentSuccess();
        // НЕудачный запрос на оплату
        } else {
            $this->logger->write(
                array(
                    'init_proxy' => 'error',
                    'tag'        => $this->order->tag,
                    'payment_id' => $this->order->payment_id
                ), 'payment_sngb'
            );

            $this->order->payment_info['error_code']    = $_GET['responsecode'];
            $this->order->payment_info['error_message'] = mb_strtoupper($_GET['result'], 'UTF-8');

            $this->paymentError();
        }
    }
}

/**
 * Вынужденная прокладка для сервиса оплаты СНГБ
 */
function sngbErrorProxy() {
    $this->logger->write(
        array(
            'error_proxy' => $_GET
        ), 'payment_sngb'
    );

    // Получение заказа
    $event_id  = $_GET['event_id'];
    $order_tag = isset($_GET['tag']) ? $_GET['tag'] : null;

    $this->order = getOrder($event_id, $order_tag);
    #$this->logger->write(array('OrderClassName' => get_class($this->order), 'OrderClass' => $this->order));

    $this->order->event_id = $_GET['event_id'];
    $this->order->tag = $_GET['tag'];
    $this->order->order_id = $_GET['trackid'];
    $this->order->payment_id = $_GET['paymentid'];
    $this->order->payment_info['payment_code'] = $_GET['responsecode'];
    $this->order->payment_info['payment_status'] = $_GET['result'];
    $this->order->payment_info['error_code'] = $_GET['error'];
    $this->order->payment_info['error_message'] = $_GET['errortext'];

    $this->paymentError();
}

/**
 * CRON-задача для проверки заказов, состояние которых указано как `AwaitingPayment` (ожидание оплаты),
 * хотя заказ уже м.б. успешно оплачен или не оплачен с ошибкой.
 */
function checkup() {
    $config =& JFactory::getConfig();
    $payment = getPayment('superbilet', $config->getValue('commission_included'));

    // Время сессии для оплаты
    $timeout = $payment->timeout() + 2;

    // Получение всех заказов со статусом `AwaitingPayment`
    $db =& JFactory::getDBO();
    $query = "SELECT * FROM `#__sb_orders` WHERE `state` = 'AwaitingPayment'";
    $db->setQuery($query);
    $awaiting_payment = $db->loadAssocList();

    // Текущая дата и время
    $now = strtotime(date('Y-m-d H:i:s'));

    foreach ($awaiting_payment as $ap) {
        // Дата заказа из БД
        $dt = strtotime($ap['dt']);
        // Разница между текущем временем и временем заказа в минутах
        $diff = round(abs($now - $dt) / 60);

        $this->logger->write(array('current_awaiting_payment' => $ap), 'tickets_superbilet_checkup');
        // 'now' => $now, 'dt' => $dt, 'diff' => $now

        // Если со времени заказа прошло больше, чем время сессии для оплаты заказа
        if ((int)$diff > $timeout) {
            // Получение заказа
            $this->order = getOrder($ap['event_id'], $ap['tag']);

            $tickets = $this->order->data;
            $pattern = "/^(\d+)-(\d+)-(\d+)-(\d+)$/";
            $this->order->chosen_tickets = array_intersect_key($tickets, array_flip(preg_grep($pattern, array_keys($tickets))));
            foreach ($this->order->chosen_tickets as $tid => &$ticket) {
                $ticket['price'] = floor($ticket['price']) != $ticket['price'] ? round($ticket['price'], 2) : round($ticket['price'], 0);
            }
            unset($ticket);

            // Получение информации о билетах
            $tickets = $this->sbgs->GetState($this->order->extractOrderTickets($this->order->data));
            $this->logger->write(array('current_awaiting_payment_GetState' => $tickets), 'tickets_superbilet_checkup');

            // Проверка корректности `order_id`
            $reservation_correct = $this->check_order_id($tickets, $this->order->order_id);
            if ($reservation_correct === true) {
                // Проверяем статус оплаты
                $ap_status = $payment->status($ap['payment_id']);
                $this->logger->write(array('current_awaiting_payment_status' => $ap_status), 'tickets_superbilet_checkup');

                switch ($ap_status['result']) {
                    // Если оплата прошла успешно
                    case 'success':
                        // Отмечаем заказ оплаченным
                        $this->order->mark('Paid', $tickets);
                        break;
                    // Если оплата прошла НЕуспешно
                    case 'error':
                        $this->order->payment_info['error_code']    = $ap_status['error_code'];
                        $this->order->payment_info['error_message'] = $ap_status['error_message'];
                        // Отменяем заказ отменённым из-за неудачной оплаты
                        $this->order->mark('Cancelled', $tickets);
                        break;
                }
            } else {
                // Отмечаем заказ отменённым из-за изменившегося или отсутствующего `order_id` - бронь освободилась по таймауту
                $this->order->payment_info['error_code']    = '';
                $this->order->payment_info['error_message'] = 'reservation id incorrect';
                $this->order->mark('Cancelled', $tickets);
            }

        }
    }
}

/**
 * Проверка каждого из билетов в заказе (после SetReservation в начале оформления заказа или после GetState при обработке онлайн-оплаты)
 * 
 * @param array   $tickets Список билетов в заказе
 * @param boolean $eticket Нужно ли будет генерировать электронные билеты
 * 
 */
function checkTickets($tickets, $eticket = false) {
    $logger = new Logger();

    // Проверка каждого из билетов
    foreach ($tickets as $tid => $ticket) {
        // Проверка неудачно зарезервированных билетов
        if (isset($ticket['result_id']) && (int)$ticket['result_id'] != 0) {
            $logger->write(array('error_ticket' => $ticket, 'error_ticket_result_id' => $ticket['result_id']));
            $error_tickets[] = $et;
        }

        $logger->write(array('successful_ticket' => $ticket));
        // Перебор удачно зарезервированных билетов
        $st = array();
        $st['event_id']  = $ticket['event_id'];
        $st['sector_id'] = $ticket['sector_id'];
        $st['row']    = $ticket['row'];
        $st['seat']   = $ticket['seat'];
        if ($eticket === true) {
            $st['number']  = $number;
            $st['barcode'] = $barcode;
        }
    }

    $this->order->chosen_tickets = $successful_tickets;
    $this->order->count_chosen   = $count_chosen;
    $this->order->total          = $total;
}
