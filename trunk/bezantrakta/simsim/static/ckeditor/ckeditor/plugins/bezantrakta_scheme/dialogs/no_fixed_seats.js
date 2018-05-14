(function(){
    CKEDITOR.dialog.add('no_fixed_seats_dialog', function(editor) {
        return {
            title: editor.lang.bezantrakta_scheme.nfs_dialog_title,
            minWidth: 400,
            minHeight: 200,
            contents: [
                {
                    id: 'no_fixed_seats_tab',
                    title: editor.lang.bezantrakta_scheme.nfs_dialog_title,
                    label: editor.lang.bezantrakta_scheme.nfs_dialog_title,
                    elements: [
                        {
                            type: 'html',
                            id: 'dialog_warning_new',
                            html: editor.lang.bezantrakta_scheme.nfs_dialog_warning_new
                        },
                        {
                            type: 'html',
                            id: 'dialog_warning_cur',
                            html: editor.lang.bezantrakta_scheme.nfs_dialog_warning_cur
                        },
                        {
                            type: 'text',
                            id: 'sector_id',
                            label: editor.lang.bezantrakta_scheme.nfs_sector_id,
                            default: this.nfs_sector_id,
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.nfs_sector_id_nonempty),

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
                            label: editor.lang.bezantrakta_scheme.nfs_row_id,
                            default: this.nfs_row_id,
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.nfs_row_id_nonempty),

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'first_seat_id',
                            label: editor.lang.bezantrakta_scheme.nfs_first_seat_id,
                            default: this.nfs_first_seat_id,
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.nfs_seat_id_nonempty),

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'last_seat_id',
                            label: editor.lang.bezantrakta_scheme.nfs_last_seat_id,
                            default: this.nfs_last_seat_id,
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.nfs_seat_id_nonempty),

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        }
                    ]
                }
            ],

            onShow: function() {
                var dialog = this;

                var selection = editor.getSelection();
                // console.log('selection:', selection);

                var element = selection.getStartElement();
                // console.log('element:', element);

                var scheme = editor.document.findOne('.stagehall');
                var ticket_service = scheme && scheme.data('ts') ? scheme.data('ts') : 'superbilet';

                if (ticket_service == 'superbilet') {
                    dialog.getContentElement('no_fixed_seats_tab', 'sector_id').enable();
                    dialog.getContentElement('no_fixed_seats_tab', 'row_id').enable();

                    // dialog.getContentElement('no_fixed_seats_tab', 'seat_title').disable();
                }
                else if (ticket_service == 'radario') {
                    dialog.getContentElement('no_fixed_seats_tab', 'sector_id').disable();
                    dialog.getContentElement('no_fixed_seats_tab', 'row_id').disable();

                    // dialog.getContentElement('no_fixed_seats_tab', 'seat_title').enable();
                }

                var dialog_warning_new = dialog.getContentElement('no_fixed_seats_tab', 'dialog_warning_new').getElement();
                var dialog_warning_cur = dialog.getContentElement('no_fixed_seats_tab', 'dialog_warning_cur').getElement();

                var is_li = element.is('li');
                var ul_parent = element.getAscendant('ul');
                var ul_parent_is_nfs = ul_parent ? ul_parent.hasClass('no-fixed-seats') : false;
                // Если курсор внутри созданного ранее списка с местами БЕЗ фиксированной рассадки
                if (is_li && ul_parent && ul_parent_is_nfs) {
                    // Сопроводительный текст
                    dialog_warning_cur.show();
                    dialog_warning_new.hide();

                    var ul = element.getParent();

                    var first_li = ul.getFirst();
                    var last_li = ul.getLast();

                    var first_ticket_id = first_li.data('ticket-id');
                    var last_ticket_id = last_li.data('ticket-id');

                    if (ticket_service == 'superbilet') {
                        var first_seat_attrs = first_ticket_id.split('_');
                        var last_seat_attrs = last_ticket_id.split('_');

                        var sector_id = first_seat_attrs[0];
                        var row_id = first_seat_attrs[1];
                        var first_seat_id = first_seat_attrs[2];
                        var last_seat_id = last_seat_attrs[2];
                    } else if (ticket_service == 'radario') {
                        var sector_id = null;
                        var row_id = null;
                        var first_seat_id = first_ticket_id;
                        var last_seat_id = last_ticket_id;
                    }

                    dialog.setValueOf('no_fixed_seats_tab', 'sector_id',     sector_id);
                    dialog.setValueOf('no_fixed_seats_tab', 'row_id',        row_id);
                    dialog.setValueOf('no_fixed_seats_tab', 'first_seat_id', first_seat_id);
                    dialog.setValueOf('no_fixed_seats_tab', 'last_seat_id',  last_seat_id);

                    // Сохранение текущих значений списка для проверки их возможного изменения
                    dialog.cur_nfs_sector_id = sector_id;
                    dialog.cur_nfs_row_id = row_id;
                    dialog.cur_nfs_first_seat_id = first_seat_id;
                    dialog.cur_nfs_last_seat_id = last_seat_id;
                } else {
                    // Сопроводительный текст
                    dialog_warning_cur.hide();
                    dialog_warning_new.show();

                    dialog.setValueOf('no_fixed_seats_tab', 'sector_id',     dialog.nfs_sector_id);
                    dialog.setValueOf('no_fixed_seats_tab', 'row_id',        dialog.nfs_row_id);
                    dialog.setValueOf('no_fixed_seats_tab', 'first_seat_id', dialog.nfs_first_seat_id);
                    dialog.setValueOf('no_fixed_seats_tab', 'last_seat_id',  dialog.nfs_last_seat_id);
                }
            },

            onOk: function() {
                var dialog = this;

                var editor = this.getParentEditor();
                // console.log('editor:', editor);
                var selection = editor.getSelection();
                // console.log('selection:', selection);

                var element = selection.getStartElement();
                // console.log('element:', element);

                var scheme = editor.document.findOne('.stagehall');
                var ticket_service = scheme && scheme.data('ts') ? scheme.data('ts') : 'superbilet';

                var sector_id = parseInt(dialog.getValueOf('no_fixed_seats_tab', 'sector_id'));
                var row_id = parseInt(dialog.getValueOf('no_fixed_seats_tab', 'row_id'));
                var first_seat_id = parseInt(dialog.getValueOf('no_fixed_seats_tab', 'first_seat_id'));
                var last_seat_id = parseInt(dialog.getValueOf('no_fixed_seats_tab', 'last_seat_id'));

                var seat_id_cursor = first_seat_id;

                // Сохранение последних введённых значений для последующей подстановки
                dialog.nfs_ticket_service = ticket_service;
                dialog.nfs_sector_id = sector_id;
                dialog.nfs_row_id = row_id;
                dialog.nfs_first_seat_id = first_seat_id;
                dialog.nfs_last_seat_id = last_seat_id;

                var is_li = element.is('li');
                var ul_parent = element.getAscendant('ul');
                var ul_parent_is_nfs = ul_parent ? ul_parent.hasClass('no-fixed-seats') : false;
                // console.log('ul_parent:', ul_parent);
                // Если курсор внутри созданного ранее списка с местами БЕЗ фиксированной рассадки
                if (is_li && ul_parent && ul_parent_is_nfs) {
                    // Если параметры списка мест были изменены - список нужно удалить и затем создать заново
                    if (
                        sector_id != dialog.cur_nfs_sector_id ||
                        row_id != dialog.cur_nfs_row_id ||
                        first_seat_id != dialog.cur_nfs_first_seat_id ||
                        last_seat_id != dialog.cur_nfs_last_seat_id
                    ) {
                        // console.log('parameters have changed');

                        ul_parent.remove();
                        // console.log('ul has been deleted');
                        // console.log('ul_parent:', ul_parent);
                    } else {
                        // console.log('parameters remain the same');
                        return true;
                    }
                }

                // Создание списка с местами БЕЗ фиксированной рассадки
                var nfs_list_template = '<ul class="no-fixed-seats">\n';
                for (var s = 0; s <= (last_seat_id - first_seat_id); s++) {
                    // Сохранение data-атрибута ticket-id
                    if (ticket_service == 'superbilet') {
                        ticket_id = sector_id + '_' + row_id + '_' + seat_id_cursor;
                    } else if (ticket_service == 'radario') {
                        ticket_id = seat_id_cursor;
                    }
                    nfs_list_template += '<li class="seat" data-ticket-id="' + ticket_id + '">&nbsp;</li>\n';
                    // console.log('seat_id_cursor:', seat_id_cursor);
                    seat_id_cursor += 1;
                };
                nfs_list_template += '</ul>';

                editor.insertHtml(nfs_list_template);
            }
        };
    });
})();
