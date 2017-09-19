<?php 
/** Дочерний класс абстрактного класса Payment для отправки запросов к API СургутНефтеГазБанка */
class SNGB extends Payment {
   /** @var string $url Базовый URL для отправки запросов к API СургутНефтеГазБанка (тестовая или боевая платёжная среда) */
    private $url;
   /** @var string $merchant_id Идентификатор мерчанта */
    private $merchant_id;
   /** @var string $merchant_id Идентификатор платёжного терминала */
    private $terminal_alias;
   /** @var string $psk Pre-Shared Key (PSK) секретный ключ для аутентификации запросов */
    private $psk;
   /** @var string $token Token для аутентификации запросов */
    private $token;

    function __construct($commission_included = null) {
        // Выбор тестового или боевого режима оплаты
        switch ($config->payment_type) {
            case 'ECommerce':
                $this->merchant_id    = $config->test_merchant_id;
                $this->terminal_alias = $config->test_terminal_alias;
                $this->url            = $config->test_url;
                $this->psk            = $config->test_psk;
                $this->token          = $config->test_token;
                break;
            
            case 'Gateway':
                $this->merchant_id    = $config->prod_merchant_id;
                $this->terminal_alias = $config->prod_terminal_alias;
                $this->url            = $config->prod_url;
                $this->psk            = $config->prod_psk;
                $this->token          = $config->prod_token;
                break;
        }

        $this->description = $config->sngb_description;

        if (is_null($commission_included)) {
            $this->commission = $config->sngb_commission;
        } else {
            if ($commission_included === true) {
                $this->commission = 0.0;
            }
        }

        $this->timeout = $config->sngb_timeout;
    }

    /**
     * Общий метод-конструктор любых запросов к API СургутНефтеГазБанка
     *
     * @param string  $method HTTP-метод запроса (GET или POST)
     * @param string  $url    Окончание URL, на который отправляется запрос
     * @param array   $data   Тело запроса (отправляется как обычные urlencoded данные формы)
     *
     * @return object Ответ на сформированный запрос
     */
    private function request($method, $url, $data) {
        $fullurl = !empty($data) ? $this->url . $url : $url;

        // Хэш для авторизации запросов
        if (!empty($data)) {
            $salt = $this->merchant_id . $data['amt'] . $data['trackid'] . $data['action'] . $this->psk;         
            $data['udf5'] = sha1($salt);
        }

        // Необходимые параметры для GET-запросов или POST-запросов
        switch ($method) {
            case 'GET':
                $fullurl .= !empty($data) ? '?' . http_build_query($data) : '';
                $options = array(
                    CURLOPT_URL => $fullurl,
                    CURLOPT_SSL_VERIFYPEER => false,
                    CURLOPT_RETURNTRANSFER => true
                );
                break;
            
            case 'POST':
                $options = array(
                    CURLOPT_URL => $fullurl,
                    CURLOPT_CUSTOMREQUEST => 'POST',
                    CURLOPT_POSTFIELDS => http_build_query($data),
                    CURLOPT_SSL_VERIFYPEER => false,
                    CURLOPT_RETURNTRANSFER => true
                );
                break;
        }
        print_r($options);

        $curl = curl_init($fullurl);
        curl_setopt_array($curl, $options);

        $response = curl_exec($curl);

        curl_close($curl);

        return $response;
    }

    // Функции для формирования конкретных запросов к API

