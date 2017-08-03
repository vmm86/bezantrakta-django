<?php
defined('_JEXEC') or die('Restricted access');

/**
 * Фабрика для создания экземпляров класса Order
 * как предварительного заказа без конкретного типа 
 * или его дочерних классов для отдельных типов заказа.
 * 
 * @param string $event_id  Уникальный номер события
 * @param string $order_tag Уникальный номер заказа (опционально)
 *
 * @return Order|OrderSelf|OrderCourier|OrderPayment|OrderETicket Экземпляр класса Order или его дочернего класса
 */
function getOrder($event_id, $order_tag = null) {
    // Если `order_tag` НЕ задан
    if (is_null($order_tag)) {
        // Если `order_tag` сохранён в cookie - он берётся оттуда
        if (isset($_COOKIE['order_tag'])) {
            $order_tag = Order::sanitizeOrderTag($_COOKIE['order_tag']);
        // Если `order_tag` НЕ сохранён в cookie - создаётся новая cookie `order_tag`
        } else {
            $order_tag = md5(uniqid(time()));
            setcookie("order_tag", $order_tag, 0, '/');
        }
        // Создание экземпляра нового предварительного заказа
        return new Order($event_id, $order_tag);
    // Если `order_tag` задан - он используется
    } else {
        $order_tag = Order::sanitizeOrderTag($order_tag);

        // Информация о конкретном заказе в БД
        $db =& JFactory::getDBO();
        $query = "SELECT * FROM `#__sb_orders` WHERE `tag` = '" . $order_tag . "'";
        $db->setQuery($query);
        $order_from_db = $db->loadAssoc();

#$logger = new Logger();
#$logger->write(array('order_from_db' => $order_from_db));

        // Если тип заказа в БД НЕ указан - заказ предварительный в состоянии `New`
        if (is_null($order_from_db['type'])) {
            #$logger->write(array('class_name' => 'Order'));
            // Создание экземпляра существующего предварительного заказа
            return new Order($event_id, $order_tag, $order_from_db);
        // Если тип заказа в БД указан - заказ оформен с каким-то типом
        } else {
            $OrderClass = 'Order' . $order_from_db['type'];
            #$logger->write(array('class_name' => $OrderClass));
            // Создание экземпляра существующего заказа
            return new $OrderClass($event_id, $order_tag, $order_from_db);
        }
    }
}

/** Класс для хранения информации о заказе и CRUD-операций с заказом в БД */
class Order {
    /** @var integer $event_id Идентификатор события */
    public $event_id = 0;
    /** @var array $event_info Информация о событии из БД */
    public $event_info = array();

    /** @var string $name ФИО покупателя */
    public $name;
    /** @var string $email email покупателя */
    public $email;
    /** @var string $phone Телефон покупателя */
    public $phone;
    /** @var string $address Адрес доставки (для доставки курьером) */
    public $address = null;

    /** 
     * @var string $type Тип оплаты/получения билетов
     * <ul>
     * <li>Self    - получение в кассе</li>
     * <li>Courier - доставка курьером</li>
     * <li>Payment - онлайн-оплата</li>
     * <li>ETicket - электронный билет</li>
     * </ul>
     */
    public $type;

    // TODO: разделить варианты доставки и оплаты на разные поля!
    // delivery | payment
    // ---------|---------
    // Self     | Cash
    // Courier  | Cash
    // Self     | Online
    // ETicket  | Online

    /** 
     * @var string $state Текущее состояние заказа (связано с типом заказа `type`)
     * <ul>
     * <li>Self
     *     <ul>
     *     <li>New                - новый заказ</li>
     *     <li>AwaitingRedemption - ожидание получения в кассе</li>
     *     <li>Redeemed           - получено в кассе (на данный момент не реализовано)</li>
     *     <li>Cancelled          - отменённый заказ</li>
     *     </ul>
     * </li>
     * <li>Courier
     *     <ul>
     *     <li>New              - новый заказ</li>
     *     <li>AwaitingDelivery - ожидание доставки курьером</li>
     *     <li>Delivered        - доставлено курьером (на данный момент не реализовано)</li>
     *     <li>Cancelled        - отменённый заказ</li>
     *     </ul>
     * </li>
     * <li>Payment
     *     <ul>
     *     <li>New             - новый заказ</li>
     *     <li>AwaitingPayment - ожидание онлайн-оплаты</li>
     *     <li>Paid            - оплачено в сервисе онлайн-оплаты + ожидание получения в кассе</li>
     *     <li>Cancelled       - отменённый заказ</li>
     *     </ul>
     * </li>
     * <li>ETicket
     *     <ul>
     *     <li>New             - новый заказ</li>
     *     <li>AwaitingPayment - ожидание онлайн-оплаты</li>
     *     <li>Paid            - оплачено в сервисе онлайн-оплаты + отправлены электронные билеты</li>
     *     <li>Cancelled       - отменённый заказ</li>
     *     </ul>
     * </li>
     * </ul>
     */
    public $state;

