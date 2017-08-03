<?php
defined('_JEXEC') or die('Restricted access');

class AfishaControllerGettickets extends AfishaController {
    /** @param SBGS   $sbgs   Экземпляр класса SBGS */
    private $sbgs = null;
    /** @param Order  $order  Экземпляр класса Order */
    private $order = null;
    /** @param Logger $logger Экземпляр класса Logger */
    private $logger = null;

    public function order() {
        global $mainframe;

        $config =& JFactory::getConfig();
        $db     =& JFactory::getDBO();

        // Получение данных POST-запроса со второго шага заказа билетов
        $customer = $_POST['customer'];
        // Запоминание данных покупателя на будущее в cookie `afishaCustomer`
        setcookie('afishaCustomer', serialize($customer), time() + 366*24*60*60, '/');

        // Получение подкласса конкретного типа заказа
        $event_id   = (int)$_POST['event_id'];
        $order_tag  = JRequest::getVar('order_tag', null, 'COOKIE', 'STRING');
        $order_type = $customer['delivery'];

        $this->order = getOrder($event_id, $order_tag);
#$this->logger->write(array('OrderClassName1' => get_class(this->$order), 'OrderClass1' => $this->order));
        // Сохранение типа заказа в БД, 
        // чтобы потом его специально нигде не указывать 
        // и сразу получать подкласс конкретного типа заказа
        $this->order->update($this->order, 'New', $order_type);

        $this->order = getOrder($event_id, $order_tag);
#$this->logger->write(array('OrderClassName2' => get_class($this->order), 'OrderClass2' => $this->order));

        // Получение контактных данных покупателя
        $this->order->name  = substr($db->quote($customer['name']),1,-1);
        $this->order->email = substr($db->quote($customer['email']),1,-1);
        $this->order->phone = preg_replace('/[^\d]/', '', $customer['phone']);

        if ($this->order->type == 'Courier') {
            $this->order->address = $customer['address'];
        }

        // Получение информации о билетах из БД
        $tickets = $this->order->extractOrderTickets($this->order->data);

        // Запись информации о закачике
        $this->sbgs->SetCustomerInfo(
            array(
                'name'  => $this->order->name,
                'phone' => $this->order->phone,
                'email' => $this->order->email,
                #'has_delivery'     => ($this->order->type == 'Courier' ? 1 : 0),
                'has_delivery'     => $this->order->has_delivery,
                #'delivery_address' => ($this->order->type == 'Courier' ? $this->order->address : null),
                'delivery_address' => $this->order->address,
                'order_id' => $this->order->tag
            )
        );

        // Резервирование выбранные билеты
        $reservation = $this->sbgs->SetReservation($tickets);

        // Проверка каждого из зарезервированных билетов
        $this->checkTickets($reservation);

        // Получение информации о билетах (вместе с `reservation_id`)
        $tickets = $this->sbgs->GetState($tickets);

        // Проверка корректности резерва билетов
        $___reservation_correct = true;
        foreach ($tickets as $ticket) {
            $this->order->reservation_id = $ticket['reservation_id'];

            if ( (int)$ticket['result'] != 0 ) {
                $___reservation_correct = false;
            }
        }

        $this->logger->write(
            array(
                'event_id' => $this->order->event_id,
                'tag' => $this->order->tag,
                'reservation_id' => $this->order->reservation_id,
                'tickets' => $tickets,
                'reservation_correct' => $___reservation_correct,
                'order' => $this->order
            )
        );

        if ($___reservation_correct === false) {
            $this->order->payment_info['error_code']    = '';
            $this->order->payment_info['error_message'] = 'reservation incorrect';
            $message = '<span id="error-message">К сожалению, произошла ошибка резерва билетов. <a href="' . $this->order->event_url . '">👉 Попробуйте заказать билеты ещё раз</a>.</span>';
            // Отмечаем заказ отменённым из-за некорректного `reservation_id`
            $this->order->mark('Cancelled', $tickets, $this->order->final_url, $message);
        }

        // Указание состояния заказа в зависимости от его типа
        $this->order->setOrderState();

        // Оформление предварительного заказа билетов
        $this->order->preOrder($tickets);

        $mainframe->close();
    }

