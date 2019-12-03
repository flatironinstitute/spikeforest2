import React, { Component } from 'react';
import { FormControl, FormLabel, FormGroup, FormControlLabel, Checkbox, Radio } from '@material-ui/core';

export default class UnitSelector extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedUnits: {}
        };
    }
    componentDidMount() {
        this.setStateFromProps();
    }
    componentDidUpdate() {
        this.setStateFromProps();
    }
    setStateFromProps() {
        if (!matches(this.state.selectedUnits, this.props.selectedUnits)) {
            this.setState({
                selectedUnits: this.props.selectedUnits
            });
        }
    }
    handleChange = (id, checked) => {
        let su = this.state.selectedUnits;
        if (this.props.mode == 'single') {
            su = {};
        }
        su[id] = checked;
        if (!checked) {
            delete su[id];
        }
        this.props.onChange && this.props.onChange(su);
    }
    render() {
        const { all_unit_ids, cluster_names } = this.props;
        let CheckboxOrRadio = this.props.mode === 'single' ? Radio : Checkbox;
        return (
            <FormControl component="fieldset">
                <FormLabel component="legend">{this.props.mode === 'single' ? 'Select unit' : 'Select units'}</FormLabel>
                <FormGroup aria-label="position" name="position" row>
                    {
                        all_unit_ids.map((id, ind) => (
                            <FormControlLabel
                                key={id}
                                control={<CheckboxOrRadio checked={this.state.selectedUnits[id] ? true : false} onChange={(evt, checked) => {this.handleChange(id, checked);}} color="primary" />}
                                label={cluster_names && cluster_names[ind] ? `${id} (${cluster_names[ind]})` : id}
                                labelPlacement="end"
                            />
                        ))
                    }
                    
                </FormGroup>
            </FormControl>
        )
    }
}

function matches(a, b) {
    for (let key in a) {
        if (a[key] != b[key])
            return false;
    }
    for (let key in b) {
        if (a[key] != b[key])
            return false;
    }
    return true;
}
