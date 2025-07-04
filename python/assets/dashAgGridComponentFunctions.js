var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.Button = function (props) {
    const {setData, data} = props;

    function onClick() {
        setData();
    }
    return React.createElement(
        window.dash_bootstrap_components.Button,
        {
            onClick,
            className: props.className,
        },
        props.value
    );
};

dagcomponentfuncs.dataTypeDefinitions = {
    dateString: {
        baseDataType: 'dateString',
        extendsDataType: 'dateString',
        valueParser: (params) =>
            params.newValue != null &&
            params.newValue.match('\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}')
                ? params.newValue
                : null,
        valueFormatter: (params) => (params.value == null ? '' : params.value),
        dataTypeMatcher: (value) =>
            typeof value === 'string' && !!value.match('\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}'),
        dateParser: (value) => {
            if (value == null || value === '') {
                return undefined;
            }
            const dateParts = value.split('/');
            return dateParts.length === 3
                ? new Date(
                    parseInt(dateParts[2]),
                    parseInt(dateParts[1]) - 1,
                    parseInt(dateParts[0])
                )
                : undefined;
        },
        dateFormatter: (value) => {
            if (value == null) {
                return undefined;
            }
            const date = String(value.getDate());
            const month = String(value.getMonth() + 1);
            return `${date.length === 1 ? '0' + date : date}/${
                month.length === 1 ? '0' + month : month
            }/${value.getFullYear()}`;
        },
    },
};


dagcomponentfuncs.DatePicker = new class {

    // gets called once before the renderer is used
    init(params) {
        // create the cell
        this.eInput = document.createElement('input');
        this.eInput.value = params.value;
        this.eInput.classList.add('ag-input');
        this.eInput.style.height = 'var(--ag-row-height)';
        this.eInput.style.fontSize = 'calc(var(--ag-font-size) + 1px)';

        // https://trentrichardson.com/examples/timepicker/
        $(this.eInput).datetimepicker({
            timeFormat: 'HH:mm:ss',
            dateFormat: 'yy-mm-dd'
        });
    }

    // gets called once when grid ready to insert the element
    getGui() {
        return this.eInput;
    }

    // focus and select can be done after the gui is attached
    afterGuiAttached() {
        this.eInput.focus();
        this.eInput.select();
    }

    // returns the new value after editing
    getValue() {
        return this.eInput.value;
    }

    // any cleanup we need to be done here
    destroy() {
        // but this example is simple, no cleanup, we could
        // even leave this method out as it's optional
    }

    // if true, then this editor will appear in a popup
    isPopup() {
        // and we could leave this method out also, false is the default
        return false;
    }

}