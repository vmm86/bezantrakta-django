(function(){
    CKEDITOR.dialog.add('scheme_init_circle_dialog', function(editor) {
        return {
            title: editor.lang.bezantrakta_scheme.init_circle_dialog_title,
            minWidth: 400,
            minHeight: 200,
            contents: [
                {
                    id: 'scheme_init_tab',
                    title: editor.lang.bezantrakta_scheme.init_circle_dialog_title,
                    label: editor.lang.bezantrakta_scheme.init_circle_dialog_title,
                    elements: [
                        {
                            type: 'radio',
                            id: 'ticket_service',
                            label: editor.lang.bezantrakta_scheme.init_circle_ticket_service,
                            items: [
                                [editor.lang.bezantrakta_scheme.init_circle_ticket_service_superbilet, 'superbilet'],
                                [editor.lang.bezantrakta_scheme.init_circle_ticket_service_radario, 'radario']
                            ],
                            default: 'superbilet',
                            validate: CKEDITOR.dialog.validate.notEqual(null, editor.lang.bezantrakta_scheme.init_circle_seats_direction_nonempty),
                            onClick: function() {
                                console.log('ticket_service: ', this.getValue());
                            }
                        },
                        {
                            type: 'text',
                            id: 'scheme_columns',
                            label: editor.lang.bezantrakta_scheme.init_circle_scheme_columns,
                            labelLayout: 'horizontal',
                            validate: CKEDITOR.dialog.validate.notEmpty(editor.lang.bezantrakta_scheme.init_circle_scheme_columns_nonempty),
                            default: 12,

                            setup: function(element) {
                                this.setValue(element.getText());
                            },

                            commit: function(element) {
                                element.setText(this.getValue());
                            }
                        },
                        {
                            type: 'html',
                            html: editor.lang.bezantrakta_scheme.init_circle_dialog_warning
                        }
                    ]
                }
            ],

            onOk: function() {
                var dialog = this;

                var editor = this.getParentEditor();
                // console.log('editor:', editor);

                var ts = dialog.getValueOf('scheme_init_tab', 'ticket_service');
                var scheme_columns = parseInt(dialog.getValueOf('scheme_init_tab', 'scheme_columns'));
                // console.log('scheme_columns:', scheme_columns);

                // Создание заготовки пустой таблицы для схемы зала и кастомных стилей для неё
                var angle = 360 / scheme_columns;
                var button_rotate = angle / 2;
                var button_skew = 90 - angle;

                var scheme_template = `
<style type="text/css">\n
.stagehall-circle {
    -webkit-transform: rotate(-${button_rotate}deg);
    -ms-transform:     rotate(-${button_rotate}deg);
    transform:         rotate(-${button_rotate}deg);
}
.stagehall-circle .sector-button {
    -webkit-transform: skewY(${button_skew}deg) rotate(${button_rotate}deg);
    -ms-transform:     skewY(${button_skew}deg) rotate(${button_rotate}deg);
    transform:         skewY(${button_skew}deg) rotate(${button_rotate}deg);
}`;

                /* angle = 360 / num of segments, rotate = (nth-child - 1) * angle, skew = -(90 - angle) */
                for (var col = 1; col <= scheme_columns; col++) {
                    var li_rotate = (col - 1) * angle;
                    var li_skew = 90 - angle;
                    var span_rotate = li_rotate > 0 ? '-' + li_rotate : 0;
                    scheme_template += `
.stagehall-circle li:nth-child(${col}) {
    -webkit-transform: rotate(${li_rotate}deg) skewY(-${li_skew}deg);
    -ms-transform:     rotate(${li_rotate}deg) skewY(-${li_skew}deg);
    transform:         rotate(${li_rotate}deg) skewY(-${li_skew}deg);
}

.stagehall-circle li:nth-child(${col}) label span {
    -webkit-transform: rotate(${span_rotate}deg);
    -ms-transform:     rotate(${span_rotate}deg);
    transform:         rotate(${span_rotate}deg);
}\n`;
                }
                scheme_template += `</style>\n\n

                <div class="stagehall-circle-wrapper">

                    <div class="stage">Сцена</div>

                    <ul class="stagehall-circle" data-ts="${ts}">`;

                    for (var col = 1; col <= scheme_columns; col++) {
                        scheme_template += `
                        <li>
                            <div class="sector-button">
                                <input id="sector-${col}" name="sectors" type="radio">
                                <label for="sector-${col}">
                                    <span>Сектор<br>${col}</span>
                                </label>
                           </div>
                        </li>`;
                    }
                    scheme_template += `
                </div>`;

                editor.setData(scheme_template);
            }
        };
    });
})();
