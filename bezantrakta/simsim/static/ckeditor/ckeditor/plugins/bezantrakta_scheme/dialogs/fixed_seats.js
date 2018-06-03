(function(){
    CKEDITOR.dialog.add('fixed_seats_dialog', function(editor) {
        return {
            title: editor.lang.bezantrakta_scheme.fs_dialog_title,
            minWidth: 400,
            minHeight: 200,
            contents: [
                {
                    id: 'fixed_seats_tab',
                    title: editor.lang.bezantrakta_scheme.fs_dialog_title,
                    label: editor.lang.bezantrakta_scheme.fs_dialog_title,
                    elements: [
                        {
                            type: 'radio',
                            id: 'seats_direction',
                            label: editor.lang.bezantrakta_scheme.fs_seats_direction,
                            items: [
                                [editor.lang.bezantrakta_scheme.fs_seats_direction_ltr, 'ltr'],
                                [editor.lang.bezantrakta_scheme.fs_seats_direction_rtl, 'rtl']
                            ],
                            default: this.fs_seats_direction,
                            validate: CKEDITOR.dialog.validate.notEqual(null, editor.lang.bezantrakta_scheme.fs_seats_direction_nonempty),
                            onClick: function() {
                                console.log('seats_direction: ' + this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'sector_id',
                            label: editor.lang.bezantrakta_scheme.fs_sector_id,
                            labelLayout: 'horizontal',
                            default: this.fs_sector_id,

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'row_id',
                            label: editor.lang.bezantrakta_scheme.fs_row_id,
                            labelLayout: 'horizontal',
                            default: this.fs_row_id,

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'seat_id',
                            label: editor.lang.bezantrakta_scheme.fs_seat_id,
                            labelLayout: 'horizontal',
                            default: this.fs_seat_id,
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.fs_seat_id_nonempty),

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'seat_title',
                            label: editor.lang.bezantrakta_scheme.fs_seat_title,
                            labelLayout: 'horizontal',

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'html',
                            html: editor.lang.bezantrakta_scheme.fs_dialog_warning
                        }
                    ]
                }
            ],

            onShow: function() {
                var dialog = this;

                var selection = editor.getSelection();
                // console.log('selection:', selection);
                var ranges = selection.getRanges();
                // console.log('ranges:', ranges);

                var seats_selected = ranges.length;
                // console.log('seats_selected:', seats_selected);

                var element = selection.getStartElement();
                // console.log('element:', element);

                var scheme = editor.document.findOne('.stagehall');
                var ticket_service = scheme && scheme.data('ts') ? scheme.data('ts') : 'superbilet';

                var seats_direction = dialog.fs_seats_direction ? dialog.fs_seats_direction : 'ltr';
                dialog.setValueOf('fixed_seats_tab', 'seats_direction', seats_direction);

                // Для СуперБилета нужно указывать ID сектора, ряда и места, но не подпись места
                if (ticket_service == 'superbilet') {
                    dialog.getContentElement('fixed_seats_tab', 'sector_id').enable();
                    dialog.getContentElement('fixed_seats_tab', 'row_id').enable();
                    dialog.setValueOf('fixed_seats_tab', 'sector_id', dialog.fs_sector_id);
                    dialog.setValueOf('fixed_seats_tab', 'row_id', dialog.fs_row_id);

                    dialog.getContentElement('fixed_seats_tab', 'seat_title').disable();
                }
                // Для Радарио нужно указывать только ID места и подпись места, но не ID сектора и ряда
                else if (ticket_service == 'radario') {
                    dialog.getContentElement('fixed_seats_tab', 'sector_id').disable();
                    dialog.getContentElement('fixed_seats_tab', 'row_id').disable();

                    dialog.getContentElement('fixed_seats_tab', 'seat_title').enable();
                    dialog.setValueOf('fixed_seats_tab', 'seat_title', dialog.fs_seat_title);
                }

                dialog.setValueOf('fixed_seats_tab', 'seat_id', dialog.fs_seat_id);

                // Если курсор стоит в одной ячейке
                if (seats_selected <= 1 && element.hasClass('seat')) {
                    var ticket_id = element.data('ticket-id');
                    if (ticket_service == 'superbilet') {
                        var seat_attrs = ticket_id.split('_')
                        var sector_id = seat_attrs[0];
                        var row_id = seat_attrs[1];
                        var seat_id = seat_attrs[2];
                    } else if (ticket_service == 'radario') {
                        var sector_id = null;
                        var row_id = null;
                        var seat_id = ticket_id;
                    }

                    var seat_title = element.getHtml().replace('<br>', '').replace('&nbsp;', '').replace('&nbsp;', '');

                    dialog.setValueOf('fixed_seats_tab', 'seats_direction', seats_direction);
                    if (ticket_service == 'superbilet') {
                        dialog.setValueOf('fixed_seats_tab', 'sector_id',   sector_id);
                        dialog.setValueOf('fixed_seats_tab', 'row_id',      row_id);
                    }
                    dialog.setValueOf('fixed_seats_tab', 'seat_id',         seat_id);
                    if (ticket_service == 'radario') {
                        dialog.setValueOf('fixed_seats_tab', 'seat_title',  seat_title);
                    }
                }
            },

            onOk: function() {
                var dialog = this;
                var selection = editor.getSelection();
                ranges = selection.getRanges();

                var seats_selected = ranges.length;

                var element = selection.getStartElement();
                // console.log('element:', element);

                var scheme = editor.document.findOne('.stagehall');
                var ticket_service = scheme && scheme.data('ts') ? scheme.data('ts') : 'superbilet';

                var seats_direction = dialog.getValueOf('fixed_seats_tab', 'seats_direction');

                var sector_id = parseInt(dialog.getValueOf('fixed_seats_tab', 'sector_id'));
                var row_id = parseInt(dialog.getValueOf('fixed_seats_tab', 'row_id'));
                var seat_id = parseInt(dialog.getValueOf('fixed_seats_tab', 'seat_id'));
                var seat_title = dialog.getValueOf('fixed_seats_tab', 'seat_title');
                seat_title = seat_title ? parseInt(seat_title) : seat_id;

                // Подготовка к перебору мест
                var seat_id_cursor = seat_id;
                var seat_title_cursor = seat_title;

                // console.log('seat_id_cursor:', seat_id_cursor);
                // console.log('seat_title_cursor:', seat_title_cursor);

                // Сохранение последних введённых значений для последующей подстановки
                dialog.fs_seats_direction = seats_direction;
                dialog.fs_ticket_service = ticket_service;
                dialog.fs_sector_id = sector_id;
                dialog.fs_row_id = row_id;
                dialog.fs_seat_id = seat_id;

                if (seats_selected > 1) {
                    // console.log('multiple seats selected');

                    var ltr = seats_direction == 'ltr';

                    for (
                        var r = ltr ? 0 : seats_selected - 1;
                        ltr ? r < seats_selected : r >= 0;
                        ltr ? r++ : r--
                    ) {
                        // console.log('  range:', ranges[r]);
                        var walker = new CKEDITOR.dom.walker(ranges[r]), node;
                        // console.log('  walker:', walker);
                        while ((node = walker.next())) {
                            // console.log('    node:', node, node.$.nodeName);
                            if (node.$.nodeName == 'TD') {
                                if (!node.hasClass('seat')) {
                                    node.addClass('seat');
                                }

                                // Сохранение data-атрибута ticket-id
                                if (ticket_service == 'superbilet') {
                                    ticket_id = sector_id + '_' + row_id + '_' + seat_id_cursor;
                                } else if (ticket_service == 'radario') {
                                    ticket_id = seat_id_cursor;
                                }
                                node.data('ticket-id', ticket_id);

                                // Добавление `&nbsp;` для подписи мест от 1 до 9
                                seat_title = seat_title_cursor < 10 ? '&nbsp;' + seat_title_cursor + '&nbsp;' : seat_title_cursor;
                                node.setHtml(seat_title);

                                // Перебор мест
                                seat_id_cursor += 1;
                                seat_title_cursor += 1;
                            }
                        }
                    };
                } else {
                    // console.log('one seat selected');
                    if (!element.hasClass('seat')) {
                        element.addClass('seat');
                    }

                    // Сохранение data-атрибута ticket-id
                    if (ticket_service == 'superbilet') {
                        ticket_id = sector_id + '_' + row_id + '_' + seat_id_cursor;
                    } else if (ticket_service == 'radario') {
                        ticket_id = seat_id_cursor;
                    }

                    element.data('ticket-id', ticket_id);

                    // Добавление `&nbsp;` для подписи мест от 1 до 9
                    seat_title = seat_title < 10 ? '&nbsp;' + seat_title + '&nbsp;': seat_title;
                    element.setHtml(seat_title);
                }
            }
        };
    });
})();
