<h2 id="event-venue">
    <span id="stagehall_name"><?php echo $this->radarioEvent->placeTitle; ?></span>
</h2>

<div class="order-header">

    <div id="basket-container">

        <div class="show-events">
    <?php
        // Выводятся только 2 или более похожих событий в группе
        if (isset($this->radarioEvent_group_events) and count($this->radarioEvent_group_events) > 1) {
    ?>
            <h3 id="related-events-header"><?php echo JText::_('COM_RADARIO_STEP1_GROUP_EVENTS'); ?></h3>
            <ul id="related-events">
        <?php
            foreach ($this->radarioEvent_group_events as $ge) {
                if ($ge->id == $this->eventId) {
        ?>
                <li class="r-e-chosen"><?php echo $ge->humanizedDateTime; ?></li>
        <?php
                } else {
        ?>
                <li><a href="<?php echo JRoute::_('index.php?option=com_radario&amp;view=event&amp;id=' . $ge->id); ?>"><?php echo $ge->humanizedDateTime; ?></a></li>
        <?php
                }
            }
        ?>
            </ul>

    <?php
        }
    ?>
        </div>

        <h3 id="chosen-tickets-header"><?php echo JText::_('COM_RADARIO_STEP1_CHOSEN_TICKETS'); ?></h3>
        <p>
            </p><ul id="chosen-tickets">
                <li id="no-tickets"><?php echo JText::_('COM_RADARIO_STEP1_NO_CHOSEN_TICKETS'); ?></li>
            </ul>
        <p></p>

        <h3 id="overall-header"><?php echo JText::_('COM_RADARIO_STEP1_TOTAL'); ?></h3>
        <p id="overall">
            <span id="no-overall"><?php echo JText::_('COM_RADARIO_STEP1_NO_CHOSEN_TICKETS'); ?></span>
            <span id="overall-text"><?php echo JText::_('COM_RADARIO_STEP1_TOTAL_TICKETS'); ?> <span id="count-chosen"></span> <?php echo JText::_('COM_RADARIO_STEP1_TOTAL_SUM'); ?> <span id="total-sum"></span> <img class="ruble" src="/images/zakaz/ruble_sign.svg"></span>
        </p>
        <br>

        <div id="legend-general">
            <p><a class="box stateS"></a> <?php echo JText::_('COM_RADARIO_STEP1_TICKETS_CHOSEN_BY_USER'); ?></p>
            <p><a class="box stateE"></a> <?php echo JText::_('COM_RADARIO_STEP1_TICKETS_UNAVAILABLE'); ?></p>
        </div>
        <br>

        <div id="legend-prices">
            <span id="legend-extension">
        <?php
            foreach ($this->radarioEvent_ticket_types as $tt_key => $tt_val) {
        ?>
                <p><a class="box stateF color<?php echo ($tt_key + 1); ?>"></a> <?php echo $tt_val->price; ?> <img class="ruble" src="/images/zakaz/ruble_sign.svg"></p>
        <?php
            }
        ?>
            </span>
        </div>

    </div>

    <div id="tickets">
        <?php echo $this->radarioEventPlaceScheme; ?>

<?php
// Вывод полей со счётчиками для выбора билетов без мест
if (isset($this->radarioEvent_ticket_types)) {
    foreach ($this->radarioEvent_ticket_types as $tt_key => $tt_val) {
        if (!$tt_val->withSeats) {
?>
    <div id="ticket-counter-<?php echo $tt_val->id; ?>" 
        class="ticket-counter"
        data-ticket-type-id="<?php echo $tt_val->id; ?>"
        data-ticket-type-title="<?php echo $tt_val->title; ?>"
        data-ticket-type-price="<?php echo $tt_val->price; ?>"
        data-ticket-type-with-seats="<?php echo ($tt_val->withSeats ? 'true' : 'false'); ?>"
        data-ticket-type-free-ticket-count="<?php echo $tt_val->freeTicketCount; ?>"
    >
        <input type="text" id="ticket-counter-input-<?php echo $tt_val->id; ?>"
            class="ticket-counter-input"
            name="ticket-counter-input-<?php echo $tt_val->id; ?>"
            value="<?php echo (isset($_COOKIE["countChosen"]) ? $_COOKIE["countChosen"] : 0); ?>"
            max="<?php echo $config->getValue('config.radario_max_places_per_order'); ?>"
            <?php echo ($tt_val->freeTicketCount == 0 ? 'disabled="disabled"' : ''); ?>
        >
        <div class="button minus-button" data-ticket-type-id="<?php echo $tt_val->id; ?>"><span>–</span></div>
        <div class="button  plus-button" data-ticket-type-id="<?php echo $tt_val->id; ?>"><span>+</span></div>
        <label for="<?php echo $tt_val->id; ?>-counter" class="ticket-counter-label">
    <?php
        if ($tt_val->freeTicketCount == 0) {
    ?>
            <?php echo $tt_val->title; ?> ( <?php echo JText::_('COM_RADARIO_STEP1_NO_TICKETS'); ?> )
    <?php
        } else {
    ?>
            <?php echo $tt_val->title; ?> ( <span id="free-ticket-count-<?php echo $tt_val->id; ?>"><?php echo $tt_val->freeTicketCount; ?></span> <?php echo JText::_('COM_RADARIO_STEP1_TICKETS_BY_PRICE'); ?> <?php echo $tt_val->price; ?> <img class="ruble" src="/images/zakaz/ruble_sign.svg"> )
    <?php
        }
    ?>
        </label>
    </div>
<?php
        }
    }
}
?>
    </div>