    public function create($reservation_id, $total, $params = null) {
        $method = 'POST';
        $url = 'PaymentInitServlet';

        $create = array();
        $create['merchant'] = $this->merchant_id;
        $create['terminal'] = $this->terminal_alias;
        // 1 - Purchase (полная покупка), 4 - Authorization (только авторизация)
        $create['action'] = 1;
        // Полная сумма заказа
        $create['amt'] = $this->overallSum($total);
        $create['trackid'] = $reservation_id;
        // Кастомные параметры заказа
        $create['udf1'] = $params['event_id']; // Идентификатор события
        // $create['udf2'] = $reservation_id; // Номер заказа
        // $create['udf3'] = $params['email']; // Email покупателя
        $create['udf4'] = isset($params['tag']) ? $params['tag'] : null; // Уникальный идентификатор заказа (32 символа)

        // Отправка запроса для инициализации оплаты
        $create_response = $this->request($method, $url, $create);

        # string "https://ecm.sngb.ru:443/ECommerce/hppaction?formAction=com.aciworldwide.commerce.gateway.payment.action.HostedPaymentPageAction&PaymentID=8038283381570110"

        // Унификация ответа

        // Разбираем URL в ответе
        $parts = parse_url($create_response);
        parse_str($parts['query'], $query);
        $query = array_change_key_case($query, CASE_LOWER);
        $query['paymentid'] = trim($query['paymentid'], '_');

        $response = array();

        // Если запрос успешен
        if (isset($query['paymentid']) && !isset($query['error'])) {
            $response['result'] = 'success';
            // URL платёжной формы
            $response['payment_url'] = $create_response;
            // Уникальный номер платежа
            $response['payment_id'] = $query['paymentid'];
        // Если запрос НЕуспешен
        } else {
            $response['result'] = 'error';
            // Код ошибки
            $response['error_code'] = $query['error'];
            // Сообщение об ошибке
            $response['error_message'] = $query['errortext'];
        }

        return $response;
    }

    public function status($payment_id) {
        $method = 'GET';
        $url = 'https://' . $this->token . ':@ecm.sngb.ru/' . $this->payment_type .'/v1/payments/' . $payment_id;
        $status = array();

        // Отправка запроса для получения информации о статусе оплаты
        $status_response = json_decode($this->request($method, $url, $status));

        // var_dump($status_response);

        # object {
        #     ["data"]   => array  ()
        #     ["count"]  => string "0"
        #     ["url"]    => string "/Gateway/v1/payments"
        #     ["object"] => string "list"
        # }

        # object {
        #     ["data"] => array (
        #         [0] => object (
        #             ["authorization"] => bool true/false
        #             ["tranid"]   => string "6115947381570110"
        #             ["amount"]   => float 1.02
        #             ["livemode"] => bool true/false
        #             ["created"]  => int 1484131109265
        #             ["captured"] => bool true/false
        #             ["currency"] => string "rub"
        #             ["refunded"] => bool true/false
        #             ["id"]       => int 8038283381570110
        #             ["track"]    => string "4583"
        #             ["object"]   => string "payment"
        #         )
        #     )
        #     ["count"]  => int 1
        #     ["url"]    => string "/Gateway/v1/payments"
        #     ["object"] => string "list"
        # }

        // Унификация ответа

        $response = array();

        // Если запрос успешен
        if (!empty($status_response->data) && $status_response->data[0]->authorization && $status_response->data[0]->captured) {
            $response['result'] = 'success';
            // Уникальный номер платежа
            $response['reservation_id']   = $status_response->data[0]->track;
            $response['payment_id']       = number_format($status_response->data[0]->id, 0, '.', ''); // strval($status_response->data[0]->id);
            $response['payment_amount']   = $status_response->data[0]->amount;
            $response['payment_refunded'] = $status_response->data[0]->refunded ? true : false;
        // Если запрос НЕуспешен
        } else {
            $response['result'] = 'error';
            // Код ошибки
            $response['error_code'] = '';
            // Сообщение об ошибке
            $response['error_message'] = 'Оплата завершилась неудачно';
        }

        return $response;
    }

    public function refund($payment_id, $total) {
        $method = 'POST';
        $url = 'PaymentTranServlet';

        $refund = array();
        $refund['merchant'] = $this->merchant_id;
        $refund['terminal'] = $this->terminal_alias;
        // 1 - Purchase (полная покупка), 4 - Authorization (только авторизация)
        $refund['action']   = 2;
        // Полная сумма заказа
        #$refund['amt']       = $this->overallSum($total);
        #$refund['trackid']   = $reservation_id;
        $refund['paymentid'] = $payment_id;
        #$refund['tranid'] = $tranid;
        // Кастомные параметры заказа
        $refund['udf1']     = $params['event_id']; // Идентификатор события
        // $refund['udf2']     = $reservation_id; // Номер заказа
        // $refund['udf3']     = $params['email']; // Email покупателя
        $refund['udf4']     = isset($params['tag']) ? $params['tag'] : null; // Уникальный идентификатор заказа (32 символа)

        // Отправка запроса для инициализации оплаты
        $refund_response = $this->request($method, $url, $refund);

        // Унификация ответа

        $response = array();

        // ...

        return $response;
    }

}
