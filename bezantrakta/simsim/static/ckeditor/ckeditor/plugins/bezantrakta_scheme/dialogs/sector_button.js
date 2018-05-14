(function(){
    CKEDITOR.dialog.add('sector_button_dialog', function(editor) {
        return {
            title: editor.lang.bezantrakta_scheme.sb_dialog_title,
            minWidth: 400,
            minHeight: 200,
            contents: [
                {
                    id: 'sb_active_tab',
                    title: editor.lang.bezantrakta_scheme.sb_tab_title,
                    label: editor.lang.bezantrakta_scheme.sb_tab_title,
                    elements: [
                        {
                            type: 'text',
                            id: 'sector_title_active',
                            label: editor.lang.bezantrakta_scheme.sb_sector_title,
                            labelLayout: 'horizontal',

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'sector_id_active',
                            label: editor.lang.bezantrakta_scheme.sb_sector_id,
                            labelLayout: 'horizontal',

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'sector_height_active',
                            label: editor.lang.bezantrakta_scheme.sb_sector_height,
                            labelLayout: 'horizontal',
                            default: 6,

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'html',
                            id: 'dialog_warning_new_active',
                            html: editor.lang.bezantrakta_scheme.sb_dialog_warning_new
                        },
                        {
                            type: 'html',
                            id: 'dialog_warning_cur_active',
                            html: editor.lang.bezantrakta_scheme.sb_dialog_warning_cur
                        },
                        {
                            type: 'html',
                            id: 'dialog_warning_height_active',
                            html: editor.lang.bezantrakta_scheme.sb_dialog_warning_height
                        }
                    ]
                },
                {
                    id: 'sb_passive_tab',
                    title: editor.lang.bezantrakta_scheme.sbe_tab_title,
                    label: editor.lang.bezantrakta_scheme.sbe_tab_title,
                    elements: [
                        {
                            type: 'text',
                            id: 'sector_title_passive',
                            label: editor.lang.bezantrakta_scheme.sbe_sector_title,
                            labelLayout: 'horizontal',

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'sector_height_passive',
                            label: editor.lang.bezantrakta_scheme.sb_sector_height,
                            labelLayout: 'horizontal',
                            default: 6,

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'html',
                            id: 'dialog_warning_new_passive',
                            html: editor.lang.bezantrakta_scheme.sbe_dialog_warning_new
                        },
                        {
                            type: 'html',
                            id: 'dialog_warning_cur_passive',
                            html: editor.lang.bezantrakta_scheme.sbe_dialog_warning_cur
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

                var is_stage = element.hasClass('stage');
                var is_seat = element.hasClass('seat');

                if (is_stage || is_seat) {
                    return false;
                }

                // Если кнопка активная (с выбором секторов) - выделение в редакторе приходится на её label
                var is_active = element.is('label');
                // console.log('is_active:', is_active);
                // Если кнопка НЕактивная (с подписью или без неё) - выделение в редакторе приходится на её span
                var is_passive = element.is('span');
                // console.log('is_passive:', is_passive);

                // Элемент кнопки
                var button = undefined;
                if (is_active) {
                    button = element.getParent();
                } else if (is_passive) {
                    button = element.getParent().getParent();
                }
                // console.log('button:', button);

                var button_parent = button ? button.getParent() : element;
                // console.log('button_parent:', button_parent);

                var is_button = button ? button.hasClass('sector-button') : false;
                // console.log('is_button:', is_button);

                // Название кнопки
                var sector_title = '';
                if (is_active) {
                    sector_title = element.findOne('span') ? element.findOne('span').getHtml() : '';
                } else if (is_passive) {
                    sector_title = element.getHtml();
                }
                // console.log('sector_title:', sector_title);
                sector_title = sector_title == '&nbsp;' ? '' : sector_title;

                dialog.setValueOf('sb_active_tab', 'sector_title_active', sector_title);
                dialog.setValueOf('sb_passive_tab', 'sector_title_passive', sector_title);

                // ID сектора
                var sector_id = is_active && button ? parseInt(button.findOne('input').getId().substr(7)) : null;
                dialog.setValueOf('sb_active_tab', 'sector_id_active', sector_id);

                // Высота ячейки (только для таблиц)
                var sector_height = button_parent.is('td') && button_parent.getStyle('height') ? parseInt(button_parent.getStyle('height').slice(0, -3)) : 6;
                if (button_parent.is('td')) {
                    dialog.setValueOf('sb_active_tab', 'sector_height_active', sector_height);
                    dialog.setValueOf('sb_passive_tab', 'sector_height_passive', sector_height);
                }
                var sector_height_input = dialog.getContentElement('sb_active_tab', 'sector_height_active').getElement();
                button_parent.is('td') ? sector_height_input.show() : sector_height_input.hide();

                // Сохранение текущих значений для проверки их возможного изменения
                editor.cur_sb_sector_title = sector_title;
                editor.cur_sb_sector_id = sector_id;
                editor.cur_sb_sector_height = sector_height;

                // Справочная информация
                var dialog_warning_new_active = dialog.getContentElement('sb_active_tab', 'dialog_warning_new_active').getElement();
                var dialog_warning_cur_active = dialog.getContentElement('sb_active_tab', 'dialog_warning_cur_active').getElement();
                var dialog_warning_height_active = dialog.getContentElement('sb_active_tab', 'dialog_warning_height_active').getElement();

                var dialog_warning_new_passive = dialog.getContentElement('sb_passive_tab', 'dialog_warning_new_passive').getElement();
                var dialog_warning_cur_passive = dialog.getContentElement('sb_passive_tab', 'dialog_warning_cur_passive').getElement();

                button_parent.is('td') ? dialog_warning_cur_active.show() : dialog_warning_cur_active.hide();

                // Разная логика в зависимости от нажатой кнопки в тулбаре
                current_tab = dialog.definition.dialog._.currentTabId;
                // console.log('current_tab:', current_tab);

                if (current_tab == 'sb_active_tab') {
                    // Если в ячейку ранее была добавлена активная кнопка сектора - выделение приходится на её label
                    if (is_active && is_button) {
                        dialog_warning_cur_active.show();
                        dialog_warning_new_active.hide();
                    } else {
                        dialog_warning_cur_active.hide();
                        dialog_warning_new_active.show();
                    }
                }
                else if (current_tab == 'sb_passive_tab') {
                    // Если в ячейку ранее была добавлена НЕактивная кнопка - выделение приходится на её span
                    if (is_passive && is_button) {
                        dialog_warning_cur_passive.show();
                        dialog_warning_new_passive.hide();
                    } else {
                        dialog_warning_cur_passive.hide();
                        dialog_warning_new_passive.show();
                    }
                }
            },

            onOk: function() {
                var dialog = this;

                var selection = editor.getSelection();
                // console.log('selection:', selection);

                var element = selection.getStartElement();
                // console.log('element:', element);

                // Если кнопка активная (с выбором секторов) - выделение в редакторе приходится на её label
                var is_active = element.is('label');
                // console.log('is_active:', is_active);
                // Если кнопка НЕактивная (с подписью или без неё) - выделение в редакторе приходится на её span
                var is_passive = element.is('span');
                // console.log('is_passive:', is_passive);

                // Элемент кнопки
                var button = undefined;
                if (is_active) {
                    button = element.getParent();
                } else if (is_passive) {
                    button = element.getParent().getParent();
                }
                // console.log('button:', button);

                var button_parent = button ? button.getParent() : element;
                // console.log('button_parent:', button_parent);

                var is_button = button ? button.hasClass('sector-button') : false;
                // console.log('is_button:', is_button);

                var cls = 'sector';

                var sector_id = parseInt(dialog.getValueOf('sb_active_tab', 'sector_id_active'));

                var button_template = undefined;

                if (!button_parent.hasClass(cls)) {
                    element.addClass(cls);
                }

                // Разная логика в зависимости от нажатой кнопки в тулбаре
                current_tab = dialog.definition.dialog._.currentTabId;
                // console.log('current_tab:', current_tab);

                var sector_title = undefined;
                var sector_heigh = undefined;

                if (current_tab == 'sb_active_tab') {
                    sector_title = dialog.getValueOf('sb_active_tab', 'sector_title_active') || '&nbsp;';
                    sector_height = parseInt(dialog.getValueOf('sb_active_tab', 'sector_height_active'));

                    button_template = `
                    <div class="sector-button">
                        <input id="sector-${sector_id}" name="sectors" type="radio">
                        <label for="sector-${sector_id}">
                            <span>${sector_title}</span>
                        </label>
                    </div>`;
                } else if (current_tab == 'sb_passive_tab') {
                    sector_title = dialog.getValueOf('sb_passive_tab', 'sector_title_passive') || '&nbsp;';
                    sector_height = parseInt(dialog.getValueOf('sb_passive_tab', 'sector_height_passive'));

                    button_template = `
                    <div class="sector-button empty">
                        <label>
                            <span>${sector_title}</span>
                        </label>
                    </div>`;
                } else {
                    return false;
                }

                // Переопределяем выделенный элемент на родительский элемент кнопки (td или li с классом sector-button)
                element = button_parent;

                // Высота ячейки
                if (button_parent.is('td')) {
                    element.setStyle('height', sector_height + 'rem');
                }

                // Удаляем текущую кнопку, если она была добавлена ранее
                if (button) {
                    button.remove();
                }

                // Пересоздание кнопки сектора
                element.setHtml(button_template);
                // console.log('button has been recreated');
            }
        };
    });
})();