</div>

<script type="text/javascript">
$(document).ready(function() {
    // Работа счётчика для групп с билетами без мест (если они имеются)
    $('.ticket-counter').on('click', '.button', function (index, value) {
        var ticketTypeId        = $(this).parent().data('ticket-type-id');
        var ticketTypeTitle     = $(this).parent().data('ticket-type-title');
        var ticketTypePrice     = $(this).parent().data('ticket-type-price');
        var ticketTypeWithSeats = $(this).parent().data('ticket-type-with-seats');
        var ticketTypeFreeTicketCount = parseInt($(this).parent().data('ticket-type-free-ticket-count'));

        var counterInput = $('#ticket-counter-input-' + ticketTypeId);
        var counterValue = parseInt(counterInput.val());
        var plusButton  = $('#ticket-counter-plus-button'  + ticketTypeId);
        var minusButton = $('#ticket-counter-minus-button' + ticketTypeId);
        var freeTicketCount = $('#free-ticket-count-' + ticketTypeId);

        var action = '';
        // Добавить или убрать билет без места в корзину
        if ($(this).hasClass('plus-button')) {
            // Нельзя выделить больше билетов, чем максимальное значение из конфигурации сайта
            if (countChosen < max_places_per_order) {
                action = 'select';
                // Нельзя выбрать больше билетов, чем есть в наличии в этой группе билетов
                if (counterValue < ticketTypeFreeTicketCount) {
                    counterValue += 1;
                    counterInput.val(counterValue);

                    chosenTickets.push({
                        'ticketTypeId': ticketTypeId,
                        'ticketTypeTitle': ticketTypeTitle,
                        'ticketTypePrice': ticketTypePrice,
                        'ticketTypeWithSeats': ticketTypeWithSeats,
                        'rowName': null,
                        'seatName': null,
                        'number': null
                    });
                    $('#chosen-tickets').append(
                        '<li id="' + ticketTypeId + '-' + (countChosen + 1) + '-' + ticketTypePrice + '">' + ticketTypeTitle + ', цена ' + ticketTypePrice + ' <img class="ruble" src="/images/zakaz/ruble_sign.svg"></li>'
                    );

                    countChosen += 1;
                    totalSum += ticketTypePrice;

                    setCookie('eventId', eventId);
                    setCookie('countChosen', countChosen);
                    setCookie('totalSum', totalSum);
                    setCookie('chosenTickets', JSON.stringify(chosenTickets));

                    $('#count-chosen').html(countChosen);
                    $('#total-sum').html(totalSum);
                } else {
                    return false;
                }
            } else {
                return false;
            }
        // Добавить или убрать билет без места в корзину
        } else if ($(this).hasClass('minus-button')) {
            action = 'free';
            if (counterValue > 0) {
                counterValue -= 1;

                chosenTickets.splice(chosenTickets.length - 1, 1);
                $('#' + ticketTypeId + '-' + countChosen + '-' + ticketTypePrice).remove();

                countChosen -= 1;
                totalSum -= ticketTypePrice;

                setCookie('eventId', eventId);
                setCookie('countChosen', countChosen);
                setCookie('totalSum', totalSum);
                setCookie('chosenTickets', JSON.stringify(chosenTickets));

                $('#count-chosen').html(countChosen);
                $('#total-sum').html(totalSum);
            } else {
                counterValue = 0;
                return false;
            }
            counterInput.val(counterValue);
        }

        if (countChosen > 0) {
            $('#count-chosen').html(countChosen);
            $('#total-sum').html(totalSum);

            $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
            $('#overall-text, #buy-tickets').show();
        } else {
            $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
            $('#overall-text, #buy-tickets').hide();
        }

        console.log('action', action, 'countChosen', countChosen, 'totalSum', totalSum, 'chosenTickets', chosenTickets);
    });

});
</script>