    /**
     * @var array $chosen_tickets Список билетов в заказе
     * TODO: Уйти от него и использовать только атрибут `data`
     */
    public $chosen_tickets = array();
    /** @var integer $count_chosen Число билетов в заказе */
    public $count_chosen = 0;
    /** @var float $total Сумма заказа (БЕЗ комиссии) */
    public $total = 0.0;

    /** @var array $data Информация о билетах из БД */
    public $data = array();

    /** @var string $tag Уникальный номер заказа (32 символа) */
    public $tag = null;
    /** @var integer $reservation_id Номер заказа в Супербилете */
    public $reservation_id;
    /** @var string $dt Дата и время заказа */
    public $dt;

    /** @var integer $Itemid Костыль для правильного отображения ЧПУ URL (без /component/ в начале URL)  */
    protected $Itemid = 33;
    /** @var string $final_url URL для оповещения о завершении заказа */
    public $final_url;
    /** @var string $event_url URL для возврата на страницу события */
    public $event_url;

    /** @var string $return_url URL для редиректа после успешной оплаты */
    public $return_url;
    /** @var string $fail_url   URL для редиректа после НЕуспешной оплаты */
    public $fail_url;

    /** Информация о заказе для страницы `final` */
    public $order_info = array();

    /** @var boolean $checkup Работает ли метод `checkup` в настоящий момент или нет */
    public $checkup = false;

    protected $fromEmail;
    protected $fromName;
    protected $subject;

    /**
     * Конструктор класса, выполняющийся внутри фабрики getOrder()
     * (getCreateOrder => init_or_read => __construct)
     * 
     * @param string $event_id      Уникальный номер события
     * @param string $order_tag     Уникальный номер заказа (опционально)
     * @param array  $order_from_db Информация о заказе из БД (опционально)
     */
    function __construct($event_id, $order_tag, $order_from_db = null) {
        $this->tag = $order_tag;

        // Если заказ ещё НЕ был создан в БД
        if (is_null($order_from_db)) {
            $this->event_id = $event_id;
            $this->dt = 'NOW()';
            $this->state = 'New';
        // Если заказ уже был создан в БД
        } else {
            $this->event_id = ((int)$order_from_db['event_id'] == $event_id) ? (int)$order_from_db['event_id'] : $event_id;

            $this->dt    = $order_from_db['dt'];
            $this->data  = unserialize($order_from_db['tickets']);
            // foreach ($this->data as $ticket) {
            //     $ticket['sector'] = 
            // }
            $this->reservation_id = $order_from_db['reservation_id'];
            $this->name  = $order_from_db['name'];
            $this->email = $order_from_db['email'];
            $this->phone = $order_from_db['phone'];
            $this->total = $order_from_db['total'];

            $this->type  = $order_from_db['type'];
            $this->state = $order_from_db['state'];
            $this->payment_id = $order_from_db['payment_id'];
        }

        if (!empty($this->event_id) && $this->event_id != 0) {
            $this->event_info = $this->getEventInfo($this->event_id);
            $this->setOrderURL();
        }
    }

    /**
     * Информация о заказе из БД
     * 
     * @param string  $output Формат вывода данных
     * @param string  $field  Условия для фильтрации данных (поле)
     * @param string  $value  Условия для фильтрации данных (значение)
     * 
     * @return mixed Информация о заказе в заданном формате
     */
    public function read($output, $field = null, $value = null) {
        $db =& JFactory::getDBO();

        $query  = "SELECT * FROM `#__sb_orders` ";

        switch (gettype($value)) {
            case 'integer':
                $query .= "WHERE `" . $field . "` = " . $value . " ";
                break;
            case 'string':
                $query .= "WHERE `" . $field . "` = '" . $value . "' ";
                break;
            case 'array':
                $query .= " WHERE `" . $field . "` IN (" . implode(", ", $value) . ") ";
                break;
        }
        $query .= "ORDER BY `dt`, `id`";

        $db->setQuery($query);

        $result = null;

        switch ($output) {
            case 'loadResult':      $result = $db->loadResult();      break; // Одна запись
            case 'loadRow':         $result = $db->loadRow();         break; // Одна строка
            case 'loadAssoc':       $result = $db->loadAssoc();       break; // Одна строка (ассоциативный массив)
            case 'loadObject':      $result = $db->loadObject();      break; // Одна строка (объект PHP)
            case 'loadResultArray': $result = $db->loadResultArray(); break; // Один столбец
            case 'loadRowList':     $result = $db->loadRowList();     break; // Несколько строк
            case 'loadAssocList':   $result = $db->loadAssocList();   break; // Несколько строк (ассоциативный массив)
            case 'loadObjectList':  $result = $db->loadObjectList();  break; // Несколько строк (объект PHP)
        }

        return $result;
    }

