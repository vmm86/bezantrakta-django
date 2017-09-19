<?php

$logfile = rtrim($_SERVER['DOCUMENT_ROOT'], '/') . '/../log/payment_sngb_log';
file_put_contents($logfile, "\n# " . print_r(date('Y-m-d H:i:s'), true) . " #" . "\n\n", FILE_APPEND);
file_put_contents($logfile, "error_response = " . print_r($_REQUEST, true) . "\n", FILE_APPEND);

$response = array_change_key_case($_REQUEST, CASE_LOWER);

$finalURL  = "REDIRECT=http://" . rtrim($_SERVER['SERVER_NAME'], '/');
$finalURL .= "/index.php?option=com_afisha&controller=gettickets&task=sngbErrorProxy";

$response_vars = array(
    "udf1"         => "event_id",
    "udf4"         => "tag",
    "trackid"      => "trackid",
    "paymentid"    => "paymentid",
    "responsecode" => "responsecode",
    "result"       => "result",
    "error"        => "error",
    "errortext"    => "errortext"
);

foreach ($response_vars as $rv_in => $rv_out) {
    isset($response[$rv_in]) ? $finalURL .= "&$rv_out=" . $response[$rv_in] : "";
}

echo $finalURL;

?>