    /**
     * Вынужденная прокладка для сервиса оплаты СНГБ
     */
    public function sngbInitProxy() {
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
            $this->order->reservation_id = $_GET['trackid'];
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
     * Обработка успешного результата оплаты
     */
    public function paymentSuccess() {
        global $mainframe;

        // Получение заказа, если он не был получен ранее
        if (!isset($this->order)) {
            $event_id  = $_GET['event_id'];
            $order_tag = isset($_GET['tag']) ? $_GET['tag'] : null;

            $this->order = getOrder($event_id, $order_tag);
        }

        $this->logger->write(array('success_order' => $this->order));

        #$this->order->event_info = $this->order->getEventInfo($this->order->event_id);
        #$this->order->setOrderURL();

        // Получение информации о билетах
        $tickets = $this->sbgs->GetState($this->order->extractOrderTickets($this->order->data));

        // Проверка корректности `reservation_id`
            // Данные условия маловероятны при онлайн-резерве и вероятны в CRON-методе `checkup`, но корректны в обоих случаях.
            // Если билеты сменили статус на `SOL` при том, что сохранили сессию и номер брони - они были выкуплены в кассе.
        $_reservation_timed_out = $this->checkReservationId($tickets, $this->order->reservation_id);
        if ($_reservation_timed_out === false) {
            $this->order->payment_info['error_code']    = '';
            $this->order->payment_info['error_message'] = 'reservation ' . $this->order->reservation_id . ' timed out';
            $message = '<span id="error-message">К сожалению, произошла ошибка резерва билетов. <a href="' . $this->order->event_url . '">👉 Попробуйте заказать билеты ещё раз</a>.</span>';
            // Отмечаем заказ отменённым из-за изменившегося или отсутствующего `reservation_id` - бронь освободилась по таймауту
            $this->order->mark('Cancelled', $tickets, $this->order->final_url, $message);
        }

        // Получение списка билетов в заказе
        $this->checkTickets($tickets, true);

        // Проверка статуса оплаты (на всякий случай)
        $config =& JFactory::getConfig();
        $payment = getPayment('superbilet', $config->getValue('commission_included'));
        $payment_status = $payment->status($this->order->payment_id);

        switch ($payment_status['result']) {
            case 'success':
                $message = '<span id="success-message">Заказ № ' . $this->order->reservation_id . ' успешно оплачен, номер оплаты ' . $this->order->payment_id . '. На введённый Вами email отправлена информация о заказанных Вами билетах.</span>';
                // Отмечаем заказ оплаченным
                $this->order->mark('Paid', $tickets, $this->order->final_url, $message);
                break;
            
            case 'error':
                $this->order->payment_info['error_code']    = $payment_status['error_code'];
                $this->order->payment_info['error_message'] = $payment_status['error_message'];
                $error_text = '';
                if (isset($this->order->payment_info['error_code'])) {
                    $error_text .= ' ' . $this->order->payment_info['error_code'];
                }
                if (isset($this->order->payment_info['error_message'])) {
                    $error_text .= ': ' . $this->order->payment_info['error_message'];
                }
                $message = '<span id="error-message">К сожалению, в процессе оплаты возникла ошибка' . $error_text . ' <a href="' . $this->order->event_url . '">👉 Попробуйте заказать билеты ещё раз</a>.</span>';
                // Отмечаем заказ отменённым из-за неудачной оплаты
                $this->order->mark('Cancelled', $tickets, $this->order->final_url, $message);
                break;
        }

        $mainframe->close();
    }

    /**
     * Вынужденная прокладка для сервиса оплаты СНГБ
     */
    public function sngbErrorProxy() {

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
        $this->order->reservation_id = $_GET['trackid'];
        $this->order->payment_id = $_GET['paymentid'];
        $this->order->payment_info['payment_code'] = $_GET['responsecode'];
        $this->order->payment_info['payment_status'] = $_GET['result'];
        $this->order->payment_info['error_code'] = $_GET['error'];
        $this->order->payment_info['error_message'] = $_GET['errortext'];

        $this->paymentError();
    }

    /**
     * Обработка НЕуспешного результата оплаты (освобождение выбранных мест и отправка email пользователю)
     */
    public function paymentError() {
        global $mainframe;

        // Получение заказа, если он не был получен ранее
        if (!isset($this->order)) {
            $event_id = $_GET['event_id'];
            $order_tag = isset($_GET['tag']) ? $_GET['tag'] : null;

            $this->order = getOrder($event_id, $order_tag);
        }

        $this->logger->write(array('error_order' => $this->order));

        #$this->order->event_info = $this->order->getEventInfo($this->order->event_id);
        #$this->order->setOrderURL();

        // Обновляем информацию о билетах
        $tickets = $this->sbgs->GetState($this->order->extractOrderTickets($this->order->data));

        // Проверка статуса оплаты (на всякий случай)
        $config =& JFactory::getConfig();
        $payment = getPayment('superbilet', $config->getValue('commission_included'));
        $payment_status = $payment->status($this->order->payment_id);

        $this->order->payment_info['error_code']    = $payment_status['error_code'];
        $this->order->payment_info['error_message'] = $payment_status['error_message'];
        $error_text = '';
        if (isset($this->order->payment_info['error_code'])) {
            $error_text .= ' ' . $this->order->payment_info['error_code'];
        }
        if (isset($this->order->payment_info['error_message'])) {
            $error_text .= ': ' . $this->order->payment_info['error_message'];
        }
        $message = '<span id="error-message">К сожалению, в процессе оплаты возникла ошибка' . $error_text . ' <a href="' . $this->order->event_url . '">👉 Попробуйте заказать билеты ещё раз</a>.</span>';
        // Отмечаем заказ отменённым из-за неудачной оплаты
        $this->order->mark('Cancelled', $tickets, $this->order->final_url, $message);

        $mainframe->close();
    }

    /**
     * CRON-задача для проверки заказов, состояние которых указано как `AwaitingPayment` (ожидание оплаты),
     * хотя заказ уже м.б. успешно оплачен или не оплачен с ошибкой.
     */
    public function checkup() {

        $this->order->checkup = true;

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

                // Проверка корректности `reservation_id`
                $reservation_correct = $this->checkReservationId($tickets, $this->order->reservation_id);
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
                    // Отмечаем заказ отменённым из-за изменившегося или отсутствующего `reservation_id` - бронь освободилась по таймауту
                    $this->order->payment_info['error_code']    = '';
                    $this->order->payment_info['error_message'] = 'reservation id incorrect';
                    $this->order->mark('Cancelled', $tickets);
                }

            }
        }

        // Удаление старых незавершённых заказов спустя сутки после их создания
        $this->cleanup();

        $this->order->checkup = false;
    }

    /**
     * Удаление старых никак не завершённых заказов (в состоянии `New`) спустя какое-то время после их создания
     * 
     * @param string $interval Временной MySQL-интервал, по истечении которого будут удалены старые незавершённые заказы (по умолчанию - сутки)
     * 
     */
    private function cleanup($interval = '1 DAY') {
        $db =& JFactory::getDBO();

        // $query  = "SELECT * FROM `#__sb_orders` ";
        $query  = "DELETE FROM `#__sb_orders` ";
        $query .= "WHERE `state` = 'New' ";
        $query .= "AND (`dt` IS NULL OR `dt` <= NOW() - INTERVAL " . $interval . ")";

        $db->setQuery($query);
        $db->query();

        $affected_rows = $db->getAffectedRows();
        if ((int)$affected_rows !== 0) {
            $this->logger->write(array('unfinished_orders_deleted' => $affected_rows), 'tickets_superbilet_checkup');
        }
    }

    /**
     * Проверка корректности `reservation_id`
     * 
     * @param array $tickets Список билетов в заказе
     * 
     * @return boolean Состояние `reservation_id` - корректно (true) или некорректно (false)
     * 
     */
    private function checkReservationId($tickets, $reservation_id) {
        $logger = new Logger();
        $log = array();

        $result = true;
        foreach ($tickets as $ticket) {
            $log['checkReservationId_ticket'] = $ticket;
            $log['checkReservationId_reservation_id'] = $reservation_id;
            if (!isset($ticket['reservation_id']) || $ticket['reservation_id'] != $reservation_id) {
                $result = false;
                break; // Можно не проходить по ВСЕМ билетам - достаточно одного
            }
        }

        $log['checkReservationId_result'] = $result;

        // Логирование в общий файл лога или в лог для метода `checkup`
        if ($this->order->checkup === true) {
            $logger->write($log, 'tickets_superbilet_checkup');
        } else {
            $logger->write($log);
        }

        return $result;
    }

    /**
     * Проверка каждого из билетов в заказе (после SetReservation в начале оформления заказа или после GetState при обработке онлайн-оплаты)
     * 
     * @param array   $tickets Список билетов в заказе
     * @param boolean $eticket Нужно ли будет генерировать электронные билеты
     * 
     */
    private function checkTickets($tickets, $eticket = false) {
        $logger = new Logger();

        $config =& JFactory::getConfig();

        $sbgs = GetSBGS(
            $config->getValue('SBGS_host'),
            $config->getValue('SBGS_user'),
            $config->getValue('SBGS_pass'),
            $config->getValue('SBGS_mode')
        );

        $events = $sbgs->GetEvents(); // TODO: мигрировать на новую схему разделения show и event
        $venues = $sbgs->GetVenues();
        $stages  = array();
        $sectors = array();
        $error_tickets      = array();
        $successful_tickets = array();
        $count_chosen = 0;
        $total = 0.0;

        // Проверка каждого из билетов
        foreach ($tickets as $tid => $ticket) {
            if (!isset($sectors[$ticket['event_id']])) {
                $sectors[$ticket['event_id']] = $sbgs->GetSectors($ticket['event_id']);
            }
            if (!isset($stages[$events[$ticket['event_id']]['venue_id']])) {
                $stages[$events[$ticket['event_id']]['venue_id']] = $sbgs->GetStages($events[$ticket['event_id']]['venue_id']);
            }

            // Проверка неудачно зарезервированных билетов
            if (isset($ticket['result_id']) && (int)$ticket['result_id'] != 0) {
                $logger->write(array('error_ticket' => $ticket, 'error_ticket_result_id' => $ticket['result_id']));

                $et = array();
                $et['sector_name'] = mb_strtolower($sectors[$ticket['event_id']][$ticket['sector_id']]['name'], 'UTF-8');
                $et['row']    = $ticket['row'];
                $et['seat']   = $ticket['seat'];
                $error_tickets[] = $et;

                unset($this->order->data[$tid]);

                continue;
            }

            $logger->write(array('successful_ticket' => $ticket));
            // Перебор удачно зарезервированных билетов
            $st = array();
            $st['event_id']  = $ticket['event_id'];
            $st['sector_id'] = $ticket['sector_id'];
            $st['sector_name'] = mb_strtolower($sectors[$ticket['event_id']][$ticket['sector_id']]['name'], 'UTF-8');
            $st['row']    = $ticket['row'];
            $st['seat']   = $ticket['seat'];
            $st['price']  = floor($ticket['price']) != $ticket['price'] ? round($ticket['price'], 2) : round($ticket['price'], 0);
            if ($eticket === true) {
                $st['number']  = $this->getSerial(10);
                $st['barcode'] = $this->getSerial(12);
            }
            $successful_tickets[$tid] = $st;
            $count_chosen += 1;
            $total += $st['price'];
        }

        $this->order->chosen_tickets = $successful_tickets;
        $this->order->count_chosen   = $count_chosen;
        $this->order->total          = $total;
    }

    /**
     * Генерация числа с указанным количеством цифр (для штрих-кода или номера билета)
     * 
     * @param integer $ceil Количество цифр в числе (по умолчанию - 12 для штрих-кода)
     * 
     * @return string Число
     */
    private function getSerial($ceil = 12) {
        $number = '';
        for ($i = 1; $i < $ceil; $i++) {
            // Первое и последнее число для удобства не будут равны нулю
            if ($i == 1 || $i == $ceil) {
                $number .= mt_rand(1, 9);
            } else {
                $number .= mt_rand(0, 9);
            }
        }
        return $number;
    }

}