    /**
     * Обновление заказа в БД (fixOrder => update)
     * 
     * @param Order  $order Экземпляр класса `Order`
     * @param string $state Статус заказа (имеет 3 состояния):
     * <ul>
     * <li>'New' - новый заказ</li>
     * <li>'AwaitingRedemption' - выкуп брони в кассе</li>
     * <li>'Redeemed' - выкуплено</li>
     * <li>'AwaitingDelivery' - ожидание доставки курьером</li>
     * <li>'Delivered' - доставлено</li>
     * <li>'AwaitingPayment' - ожидание онлайн-оплаты</li>
     * <li>'Paid' - оплачено</li>
     * <li>'Cancelled' - отменено</li>
     * </ul>
     * @param string $type Тип доставки/оплаты (имеет состояния):
     * <ul>
     * <li>'Reservation' - зарезервировано</li>
     * <li>'Payment' - оплачено</li>
     * <li>'ETicket' - электронный билет</li>
     * </ul>
     */
    public function update($order, $state = null, $type = null) {
        $update = array();
        $update['dt'] = 'NOW()';
        $update['type'] = is_null($type) ? "'" . $order->type . "'" : "'" . $type . "'";
        $update['state'] = "'$state'";
        $update['tickets'] = "'" . addslashes(serialize($order->data)) . "'";

        $fields = array('event_id', 'reservation_id', 'name', 'phone', 'email', 'total', 'payment_id');
        foreach ($fields as $field) {
            if(isset($order->$field) && $order->$field != null) {
                $update[$field] = "'" . $order->$field . "'";
            }
        }

        $first = true;
        $update_str = '';
        foreach($update as $key => $val) {
            if ($first) {
                $first = false;
            } else {
                $update_str .= ', ';
            }
            $update_str .= "`$key` = $val";
        }

        // Обновление заказа в БД
        $db =& JFactory::getDBO();
        $query  = "UPDATE `#__sb_orders` ";
        $query .= "SET $update_str ";
        $query .= "WHERE `tag` = '" . $order->tag . "'";
        $db->setQuery($query);
        $db->query();
    }

    /**
     * Финализация заказа в СуперБилет и в БД (на определённом этапе и с определённым результатом)
     * 
     * @param $state   string Состояние заказа (описаны в документации к $this->state)
     * @param $tickets array  Билеты в заказе
     * @param $url     string URL для редиректа после отработки метода (опционально)
     * @param $message string Сообщение для вывода на странице после редиректа (опционально)
     * 
     */
    public function mark($state, $tickets, $url = null, $message = null) {
        $config =& JFactory::getConfig();
        $sbgs = GetSBGS(
            $config->getValue('SBGS_host'),
            $config->getValue('SBGS_user'),
            $config->getValue('SBGS_pass'),
            $config->getValue('SBGS_mode')
        );
        // Предобработка заказа в СуперБилет
        switch ($state) {
            case 'Paid':
                // Отмечаем заказ оплаченным
                $sold_reply = $sbgs->SetSold($this->ticketsFillTransactionData($tickets));
                // Получаем информацию о билетах
                $tickets = $sbgs->GetState($tickets);
                break;
            
            case 'Cancelled':
                // Удаление резерва билетов
                $sbgs->ClearReservation($tickets);
                break;
        }

        // Отмечаем состояние заказа в БД
        $this->update($this, $state);

        // Массив данных для логирования
        $log = array();

        $log['event_id']       = $this->event_id;
        $log['tag']            = $this->tag;
        $log['reservation_id'] = $this->reservation_id;
        $log['name']           = $this->name;
        $log['email']          = $this->email;
        $log['phone']          = $this->phone;
        $log['total']          = $this->total;
        $log['type']           = $this->type;
        $log['state']          = $state;
        $log['tickets']        = $tickets;

        // Дополнительные данные в зависимости от состояния заказа
        switch ($state) {
            case 'AwaitingPayment':
                $log['payment_id'] = $this->payment_id;
                break;

            case 'Paid':
                $log['payment_id'] = $this->payment_id;
                $log['set_sold']   = $sold_reply;
                break;

            case 'Cancelled':
                $log['error_code']    = isset($this->payment_info['error_code']) ? $this->payment_info['error_code'] : '';
                $log['error_message'] = $this->payment_info['error_message'];
                break;
        }

        // Данные о заказе (для отладки)
        $log['order']      = $this;
        $log['order_data'] = $this->data;

        // Логирование состояния заказа
        $logger = new Logger();

        // Логирование в общий файл лога или в лог для метода `checkup`
        if ($this->checkup === true) {
            $logger->write($log, 'tickets_superbilet_checkup');
        } else {
            $logger->write($log);
        }

        // Постобработка заказа
        switch ($this->type) {
            case 'Self':
                if ($state == 'AwaitingRedemption') {
                    // Отправка уведомлений о бронировании
                    $this->email();
                }
                break;

            case 'Courier':
                if ($state == 'AwaitingDelivery') {
                    // Отправка уведомлений о бронировании
                    $this->email();
                }
                break;

            case 'Payment':
                if ($state == 'Paid') {
                    // Отправка уведомлений об онлайн-оплате
                    $this->email();
                }
                break;

            case 'ETicket':
                if ($state == 'Paid') {
                    // Генерация электронных билетов
                    $eticket = new ETicket();
                    $eticket->generate($this);
                }
                break;
        }

        // Удаление cookie `order_tag`, если заказ финализирован
        if ($state != 'New') {
            setcookie("order_tag", false, 0, '/');
        }

        if (!is_null($url)) {
            // Редирект на платёжную форму или шаг 3 с уведомлением о состоянии заказа
            $this->redirectTo($url, $message);
        }
    }

