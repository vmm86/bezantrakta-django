(function(){
    CKEDITOR.dialog.add('scheme_init_table_dialog', function(editor) {
        return {
            title: editor.lang.bezantrakta_scheme.init_table_dialog_title,
            minWidth: 400,
            minHeight: 200,
            contents: [
                {
                    id: 'scheme_init_tab',
                    title: editor.lang.bezantrakta_scheme.init_table_dialog_title,
                    label: editor.lang.bezantrakta_scheme.init_table_dialog_title,
                    elements: [
                        {
                            type: 'radio',
                            id: 'ticket_service',
                            label: editor.lang.bezantrakta_scheme.init_table_ticket_service,
                            items: [
                                [editor.lang.bezantrakta_scheme.init_table_ticket_service_superbilet, 'superbilet'],
                                [editor.lang.bezantrakta_scheme.init_table_ticket_service_radario, 'radario']
                            ],
                            default: 'superbilet',
                            validate: CKEDITOR.dialog.validate.notEqual(null, editor.lang.bezantrakta_scheme.init_table_seats_direction_nonempty),
                            onClick: function() {
                                console.log('ticket_service: ', this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'scheme_rows',
                            label: editor.lang.bezantrakta_scheme.init_table_scheme_rows,
                            labelLayout: 'horizontal',
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.init_table_scheme_rows_nonempty),

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'scheme_columns',
                            label: editor.lang.bezantrakta_scheme.init_table_scheme_columns,
                            labelLayout: 'horizontal',
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.init_table_scheme_columns_nonempty),

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'html',
                            html: editor.lang.bezantrakta_scheme.init_table_dialog_warning
                        }
                    ]
                }
            ],

            onOk: function() {
                var dialog = this;

                var editor = this.getParentEditor();
                // console.log('editor:', editor);

                var ticket_service = dialog.getValueOf('scheme_init_tab', 'ticket_service');
                var scheme_columns = parseInt(dialog.getValueOf('scheme_init_tab', 'scheme_columns'));
                var scheme_rows = parseInt(dialog.getValueOf('scheme_init_tab', 'scheme_rows'));
                // console.log('scheme_columns:', scheme_columns);
                // console.log('scheme_rows:', scheme_rows);

                // Создание заготовки пустой таблицы для схемы зала
                var scheme_template = '<table class="stagehall" border="0" data-ts="' + ticket_service + '">\n';
                scheme_template += '<tbody>\n';
                for (var r = 0; r < scheme_rows; r++) {
                    scheme_template += '<tr>\n';
                        for (var c = 0; c < scheme_columns; c++) {
                            scheme_template += '<td>&nbsp;</td>\n';
                        };
                    scheme_template += '</tr>\n';
                };
                scheme_template += '</tbody>\n';
                scheme_template += '</table>';

                // var scheme = CKEDITOR.dom.element.createFromHtml(scheme_template);
                // editor.insertElement(scheme);
                editor.setData(scheme_template);
            }
        };
    });
})();
