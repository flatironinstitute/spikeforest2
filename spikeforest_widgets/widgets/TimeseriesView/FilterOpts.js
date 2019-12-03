import React, { Component } from 'react';
import { FormControl, Select, MenuItem, Menu, makeStyles, InputLabel, TextField, Button } from '@material-ui/core';

export default class FilterOpts extends Component {
    constructor(props) {
        super(props);
        this.state = {
            editedFilterOpts: null
        }
    }
    componentDidMount() {
        this.setState({
            editedFilterOpts: JSON.parse(JSON.stringify(this.props.filterOpts))
        });
    }
    componentDidUpdate(prevProps) {
        if (this.props.filterOpts !== prevProps.filterOpts) {
            this.setState({
                editedFilterOpts: JSON.parse(JSON.stringify(this.props.filterOpts))
            });
        }
    }
    _handleFieldChange = (key, val) => {
        let newFilterOpts = this.state.editedFilterOpts;
        newFilterOpts[key] = val;
        this.setState({
            editedFilterOpts: newFilterOpts
        });
    }
    _handleUpdate = () => {
        this.props.onChange && this.props.onChange(this.state.editedFilterOpts);
    }
    render() {
        const { editedFilterOpts } = this.state;
        if (!editedFilterOpts) {
            return <span />;
        }
        let formFields = [
            {
                key: 'type',
                label: 'Filter type',
                type: 'select',
                value: editedFilterOpts.type,
                options: [
                    {
                        value: 'none',
                        label: 'No filter'
                    },
                    {
                        value: 'bandpass_filter',
                        label: 'Bandpass filter'
                    }
                ]
            },
            {
                key: 'freq_min',
                label: 'Freq. min (Hz)',
                type: 'float',
                value: editedFilterOpts.freq_min,
            },
            {
                key: 'freq_max',
                label: 'Freq. max (Hz)',
                type: 'float',
                value: editedFilterOpts.freq_max,
            },
            {
                key: 'freq_wid',
                label: 'Freq. wid (Hz)',
                type: 'float',
                value: editedFilterOpts.freq_wid,
            },
            {
                key: 'update',
                label: 'Update',
                type: 'button',
                onClick: this._handleUpdate
            }
        ];
        return (
            <Form2
                formFields={formFields}
                onFieldChange={this._handleFieldChange}
            />
        );
    }
}

const useStyles = makeStyles(theme => ({
    root: {
      display: 'flex',
      flexDirection: 'column'
    },
    formControl: {
      margin: theme.spacing(1),
      minWidth: 120,
    },
    selectEmpty: {
      marginTop: theme.spacing(2),
    },
}));

function Form2(props) {
    const classes = useStyles();
    const { formFields } = props;
    return (
        <form className={classes.root} autoComplete="off">
            {
                formFields.map((ff) => (
                    <FormControl2
                        formField={ff}
                        key={ff.key}
                        onChange={(newval) => {props.onFieldChange && props.onFieldChange(ff.key, newval)}}
                    />
                ))
            }
        </form>
    )
}

class FormControl2 extends Component {
    render() {
        const { formField } = this.props;
        if (formField.type == 'select') {
            return (
                <FormControl key={formField.key}>
                    <InputLabel htmlFor={formField.key}>{formField.label}</InputLabel>
                    <Select
                        value={formField.value}
                        onChange={(evt) => {this.props.onChange(evt.target.value)}}
                        inputProps={{
                            name: formField.key,
                            id: formField.key,
                        }}
                    >
                        {
                            formField.options.map((option) => (
                                <MenuItem value={option.value}>{option.label}</MenuItem>
                            ))
                        }
                    </Select>
                </FormControl>
            );
        }
        else if (formField.type == 'float') {
            return (
                <TextField
                    id={formField.key}
                    label={formField.label}
                    value={formField.value}
                    onChange={(evt) => {this.props.onChange(Number(evt.target.value))}}
                    // onChange={...}
                    type="number"                    
                />
            );
        }
        else if (formField.type == 'button') {
            return (
                <Button onClick={formField.onClick}>
                    {formField.label}
                </Button>
            );
        }
        else {
            return <span>Unknown type: {formField.type}</span>;
        }
    }
}