<?php

/** Дочерний класс абстрактного класса Payment для отправки запросов к API Сбербанка */
class Sberbank extends Payment {
    function __construct($commission_included = null) {
        if (is_null($commission_included)) {
            $this->commission = $config->sberbank_commission;
        } else {
            if ($commission_included === true) {
                $this->commission = 0.0;
            }
        }
    }

    /**
     * Общий метод-конструктор любых запросов к API Сбербанка
     *
     * @param string  $method HTTP-метод запроса (GET или POST)
     * @param string  $url    Окончание URL, на который отправляется запрос
     * @param array   $data   Тело запроса (отправляется как обычные urlencoded данные формы)
     *
     * @return object Ответ на сформированный запрос
     */
    private function request($method, $url, $data) {
        $fullurl = $this->url . $url;

        // Параметры для авторизации любых запросов
        $data['userName'] = $this->user_name;
        $data['password'] = $this->password;

        // Необходимые параметры для GET-запросов или POST-запросов
        switch ($method) {
            case 'GET':
                $fullurl .= '?' . http_build_query($data);
                $options = array(
                    CURLOPT_URL => $fullurl,
                    CURLOPT_HTTPHEADER => array(
                        'Accept:application/json'
                    ),
                    CURLOPT_RETURNTRANSFER => true,
                    // CURLOPT_FOLLOWLOCATION => true,
                    CURLOPT_TIMEOUT => 16,
                    CURLOPT_MAXREDIRS => 10
                );
                break;
            
            case 'POST':
                $options = array(
                    CURLOPT_URL => $fullurl,
                    CURLOPT_CUSTOMREQUEST => 'POST',
                    CURLOPT_POSTFIELDS => http_build_query($data),
                    CURLOPT_HTTPHEADER => array(
                        'Accept:application/json'
                    ),
                    CURLOPT_RETURNTRANSFER => true,
                    // CURLOPT_FOLLOWLOCATION => true,
                    CURLOPT_TIMEOUT => 16,
                    CURLOPT_MAXREDIRS => 10
                );
                break;
        }

        $curl = curl_init($fullurl);
        curl_setopt_array($curl, $options);
        $response = curl_exec($curl);

        curl_close($curl);
        
        return json_decode($response);
    }

    // Функции для формирования конкретных запросов к API

    public function create($reservation_id, $total, $params = null) {
        $method = 'POST';
        $url = 'register.do';

        $create = array();
        $create['orderNumber'] = $reservation_id;
        // Полная сумма заказа с комиссией в копейках
        $create['amount'] = $this->overallSum($total) * 100;
        // URL возврата после успешной или неуспешной оплаты
        $create['returnUrl'] = $params['return_url'].'&event_id='.$params['event_id'].'&tag='.$params['tag'];
        $create['failUrl']   = $params['fail_url']  .'&event_id='.$params['event_id'].'&tag='.$params['tag'];
        // Время на оплату заказа в минутах (по умолчанию - 20 минут)
        $create['sessionTimeoutSecs'] = $this->timeout * 60;
        // Кастомные параметры заказа (можно отправлять любые данные)
        $jsonParams = new stdClass();
        $jsonParams->email = $params['email'];
        $create['jsonParams'] = json_encode($jsonParams);

        // Запрос на оплату
        $create_response = $this->request($method, $url, $create);

        // Унификация ответа

        $response = array();

        // Если запрос успешен
        if (!isset($create_response->errorCode) || $create_response->errorCode == 0) {
            $response['result'] = 'success';
            // URL платёжной формы
            $response['payment_url'] = $create_response->formUrl;
            // Уникальный номер оплаты
            $response['payment_id'] = $create_response->orderId;
        // Если запрос НЕуспешен
        } else {
            $response['result'] = 'error';
            // Код ошибки
            $response['error_code'] = $create_response->errorCode;
            // Сообщение об ошибке
            $response['error_message'] = $create_response->errorMessage;
        }

        return $response;
    }

    public function status($payment_id) {
        $method = 'POST';
        $url = 'getOrderStatusExtended.do';

        $status = array();
        $status['orderId'] = $payment_id;

        // Отправка запроса для получения информации о статусе оплаты
        $status_response = $this->object_to_array_lowercase_keys($this->request($method, $url, $status));

        // Унификация ответа

        $response = array();

        // Если запрос успешен
        if (
                (int)$status_response['errorcode'] == 0 &&
                (int)$status_response['paymentamountinfo']['approvedamount'] > 0 &&
                (int)$status_response['paymentamountinfo']['refundedamount'] == 0
            )
        {
            $response['result'] = 'success';
        // Если запрос НЕуспешен
        } else {
            $response['result'] = 'error';
            // Код ошибки
            $response['error_code'] = $status_response['actioncode'];
            // Сообщение об ошибке
            $response['error_message'] = $status_response['actioncodedescription'];
        }

        $response['reservation_id']   = $status_response['ordernumber'];
        $response['payment_id']       = $status_response['attributes'][0]['value'];
        $response['payment_amount']   = (int)$status_response['paymentamountinfo']['approvedamount'] / 100;
        $response['payment_refunded'] = (int)$status_response['paymentamountinfo']['refundedamount'] != 0 ? true : false;

        return $response;
    }

    public function refund($payment_id, $total) {
        $method = 'POST';
        $url = 'refund.do';

        $refund = array();
        // Номер оплаты Сбербанка
        $refund['orderId'] = $payment_id;
        // Полная сумма заказа с комиссией в копейках
        $refund['amount'] = $this->overallSum($total) * 100;

        $refund_response = $this->object_to_array_lowercase_keys($this->request($method, $url, $refund));

        // Унификация ответа

        $response = array();

        // ...

        return $refund_response;
    }

    /**
     * Перевод всех ключей в ответе метода в нижний регистр.
     * Регистр ключей различается в ответах разных методов! (рукалицо)
     *
     * @param object $object Ответ метода в виде объекта
     *
     * @return array Ответ метода в виде массива с ключами на первом и втором уровне в нижнем регистре
     */
    private function object_to_array_lowercase_keys($object) {
        $array = array_change_key_case(json_decode(json_encode($object), true), CASE_LOWER);
        foreach ($array as $key => $value) {
            if (gettype($value) == 'array') {
                $array[$key] = array_change_key_case($array[$key], CASE_LOWER);
            }
        }
        return $array;
    }

}
