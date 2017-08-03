<?php

/** Класс для отправки запросов к API Радарио */
class RadarioAPI {
    /**
     * Общий метод-конструктор любых запросов к API Радарио
     *
     * @param  string $method HTTP-метод запроса (GET или POST)
     * @param  string $url    Окончание URL, на который отправляется запрос
     * @param  object $data   Тело запроса (при GET-запросах не требуется, при POST-запросах отправляется в JSON)
     *
     * @return array|object Ответ на сформированный запрос
     */
    private function request($method, $url, $data = null) {
        // Разный вывод данных в зависимости от источника запроса
        //// JavaScript-фронтенд
        if ($xhr == "xmlhttprequest") {
            echo $response;
            exit;
        //// PHP-бэкенд
        } else {
            return json_decode($response);
            exit;
        }

    }

    /**
     * Обработка ответа запроса к API и добавление необходимых дополнительных полей
     *
     * @param string $action   Название запрошенного метода
     * @param object $response Ответ на запрос
     *
     * @return object Обработанный ответ на запрос
     */
    private function prettify($action, $response) {
        switch ($action) {
            case 'events':
            case 'group_events':
                foreach ($response->data->items as $key => $val) {
                    // Убрать кавычки из названия события
                    // $response->data->items[$key]['title']  = str_replace('"', "''", $response->data->items[$key]['title']);
                    // Человекопонятная дата события
                    $response->data->items[$key]->humanizedDate = $this->formatDate($val->beginDate, 'day_month');
                    $response->data->items[$key]->humanizedDateTime = $this->formatDate($val->beginDate, 'date_time');
                    // Файлы изображений от Радарио
                    $response->data->items[$key]->images = json_decode($response->data->items[$key]->images);
                    // Абсолютная ссылка на файл постера от Радарио или заглушку
                    $response->data->items[$key]->poster = (
                        isset($response->data->items[$key]->images[0]->id)
                        ? 'http://images.radario.ru/images/webeventorder/' . $response->data->items[$key]->images[0]->id
                        : 'http://' . rtrim($_SERVER['SERVER_NAME'], '/') . '/components/com_radario/assets/img/' . $response->data->items[$key]->companyId . '.jpg'
                    );
                    // Обработка ID группы похожих событий
                    $response->data->groupId = !is_null($response->data->items[$key]->groupId) ? (int)$response->data->items[$key]->groupId : null;
                }
                $response = $response->data->items;
                break;

            case 'event':
                    // Человекопонятная дата/время события
                    $response->data->humanizedDate     = $this->formatDate($response->data->beginDate, 'date');
                    $response->data->humanizedTime     = $this->formatDate($response->data->beginDate, 'time');
                    $response->data->humanizedFullDate = $this->formatDate($response->data->beginDate, 'day_month');
                    $response->data->humanizedYear     = $this->formatDate($response->data->beginDate, 'year');
                    // Файлы изображений от Радарио
                    $response->data->images = json_decode($response->data->images);
                    // // Абсолютная ссылка на файл постера от Радарио или заглушку
                    $response->data->poster = (
                        isset($response->data->images[0]->id)
                        ? 'http://images.radario.ru/images/webeventorder/' . $response->data->images[0]->id
                        : 'http://' . rtrim($_SERVER['SERVER_NAME'], '/') . '/components/com_radario/assets/img/' . $response->data->companyId . '.jpg'
                    );
                    $response->data->logo = 'http://' . rtrim($_SERVER['SERVER_NAME'], '/') . '/components/com_radario/assets/img/' . $response->data->companyId . '.jpg';
                    // ID группы похожих событий
                    $response->data->groupId = !is_null($response->data->groupId) ? (int)$response->data->groupId : null;
                $response = $response->data;
                break;

            case 'ticket_types':
                // Сортировка по возрастанию цены (по умолчанию сортируются в порядке создания)
                function compareByPrice($a, $b) {
                    if ($a->price < $b->price) {
                        return -1;
                    } else if ($a->price > $b->price) {
                        return 1;
                    } else {
                        return 0;
                    }
                }
                $response = $response->data->items;
                usort($response, 'compareByPrice');
                // Добавление поля с количеством билетов в продаже
                foreach ($response as $key => &$val) {
                    $response[$key]->withSeats = ($response[$key]->withSeats ? true : false);
                    $response[$key]->freeTicketCount = (int) $val->ticketCount - (int) $val->soldTicketCount;
                }
                unset($val);
                break;

            default:
                break;
        }
        return $response;
    }

}
