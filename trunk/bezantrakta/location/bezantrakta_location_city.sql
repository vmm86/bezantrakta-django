-- phpMyAdmin SQL Dump
-- version 4.6.6
-- https://www.phpmyadmin.net/
--
-- Хост: localhost
-- Время создания: Июн 13 2017 г., 10:30
-- Версия сервера: 5.7.18-0ubuntu0.16.04.1
-- Версия PHP: 7.0.18-0ubuntu0.16.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `belcanto_bezantrakta_django`
--

--
-- Дамп данных таблицы `bezantrakta_location_city`
--

INSERT INTO `bezantrakta_location_city` (`id`, `title`, `slug`, `timezone`, `is_published`) VALUES
(391, 'Красноярск', 'ksn', 'Asia/Krasnoyarsk', 0),
(473, 'Воронеж', 'vrn', 'Europe/Moscow', 1),
(831, 'Нижний Новгород', 'nnov', 'Europe/Moscow', 0),
(846, 'Самара', 'sam', 'Europe/Samara', 0),
(861, 'Краснодар', 'kdr', 'Europe/Moscow', 0),
(863, 'Ростов-на-Дону', 'rnd', 'Europe/Moscow', 0),
(3462, 'Сургут', 'sur', 'Asia/Yekaterinburg', 0),
(3466, 'Нижневартовск', 'nvar', 'Asia/Yekaterinburg', 0),
(3532, 'Оренбург', 'ore', 'Asia/Yekaterinburg', 0),
(3812, 'Омск', 'omsk', 'Asia/Omsk', 0),
(3952, 'Иркутск', 'irk', 'Asia/Irkutsk', 0),
(4712, 'Курск', 'kur', 'Europe/Moscow', 0),
(4722, 'Белгород', 'bel', 'Europe/Moscow', 1),
(4725, 'Старый Оскол', 'sosk', 'Europe/Moscow', 0),
(4742, 'Липецк', 'lip', 'Europe/Moscow', 0),
(4752, 'Тамбов', 'tam', 'Europe/Moscow', 0),
(4812, 'Смоленск', 'smo', 'Europe/Moscow', 0),
(4822, 'Тверь', 'tve', 'Europe/Moscow', 0),
(4832, 'Брянск', 'bry', 'Europe/Moscow', 0),
(4842, 'Калуга', 'kal', 'Europe/Moscow', 0),
(4852, 'Ярославль', 'yar', 'Europe/Moscow', 0),
(4862, 'Орел', 'orel', 'Europe/Moscow', 0),
(4872, 'Тула', 'tula', 'Europe/Moscow', 0),
(4912, 'Рязань', 'rzn', 'Europe/Moscow', 0),
(4922, 'Владимир', 'vdm', 'Europe/Moscow', 0),
(4932, 'Иваново', 'iva', 'Europe/Moscow', 0),
(4942, 'Кострома', 'ktr', 'Europe/Moscow', 0),
(8112, 'Псков', 'pskov', 'Europe/Moscow', 0),
(8162, 'Великий Новгород', 'vnov', 'Europe/Moscow', 0),
(8182, 'Архангельск', 'akh', 'Europe/Moscow', 0),
(8412, 'Пенза', 'penza', 'Europe/Moscow', 0),
(8422, 'Ульяновск', 'uly', 'Europe/Moscow', 0),
(8442, 'Волгоград', 'vol', 'Europe/Volgograd', 0),
(8452, 'Саратов', 'sar', 'Europe/Volgograd', 1),
(8482, 'Тольятти', 'tol', 'Europe/Samara', 0),
(81153, 'Великие Луки', 'vluki', 'Europe/Moscow', 0),
(81842, 'Северодвинск', 'sdvn', 'Europe/Moscow', 0);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
