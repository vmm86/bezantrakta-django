<?php
/** Класс для хранения информации о заказе и CRUD-операций с заказом в БД */
class Order {
    public $final_url;
    public $event_url;

    public $return_url;
    public $fail_url;

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
        // Постобработка заказа
        switch ($this->type) {
            case 'Self':
            case 'Courier':
            case 'Payment':
                if ($state == 'ordered') {
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

        if (!is_null($url)) {
            // Редирект на платёжную форму или шаг 3 с уведомлением о состоянии заказа
            $this->redirectTo($url, $message);
        }
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