    private function ticketsFillTransactionData($tickets_in) {
        $tickets_out = array();
        foreach ($tickets_in as $key => $value) {
            $value['TransactionID'] = $value['session'];
            $value['PaymentDate'] = date('d.m.Y', time());
            $value['PaymentTime'] = date('H:m:s', time());
            $tickets_out[$key] = $value;
        }
        return $tickets_out;
    }

    /**
     * Хелпер-функция для удобных редиректов
     * 
     * @param string $url     URL для редиректа
     * @param string $message Опциональное сообщение, выводимое на странице после редиректа
     */
    private function redirectTo($url, $message = null) {
        global $mainframe;
        $mainframe->redirect($url, $message, $msgType = 'message');
        $mainframe->close();
    }

    /**
     * Удаление заказа из БД
     * 
     * @param string $order_tag Уникальный номер заказа
     * 
     */
    private function delete($order_tag) {
        $db =& JFactory::getDBO();

        $query  = "DELETE FROM `#__sb_orders` ";
        $query .= "WHERE `tag` = '$order_tag'";

        $db->setQuery($query);
        $db->query();
    }

    /**
     * Сеттер атрибутов `final_url`, `event_url`, `return_url`, `fail_url`
     */
    public function setOrderURL() {
        $this->final_url = JRoute::_(
            'index.php?option=com_afisha&view=final&id=' . $this->event_id . '&tag=' . $this->tag . '&Itemid=' . $this->Itemid
        );
        $this->event_url = JRoute::_(
            'index.php?option=com_afisha&view=event&id=' . $this->event_id . '&Itemid=' . $this->Itemid
        );

        $config =& JFactory::getConfig();
        $this->return_url = JRoute::_($config->getValue('superbilet_return_url'));
        $this->fail_url   = JRoute::_($config->getValue('superbilet_fail_url'));
    }

    /**
     * Информация о событии из БД
     * 
     * @param string $event_id Уникальный номер события
     * 
     * @return array Ассоциативный массив (событие, шоу, зал)
     */
    public function getEventInfo($event_id) {
        $db =& JFactory::getDBO();

        $query  = "SELECT E.*, E.id AS event_id, ";
        $query .= "E.date AS event_date, E.time AS event_time, CONCAT(E.date, ' ', E.time) AS event_datetime, ";
        $query .= "E.date < CURDATE() AS occured, E.sectors, ";
        $query .= "S.*, S.id AS show_id, S.name AS name, ";
        $query .= "V.name AS venue_name, ";
        $query .= "ST.id as stage_id, ST.name AS stage_name, S.genre AS genre ";
        $query .= "FROM  #__sb_events AS E ";
        $query .= "LEFT JOIN #__sb_shows  AS S  ON E.show_id  = S.id ";
        $query .= "LEFT JOIN #__sb_venues AS V  ON E.venue_id = V.id ";
        $query .= "LEFT JOIN #__sb_stages AS ST ON E.stage_id = ST.id ";
        $query .= "WHERE E.id = " . $event_id;
        $db->setQuery($query);
        $event = $db->loadAssoc();

        if (!empty($event)) {
            // Человекопонятная дата/время события
            $event['humanized_date']      = $this->formatDate($event['event_datetime'], 'day_month');
            $event['humanized_full_date'] = $this->formatDate($event['event_datetime'], 'day_month_year');
            $event['humanized_time'] = $this->formatDate($event['event_time'], 'time');
            $event['humanized_year'] = $this->formatDate($event['event_date'], 'year');

            // Постер события и логотип организатора
            $poster = rtrim($_SERVER['DOCUMENT_ROOT'], '/') . '/images/show/level2/' . $event['show_id'] . '.jpg';
            $logo   = rtrim($_SERVER['DOCUMENT_ROOT'], '/') . '/components/com_afisha/assets/img/belcanto.png';
            $event['poster'] = is_readable($poster) ? $poster : $logo;
            $event['logo']   = $logo;
        }

        #$logger = new Logger();
        #$logger->write(array('event_id' => $event_id, 'getEvent' => $event));

        return $event;
    }

