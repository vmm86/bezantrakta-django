(function() {
    CKEDITOR.plugins.add('bezantrakta_scheme', {
        icons: [
            'init_table', 'init_circle',
            'stage',
            'sector',
            'fixedseats', 'nofixedseats',
            'sectorbuttonactive', 'sectorbuttonpassive',

            'tablerowinsertbefore', 'tablerowinsertafter', 'tablerowdelete',
            'tablecolumninsertbefore', 'tablecolumninsertafter', 'tablecolumndelete',
            'tablecellsmerge', 'tablecellsclear',

            'bordertop', 'borderright', 'borderbottom', 'borderleft'
        ].join(','),
        lang: 'ru',
        init: function(editor) {
            // Группа в контекстном меню
            if (editor.contextMenu) {
                editor.addMenuGroup('bezantrakta_scheme_group');
            }

            // Создание новой табличной схемы зала
            editor.addCommand('scheme_init_table', new CKEDITOR.dialogCommand('scheme_init_table_dialog'));

            editor.ui.addButton('SchemeInitTable', {
                label: editor.lang.bezantrakta_scheme.init_table_title,
                icon: 'init_table',
                command: 'scheme_init_table',
                toolbar: 'bezantrakta_scheme'
            });

            CKEDITOR.dialog.add('scheme_init_circle_dialog', this.path + 'dialogs/init_circle.js');

            // Создание новой круговой посекторной схемы зала
            editor.addCommand('scheme_init_circle', new CKEDITOR.dialogCommand('scheme_init_circle_dialog'));

            editor.ui.addButton('SchemeInitCircle', {
                label: editor.lang.bezantrakta_scheme.init_circle_title,
                icon: 'init_circle',
                command: 'scheme_init_circle',
                toolbar: 'bezantrakta_scheme'
            });

            CKEDITOR.dialog.add('scheme_init_table_dialog', this.path + 'dialogs/init_table.js');

            // Работа с таблицей
            editor.ui.addButton('RowInsertBefore', {
                label: editor.lang.bezantrakta_scheme.row_insert_before,
                icon: 'tablerowinsertbefore',
                command: 'rowInsertBefore',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('RowInsertAfter', {
                label: editor.lang.bezantrakta_scheme.row_insert_after,
                icon: 'tablerowinsertafter',
                command: 'rowInsertAfter',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('RowDelete', {
                label: editor.lang.bezantrakta_scheme.row_delete,
                icon: 'tablerowdelete',
                command: 'rowDelete',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('ColumnInsertBefore', {
                label: editor.lang.bezantrakta_scheme.column_insert_before,
                icon: 'tablecolumninsertbefore',
                command: 'columnInsertBefore',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('ColumnInsertAfter', {
                label: editor.lang.bezantrakta_scheme.column_insert_after,
                icon: 'tablecolumninsertafter',
                command: 'columnInsertAfter',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('ColumnDelete', {
                label: editor.lang.bezantrakta_scheme.column_delete,
                icon: 'tablecolumndelete',
                command: 'columnDelete',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('CellsMerge', {
                label: editor.lang.bezantrakta_scheme.cells_merge,
                icon: 'tablecellsmerge',
                command: 'cellMerge',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('CellsClear', {
                label: editor.lang.bezantrakta_scheme.cells_clear,
                icon: 'tablecellsclear',
                command: 'removeFormat',
                toolbar: 'bezantrakta_scheme'
            });

            // Сцена
            editor.addCommand('toggle_stage', {
                exec: function(editor) {
                    cls = 'stage';

                    element = editor.getSelection().getStartElement();

                    if (!element.hasClass('seat') && !element.hasClass('sector')) {
                        element.hasClass(cls) ? element.removeClass(cls) : element.addClass(cls);
                        if (element.getHtml() == '<br>') {
                            element.setHtml('Сцена');
                        }
                    }
                }
            });

            editor.ui.addButton('Stage', {
                label: editor.lang.bezantrakta_scheme.stage_tooltip,
                icon: 'stage',
                command: 'toggle_stage',
                toolbar: 'bezantrakta_scheme'
            });

            // Секторы
            editor.addCommand('toggle_sector', {
                exec: function(editor) {
                    cls = 'sector';

                    var selection = editor.getSelection();
                    // console.log('selection:', selection);
                    var ranges = selection.getRanges();
                    // console.log('ranges:', ranges);

                    var cells_selected = ranges.length;
                    // console.log('cells_selected:', cells_selected);

                    var element = selection.getStartElement();
                    // console.log('element:', element);

                    // Если выделено больше одной ячейки
                    if (cells_selected > 1) {
                        // console.log('multiple cells selected');
                        for (var r = 0; r < cells_selected; r++) {
                            // console.log('  range:', ranges[r]);
                            var walker = new CKEDITOR.dom.walker(ranges[r]), node;
                            // console.log('  walker:', walker);
                            while ((node = walker.next())) {
                                // console.log('    node:', node, node.$.nodeName);
                                if (node.$.nodeName == 'TD') {
                                    if (!node.hasClass('seat') && !node.hasClass('stage')) {
                                        node.hasClass(cls) ? node.removeClass(cls) : node.addClass(cls);

                                        sector_text = node.getHtml().replace('<br>', '');
                                        sector_html = parseInt(sector_text) < 10 ? '&nbsp;' + sector_text + '&nbsp;' : sector_text;
                                        node.setHtml(sector_html);
                                    }
                                }
                            }
                        };
                    // Если курсор стоит в одной ячейке
                    } else {
                        // console.log('one cell selected');
                        if (!element.hasClass('seat') && !element.hasClass('stage')) {
                            element.hasClass(cls) ? element.removeClass(cls) : element.addClass(cls);

                            sector_text = element.getHtml().replace('<br>', '');
                            sector_html = parseInt(sector_text) < 10 ? '&nbsp;' + sector_text + '&nbsp;' : sector_text;
                            element.setHtml(sector_html);
                        }
                    }
                }
            });

            editor.ui.addButton('Sector', {
                label: editor.lang.bezantrakta_scheme.sector_tooltip,
                icon: 'sector',
                command: 'toggle_sector',
                toolbar: 'bezantrakta_scheme'
            });

            // Толстые границы ячеек (верхняя, правая, нижняя, левая)

            // Фабрика для создания действий по редактированию границ
            function toggleBorderFactory(editor, cls) {
                this.exec = function(editor) {
                    // console.log('cls:', cls);

                    var selection = editor.getSelection();
                    // console.log('selection:', selection);
                    var ranges = selection.getRanges();
                    // console.log('ranges:', ranges);

                    var cells_selected = ranges.length;
                    // console.log('cells_selected:', cells_selected);

                    var element = selection.getStartElement();
                    // console.log('element:', element);

                    // Если выделено больше одной ячейки
                    if (cells_selected > 1) {
                        // console.log('multiple cells selected');
                        for (var r = 0; r < cells_selected; r++) {
                            // console.log('  range:', ranges[r]);
                            var walker = new CKEDITOR.dom.walker(ranges[r]), node;
                            // console.log('  walker:', walker);
                            while ((node = walker.next())) {
                                // console.log('    node:', node, node.$.nodeName);
                                if (node.$.nodeName == 'TD') {
                                    node.hasClass(cls) ? node.removeClass(cls) : node.addClass(cls);
                                }
                            }
                        };
                    // Если курсор стоит в одной ячейке
                    } else {
                        // console.log('one cell selected');
                        element.hasClass(cls) ? element.removeClass(cls) : element.addClass(cls);
                    }
                }
            };

            editor.addCommand('toggle_border_bt', new toggleBorderFactory(editor, 'bt'));
            editor.addCommand('toggle_border_br', new toggleBorderFactory(editor, 'br'));
            editor.addCommand('toggle_border_bb', new toggleBorderFactory(editor, 'bb'));
            editor.addCommand('toggle_border_bl', new toggleBorderFactory(editor, 'bl'));

            editor.ui.addButton('BorderTop', {
                label: editor.lang.bezantrakta_scheme.border_tooltip_bt,
                icon: 'bordertop',
                command: 'toggle_border_bt',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('BorderRight', {
                label: editor.lang.bezantrakta_scheme.border_tooltip_br,
                icon: 'borderright',
                command: 'toggle_border_br',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('BorderBottom', {
                label: editor.lang.bezantrakta_scheme.border_tooltip_bb,
                icon: 'borderbottom',
                command: 'toggle_border_bb',
                toolbar: 'bezantrakta_scheme'
            });

            editor.ui.addButton('BorderLeft', {
                label: editor.lang.bezantrakta_scheme.border_tooltip_bl,
                icon: 'borderleft',
                command: 'toggle_border_bl',
                toolbar: 'bezantrakta_scheme'
            });

            // Сидячие места (С фиксированной рассадкой)
            editor.addCommand('fixed_seats', new CKEDITOR.dialogCommand('fixed_seats_dialog'));

            editor.ui.addButton('FixedSeats', {
                label: editor.lang.bezantrakta_scheme.fs_title,
                icon: 'fixedseats',
                command: 'fixed_seats',
                toolbar: 'bezantrakta_scheme'
            });

            if (editor.contextMenu) {
                editor.addMenuItem('fixed_seats_item', {
                    label: editor.lang.bezantrakta_scheme.fs_title,
                    icon: this.path + 'icons/fixedseats.png',
                    command: 'fixed_seats',
                    group: 'bezantrakta_scheme_group'
                });

                editor.contextMenu.addListener(function(element) {
                    var table = element.getAscendant('table', true);
                    if (table && table.hasClass('stagehall')) {
                        return {fixed_seats_item: CKEDITOR.TRISTATE_OFF};
                    }
                });
            }

            CKEDITOR.dialog.add('fixed_seats_dialog', this.path + 'dialogs/fixed_seats.js');

            // Стоячие места (БЕЗ фиксированной рассадки)
            editor.addCommand('no_fixed_seats', new CKEDITOR.dialogCommand('no_fixed_seats_dialog'));

            editor.ui.addButton('NoFixedSeats', {
                label: editor.lang.bezantrakta_scheme.nfs_title,
                icon: 'nofixedseats',
                command: 'no_fixed_seats',
                toolbar: 'bezantrakta_scheme'
            });

            if (editor.contextMenu) {
                editor.addMenuItem('no_fixed_seats_item', {
                    label: editor.lang.bezantrakta_scheme.nfs_title,
                    icon: this.path + 'icons/nofixedseats.png',
                    command: 'no_fixed_seats',
                    group: 'bezantrakta_scheme_group'
                });

                editor.contextMenu.addListener(function(element) {
                    var table = element.getAscendant('table', true);
                    if (table && table.hasClass('stagehall')) {
                        return {no_fixed_seats_item: CKEDITOR.TRISTATE_OFF};
                    }
                });
            }

            CKEDITOR.dialog.add('no_fixed_seats_dialog', this.path + 'dialogs/no_fixed_seats.js');

            // Активные кнопки для выбора секторов
            editor.addCommand(
                'sector_button_active',
                new CKEDITOR.dialogCommand('sector_button_dialog', {tabId: 'sb_active_tab'})
            );

            editor.ui.addButton('SectorButtonActive', {
                label: editor.lang.bezantrakta_scheme.sb_title,
                icon: 'sectorbuttonactive',
                command: 'sector_button_active',
                toolbar: 'bezantrakta_scheme'
            });

            // НЕактивные кнопки без выбора секторов (только подпись)
            editor.addCommand(
                'sector_button_passive',
                new CKEDITOR.dialogCommand('sector_button_dialog', {tabId: 'sb_passive_tab'})
            );

            editor.ui.addButton('SectorButtonPassive', {
                label: editor.lang.bezantrakta_scheme.sbe_title,
                icon: 'sectorbuttonpassive',
                command: 'sector_button_passive',
                toolbar: 'bezantrakta_scheme'
            });

            CKEDITOR.dialog.add('sector_button_dialog', this.path + 'dialogs/sector_button.js');
        }
    });
})();
