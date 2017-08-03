<?php 

/**
 * Фабрика для создания экземпляров дочерних классов Payment.
 * Выбор активного сервиса онлайн-оплаты и инстанцирование его дочернего класса.
 * 
 * @param string $ticket_service Текущий билетный сервис
 *
 * @return Sberbank|SNGB Экземпляр дочернего класса активной для этого билетного сервиса онлайн-оплаты
 */
function getPayment($ticket_service, $commission_included = null) {
    $config = new JConfig();

    // Выбор активного сервиса онлайн-оплаты
    $active_payment_param = $ticket_service . '_active_payment';
    $active_payment_value = $config->$active_payment_param;

    // Инстанцирование класса активного сервиса онлайн-оплаты
    return new $active_payment_value($commission_included);
}

/**
  * Абстрактный класс, опосредованно связывающий сервисы продажи билетов с сервисами онлайн-оплаты.
  * Реализующие его дочерние классы сервисов онлайн-оплаты инстанцируются в зависимости от того, какая оплата активна для текущего билетного сервиса. Это указано в конфигурации сайта в параметрах вида "{TICKET_SERVICE_ALIAS}_active_payment".
  * Отдельные методы реализующих его классов сервисов онлайн-оплаты возвращают одни и те же формализованные ответы для унификации работы с ними.
  */
abstract class Payment {
    /** @var string $success_url URL для обработки успешной оплаты */
    protected $success_url;
    /** @var string $error_url URL для обработки НЕуспешной оплаты */
    protected $error_url;
    /** @var string $description Описание онлайн-оплаты */
    protected $description;
    /** @var float $commission Процент комиссии сервиса онлайн-оплаты */
    protected $commission = 0.0;
    /** @var integer $timeout Таймаут до завершения оплаты в минутах */
    protected $timeout = 15;

    /**
     * Информация об онлайн-оплате
     *
     * @return string HTML-описание онлайн-оплаты
     */
    public function description() {
        return $this->description;
    }

    /**
     * Получение комиссии сервиса онлайн-оплаты
     *
     * @return float Процент комиссии
     */
    public function commission() {
        return $this->commission;
    }

    /**
     * Получение таймаута на проведение оплаты
     *
     * @return string Время сессии онлайн-оплаты в минутах
     */
    public function timeout() {
        return $this->timeout;
    }

    /**
     * Получение суммы заказа с комиссией активного сервиса онлайн-оплаты
     *
     * @param float $total Сумма заказа в рублях БЕЗ комиссии
     *
     * @return float Сумма заказа в рублях С комиссией
     */
    public function overallSum($total) {
        $overallSum = ($total + (($total * $this->commission) / 100));

        // Если в десятичной части больше двух знаков - округляется до сотых, т.е. до копеек
        if (floor($overallSum) != $overallSum ) {
            $overallSum = round($overallSum, 2);
        }

        return $overallSum;
    }

    /**
     * Запрос на создание новой оплаты для нового заказа
     *
     * @param string $reservation_id Уникальный номер заказа
     * @param float  $total          Сумма заказа в рублях (БЕЗ комиссии)
     * @param array  $params         Дополнительные параметры (если требуются)
     *
     * @return array Унифицированный ответ (должен содержать уникальный URL платёжной формы)
     * <ul>
     * <li>если запрос успешен
     *     <ul>
     *     <li> `result`      string - `success` </li>
     *     <li> `payment_url` string - URL платёжной формы </li>
     *     <li> `payment_id`  string - Уникальный номер оплаты </li>
     *     </ul>
     * </li>
     * <li>если запрос НЕуспешен
     *     <ul>
     *     <li> `result`        string - `error` </li>
     *     <li> `error_code`    string - Код ошибки </li>
     *     <li> `error_message` string - Сообщение об ошибке </li>
     *     </ul>
     * </li>
     * </ul>
     */
    abstract protected function create($reservation_id, $total, $params = null);

    /**
     * Запрос на получение статуса ранее созданной оплаты
     *
     * @param string $payment_id Уникальный номер оплаты
     *
     * @return array Унифицированный ответ
     * <ul>
     * <li>если оплата успешна
     *     <ul>
     *     <li> `result`           string  - `success` </li>
     *     <li> `reservation_id`   string  - Уникальный номер заказа </li>
     *     <li> `payment_id`       integer - Уникальный номер оплаты </li>
     *     <li> `payment_amount`   float   - Сумма оплаты </li>
     *     <li> `payment_refunded` boolean - Был ли по оплате проведён возврат </li>
     *     </ul>
     * </li>
     * <li>если оплата НЕуспешна
     *     <ul>
     *     <li> `result`        string - `error` </li>
     *     <li> `error_code`    string - Код ошибки </li>
     *     <li> `error_message` string - Сообщение об ошибке </li>
     *     </ul>
     * </li>
     * </ul>
     */
    abstract protected function status($payment_id);

    /**
     * Возврат средств по ранее подтверждённой оплате (иногда может проводиться в личном кабинете сервиса онлайн-оплаты и не требоваться по API)
     *
     * @param string $payment_id Уникальный номер оплаты
     * @param float  $total      Общая сумма заказа в рублях (БЕЗ комиссии)
     *
     * @return array Унифицированный ответ
     */
    abstract protected function refund($payment_id, $total);

}