    /**
     * Название сектора из БД
     * 
     * @param string $sector_id Уникальный номер сектора
     * 
     * @return string Название сектора
     */
    public function getSectorName($sector_id) {
        $db =& JFactory::getDBO();
        $query  = "SELECT `name` FROM  #__sb_sectors ";
        $query .= "WHERE `id` = " . $sector_id;
        $data = $db->setQuery($query);
        $sector = $db->loadResult();

        return $sector;
    }

    public function extractOrderTickets($order) {
        $tickets = array();
        foreach ($order as $key => $ticket) {
            if (is_array($ticket)) {
                $tickets[$key] = $ticket;
            }
        }
        return $tickets;
    }

    public function extractOrderData($order) {
        $data = array();
        foreach ($order as $key => $val) {
            if (!is_array($val)) {
                $data[$key] = $val;
            }
        }
        return $data;
    }

    /**
     * Получение суммы заказа в зависимости от его типа (реализуется в дочерних классах конкретного типа заказа)
     *
     * @return float Сумма заказа
     */
    // public function getTotal() {}

    /**
     * Если в сумме заказа ЕСТЬ дробная часть, отличная от нуля  - сумма округляется до сотых (т.е. до копеек).
     * Если в сумме заказа НЕТ  дробной части или она равна нулю - сумма округляется до целых (т.е. до рублей).
     *
     * @param  float         Сумма заказа в рублях
     *
     * @return integer|float Сумма заказа в рублях или в копейках
     */
    protected function prettifyTotal($total) {
        $total = floor($total) != $total ? round($total, 2) : round($total, 0);
        return $total;
    }

    /**
     * Обработка уникального номера заказа из cookie
     * 
     * @param string $raw Значение из cookie
     * 
     * @return string Обработанный уникальный номер заказа (32 символа)
     */
    public static function sanitizeOrderTag($raw) {
        $clean = preg_replace('/[^a-zA-Z0-9_]/', '', $raw);
        if (strlen($clean) > 32) {
            return substr($clean, 0, 32);
        }
        return str_pad($clean, 32, "_", STR_PAD_RIGHT);
    }

    /**
     * Конвертация даты/времени в человекопонятный текст
     * 
     * @param string $input  Дата для обработки
     * @param string $output Формат вывода
     * 
     * @return string Человекопонятное представление даты/времени в заданном формате
     */
    private function formatDate($input, $output) {
        $input = strtotime($input);
        $result = '';
        $day   = (int) date('j', $input);
        $month = (int) date('n', $input);
        switch($month) {
            case 1:  $month = 'января';   break;
            case 2:  $month = 'февраля';  break;
            case 3:  $month = 'марта';    break;
            case 4:  $month = 'апреля';   break;
            case 5:  $month = 'мая';      break;
            case 6:  $month = 'июня';     break;
            case 7:  $month = 'июля';     break;
            case 8:  $month = 'августа';  break;
            case 9:  $month = 'сентября'; break;
            case 10: $month = 'октября';  break;
            case 11: $month = 'ноября';   break;
            case 12: $month = 'декабря';  break;
        }
        $year = (int) date('Y', $input);
        $date = date('d.m.Y', $input);
        $time = date('G:i', $input);

        switch($output) {
            case 'day_month':
                $result = $day . ' ' . $month;
                break;
            case 'day_month_year':
                $result = $day . ' ' . $month . ' ' . $year . ' г.';
                break;
            case 'date':
                $result = $date;
                break;
            case 'time':
                $result = $time;
                break;
            case 'date_time':
                $result = $date . ' ' . $time;
                break;
            case 'year':
                $result = $year . ' год';
        }

        return $result;
    }

    protected function setOrderState() {}

    // Работа с email-уведомлениями

    protected function renderOrderId($html = false) {
        $output  = $html ? "<h2>" : "";
        $output .= isset($this->reservation_id) ? 'Заказ билетов № ' . $this->reservation_id : 'Заказ';
        $output .= $html ? "</h2>\n" : "\n\n";

        return $output;
    }

    protected function renderEventTitle($html = false) {
        $output  = $html ? "<h3>" : "";
        $output .= $this->event_info['humanized_full_date'] . " ";
        $output .= $this->event_info['humanized_time']      . " ";
        $output .= $this->event_info['name'];
        $output .= $html ? "</h3>\n" : "\n\n";

        $output .= $html ? "<h3>" : "";
        $output .= $this->event_info['venue_name'];
        $output .= $html ? "</h3>\n" : "\n\n";

        return $output;
    }

    protected function renderTickets($html = false) {
        $output  = $html ? "<p>" : "";
        $output .= "Билеты в заказе:";
        $output .= $html ? "</p>\n" : "\n";

        $output .= $html ? "<ul>\n" : "\n";
        foreach ($this->chosen_tickets as $t) {
            $output .= $html ? "<li>" : "* ";
            $output .= $t['sector_name']      . ", ";
            $output .= "ряд "   . $t['row']   . ", ";
            $output .= "место " . $t['seat']  . ", ";
            $output .= "цена "  . $t['price'] . " р.";
            $output .= $html ? "</li>\n" : "\n";
        }
        $output .= $html ? "</ul>\n" : "\n";

        return $output;
    }

    protected function renderTotal() {
        $output = "Общая сумма заказа: " . $this->getTotal() . " р.";

        return $output;
    }

    protected function renderContacts() {
        $output  = "\n\nИмя: " . $this->name  . "\n";
        $output .= "Email: "   . $this->email . "\n";
        $output .= "Телефон: " . $this->phone . "\n\n";

        return $output;
    }

    protected function renderTelephoneLinks() {
        $config =& JFactory::getConfig();

        $output = "<p>Тел. для справок ";

        $help_telephones = $config->getValue('help_telephones');
        $i = 1;
        foreach ($help_telephones as $ht_link => $ht_text) {
            $output .= "<a href=\"" . $ht_link . "\">" . $ht_text . "</a>";
            if ($i != count($help_telephones)) {
                $output .= ", ";
            }
            $i++;
        }

        $output .= ".</p>\n";

        return $output;
    }

    protected function renderSocialLinks() {
        $config =& JFactory::getConfig();

        $output = "<p>Вступайте в наши группы в социальных сетях:\n";

        $social_accounts = $config->getValue('social_accounts');
        foreach ($social_accounts as $sa) {
            $output .= "<a href=\"" . rtrim($sa['link'], '/') . "/?utm_source=bezantrakta&utm_medium=email&utm_campaign=order&utm_content=" . $sa['alias'] . "\"><img width=\"32\" height=\"32\" src=\"" . rtrim(JURI::root(), '/') . "/emailing/images/" . $sa['alias'] . ".jpg\" alt=\"" . $sa['title'] . "\" style=\"vertical-align: middle;\"></a>\n";
        }

        $output .= "<p>Получайте дополнительные скидки и бонусы. Будьте в курсе концертных событий!</p>\n";

        return $output;
    }

    /**
     * Формирование email-уведомления администратору
     * 
     * @return string HTML-код email-уведомления администратору
     */
    protected function renderAdminEmail() {
        // Заголовок с номером заказа
        $admin  = $this->renderOrderId();
        // Подзаголовок с названием события и зала
        $admin .= $this->renderEventTitle();
        // Список билетов в заказе
        $admin .= $this->renderTickets();

        // Итоговая сумма заказа в зависимости от его типа
        $admin .= $this->renderTotal();
        // Контактные данные покупателя
        $admin .= $this->renderContacts();
        // Способ получения и оплаты билетов
        $admin .= $this->renderDelivery();
        // Номер оплаты (опционально)
        $admin .= $this->renderPaymentId();

        return $admin;
    }

    /**
     * Отправка email-уведомлений покупателю и администратору
     */
    protected function emailAdmin($fromEmail, $fromName, $subject) {
        JUtility::sendMail(
            $fromEmail,
            $fromName,
            $fromEmail,
            $subject,
            $this->renderAdminEmail(),
            0
        );
    }

    /**
     * Формирование email-уведомления покупателю
     * 
     * @return string HTML-код email-уведомления покупателю
     */
    public function renderCustomerEmail() {
        // Заголовок с номером заказа
        $customer  = $this->renderOrderId(true);
        // Подзаголовок с названием события и зала
        $customer .= $this->renderEventTitle(true);
        // Список билетов в заказе
        $customer .= $this->renderTickets(true);

        // Итоговая сумма заказа в зависимости от его типа
        $customer .= $this->renderTotalCustomer(true);
        // Номер оплаты (опционально)
        $customer .= $this->renderPaymentId(true);
        // Описание заказа (из конфигурации сайта)
        $customer .= $this->renderDescriptionCustomer(true);
        // Телефоны для справок
        $customer .= $this->renderTelephoneLinks(true);
        // Ссылки на аккаунты в соцсетях
        $customer .= $this->renderSocialLinks(true);

        return $customer;
    }

    /**
     * Отправка email-уведомлений покупателю
     */
    protected function emailCustomer($fromEmail, $fromName, $subject, $ticketsAttachment = null) {
        JUtility::sendMail(
            $fromEmail,
            $fromName,
            $this->email,
            $subject,
            $this->renderCustomerEmail(),
            1
        );
    }

    /**
     * Отправка email-уведомлений покупателю и администратору
     */
    public function email($ticketsAttachment = null) {
        $config =& JFactory::getConfig();
        $fromEmail = $config->getValue('mailfrom');
        $fromName  = $config->getValue('fromname');
        $subject   = $this->renderOrderId();

        // Текстовое письмо администратору
        $this->emailAdmin($fromEmail, $fromName, $subject);

        // HTML-письмо покупателю (с вложением электронных билетов, если он их заказывал)
        $this->emailCustomer($fromEmail, $fromName, $subject, $ticketsAttachment);
    }
}

class OrderCash extends Order {
    public function preOrder($tickets) {
        $message = '<span id="success-message">Заказ успешно завершён. На введённый Вами email отправлена информация о заказанных Вами билетах.</span>';
        // Отмечаем заказ забронированным
        $this->mark($this->state, $tickets, $this->final_url, $message);
    }

    public function renderPaymentId($html = false) {
        return "";
    }
}

class OrderSelf   extends OrderCash {
    public $type = 'Self';
    public $has_delivery = 0;

    public function setOrderState() {
        $this->state = 'AwaitingRedemption';
    }

    public function getTotal() {
        return $this->prettifyTotal($this->total);
    }

    public function renderDelivery($html = false) {
        $output  = $html ? "<p>" : "";
        $output .= "Получение: в кассе.";
        $output .= $html ? "</p>\n" : "\n";

        $output .= $html ? "<p>" : "";
        $output .= "Оплата: наличными.";
        $output .= $html ? "</p>\n" : "\n";

        return $output;
    }

    public function renderTotalCustomer($html = false) {
        $output  = $html ? "<p>" : "";
        $output .= $this->renderTotal();
        $output .= $html ? "</p>\n" : "\n\n";

        return $output;
    }

    public function renderDescriptionCustomer() {
        $config =& JFactory::getConfig();
        // $output = $config->getValue('sb_self_email_description');
        $output = JText::sprintf($config->getValue('sb_self_email_description'), rtrim(JURI::root(), '/'));

        return $output;
    }
}

class OrderCourier extends OrderCash {
    public $type = 'Courier';
    public $has_delivery = 1;

    public function setOrderState() {
        $this->state = 'AwaitingDelivery';
    }

    public function getTotal() {
        $config =& JFactory::getConfig();
        $courier_price = $config->getValue('sb_courier_price');
        return $this->prettifyTotal($this->total + $courier_price);
    }

    public function renderDelivery($html = false) {
        $output  = $html ? "<p>" : "";
        $output .= "Получение: доставка курьером.";
        $output .= $html ? "</p>\n" : "\n";

        $output .= $html ? "<p>" : "";
        if (isset($this->address)) {
            $output .= "Адрес доставки: " . $this->address . ".";
        } else {
            $output .= "Адрес доставки: не указан.";
        }
        $output .= $html ? "</p>\n" : "\n";

        $output .= $html ? "<p>" : "";
        $output .= "Оплата: наличными.";
        $output .= $html ? "</p>\n" : "\n";

        return $output;
    }

    public function renderTotalCustomer($html = false) {
        $config =& JFactory::getConfig();
        $courier_price = (int) $config->getValue('sb_courier_price');

        $output  = $html ? "<p>" : "";
        $output .= $this->renderTotal();
        if ($courier_price > 0) {
            $output .= " (в сумму заказа включена стоимость доставки курьером).";
        } else {
            $output .= " (доставка курьером бесплатная).";
        }
        $output .= $html ? "</p>\n" : "\n\n";

        return $output;
    }

    public function renderDescriptionCustomer() {
        $config =& JFactory::getConfig();
        $output = $config->getValue('sb_courier_email_description');

        return $output;
    }
}

class OrderOnline extends Order {
    /** @param string $payment_id Уникальный номер оплаты */
    public $payment_id;
    /** @param array $payment_info Информация об оплате (код ошибки, сообщение об ошибке) */
    public $payment_info;

    public function preOrder($tickets) {
        $config =& JFactory::getConfig();
        $payment = getPayment('superbilet', $config->getValue('commission_included'));

        // Опциональные дополнительные параметры для формирования оплаты
        $params = array();
        $params['event_id']   = $this->event_id;   // Идентификатор события
        $params['tag']        = $this->tag;        // Идентификатор заказа
        $params['name']       = $this->name;       // ФИО покупателя
        $params['email']      = $this->email;      // Email покупателя
        $params['phone']      = $this->phone;      // Телефон покупателя
        $params['return_url'] = $this->return_url; // URL успешного завершения оплаты
        $params['fail_url']   = $this->fail_url;   // URL НЕуспешного завершения оплаты

        $create_payment = $payment->create($this->reservation_id, $this->total, $params);

        // Успешный или НЕуспешный запрос на оплату
        switch ($create_payment['result']) {
            case 'success':
                // Получение номера оплаты
                $this->payment_id = $create_payment['payment_id'];

                // Отмечаем заказ с запрошенной оплатой с редиректом на форму оплаты платёжного сервиса
                $this->mark($this->state, $tickets, $create_payment['payment_url']);
                break;

            case 'error':
                $this->payment_info['error_code']    = $create_payment['error_code'];
                $this->payment_info['error_message'] = $create_payment['error_message'];
                $message = '<span id="error-message">Запрос оплаты завершился с ошибкой. ' . $create_payment['error_code'] . ' ' . $create_payment['error_message'] . '. <a href="' . $this->event_url . '">Попробуйте заказать билеты ещё раз</a>.</span>';
                // Отмечаем заказ отменённым из-за НЕуспешного запроса на оплату
                $this->mark('Cancelled', $tickets, $this->final_url, $message);
                break;
        }
    }

    public function getTotal() {
        $config =& JFactory::getConfig();
        $payment = getPayment('superbilet', $config->getValue('commission_included'));

        return $this->prettifyTotal($payment->overallSum($this->total));
    }

    public function renderPaymentId($html = false) {
        $output  = $html ? "<p>" : "";
        $output .= "Номер оплаты: " . $this->payment_id . ".";
        $output .= $html ? "</p>\n" : "\n\n";

        return $output;
    }

    public function renderTotalCustomer($html = false) {
        $config =& JFactory::getConfig();
        $commission_included = $config->getValue('commission_included');

        $output  = $html ? "<p>" : "";
        $output .= $this->renderTotal();
        $output .= $commission_included === true ? "" : " (в сумму заказа включена комиссия платёжной системы).";
        $output .= $html ? "</p>\n" : "\n\n";

        return $output;
    }
}

class OrderPayment extends OrderOnline {
    public $type = 'Payment';
    public $has_delivery = 0;

    public function setOrderState() {
        $this->state = 'AwaitingPayment';
    }

    public function renderDelivery($html = false) {
        $output  = $html ? "<p>" : "";
        $output .= "Получение: в кассе.";
        $output .= $html ? "</p>\n" : "\n";

        $output .= $html ? "<p>" : "";
        $output .= "Оплата: онлайн-оплата.";
        $output .= $html ? "</p>\n" : "\n";

        return $output;
    }

    public function renderDescriptionCustomer() {
        $config =& JFactory::getConfig();
        $output = JText::sprintf($config->getValue('sb_payment_email_description'), rtrim(JURI::root(), '/'));

        return $output;
    }
}

class OrderETicket extends OrderOnline {
    public $type = 'ETicket';
    public $has_delivery = 0;

    public function setOrderState() {
        $this->state = 'AwaitingPayment';
    }

    public function renderDelivery($html = false) {
        $output  = $html ? "<p>" : "";
        $output .= "Получение: электронный билет на email.";
        $output .= $html ? "</p>\n" : "\n";

        $output .= $html ? "<p>" : "";
        $output .= "Оплата: онлайн-оплата.";
        $output .= $html ? "</p>\n" : "\n";

        return $output;
    }

    public function renderDescriptionCustomer() {
        $config =& JFactory::getConfig();
        $output = $config->getValue('sb_eticket_email_description');

        return $output;
    }

    /**
     * Отправка email-уведомлений покупателю
     * 
     * @param array $ticketsAttachment Сгенерированные PDF-файлы с билетами
     */
    public function emailCustomer($fromEmail, $fromName, $subject, $ticketsAttachment) {
        JUtility::sendMail(
            $fromEmail,
            $fromName,
            $this->email,
            $subject,
            $this->renderCustomerEmail(),
            1,
            null,
            null,
            $ticketsAttachment
        );
    }
}
