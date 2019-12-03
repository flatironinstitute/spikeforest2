import React, { Component } from 'react';
import ElectrodeGeometry from '../ElectrodeGeometry/ElectrodeGeometry';
import { Checkbox } from '@material-ui/core';

export default class SelectElectrodes extends Component {
    _toHuman(ids) {
        let list = Object.keys(ids);
        if (list.length === 0)
            return 'none';
        return list.join(', ');
    }
    _fromHuman(txt) {
        if (txt === 'none') {
            return {};
        }
        let ret = [];
        let list = txt.split(',');
        for (let a of list) {
            let val = Number(a.trim());
            if (isNaN(val)) return null;
            ret.push(val);
        }
        let ret2 = {};
        for (let i of ret) {
            ret2[i] = true;
        }
        return ret2;
    }
    _handleTextEdit = (txt) => {
        let ids = this._fromHuman(txt);
        if (!ids) return;
        this.props.onChange(ids);
    }
    _toggleViewOnlySelectedChannels = (val) => {
        let prefs = clone(this.props.prefs || {});
        prefs.viewOnlySelectedChannels = prefs.viewOnlySelectedChannels ? false : true;
        this.props.onPrefsChange && this.props.onPrefsChange(prefs);
    }
    render() {
        let labels = this.props.labels;
        let locations = this.props.locations ? this.props.locations : makeDefaultChannelLocations(this.props.num_channels);
        let prefs = this.props.prefs || {};
        return (
            <React.Fragment>
                <h3>Select electrodes</h3>
                <EditableText
                    key="editable-text"
                    text={this._toHuman(this.props.selectedElectrodeIds)}
                    onChange={this._handleTextEdit}
                />
                <ElectrodeGeometry
                    key="electrode-geometry"
                    labels={labels}
                    locations={locations}
                    width={this.props.width}
                    selectedElectrodeIds={this.props.selectedElectrodeIds}
                    onSelectedElectrodeIdsChanged={(ids) => {this.props.onChange(ids)}}
                />
                <Checkbox key="checkbox1" checked={prefs.viewOnlySelectedChannels} onClick={() => {this._toggleViewOnlySelectedChannels()}} /> View only selected channels
            </React.Fragment>
        );
    }
}

class EditableText extends Component {
    constructor(props) {
        super(props);
        this.state = {
            clicked: false,
            editedText: ''
        };
    }

    _handleClick = () => {
        if (this.state.clicked) return;
        this.setState({ clicked: true, editedText: this.props.text });
    }

    _handleUnclick = () => {
        this.setState({ clicked: false });
        this.props.onChange(this.state.editedText);
    }

    _handleEditedTextChanged = (evt) => {
        this.setState({
            editedText: evt.target.value
        });
    }

    _handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            this._handleUnclick()
        };
    }

    render() {
        let style0 = {
            width: this.props.width
        };
        let link0 = <span></span>;
        if (this.state.clicked) {
            link0 = (
                <input
                    type={"text"}
                    value={this.state.editedText}
                    readOnly={false}
                    onFocus={e => e.target.select()}
                    onBlur={this._handleUnclick}
                    autoFocus={true}
                    style={style0}
                    onChange={this._handleEditedTextChanged}
                    onKeyDown={this._handleKeyDown}
                />
            );
        }
        else {
            let text = this.props.text;

            link0 = (
                <span title={this.props.title}>
                    <Link2 onClick={this._handleClick}><span>{text}</span></Link2>
                </span>
            );
        }
        return link0;
    }
}

function Link2(props) {
    let style0 = {
        color: 'gray',
        cursor: 'pointer',
        textDecoration: 'underline'
    };
    return (
        <span
            style={style0}
            onClick={props.onClick}
        >
            {props.children}
        </span>
    );
}


function makeDefaultChannelLocations(M) {
    let ret = [];
    let y = 0;
    let numPerRow = Math.ceil(Math.sqrt(M));
    let numRows = Math.ceil(M / numPerRow);
    for (let r = 0; r < numRows; r++) {
        let x = 0;
        for (let c = 0; c < numPerRow; c++) {
            if (ret.length + 1 < M) {
                ret.push([x, y]);
            }
            x++;
        }
        y++;
    }
    return ret;
}

function clone(obj) {
    return JSON.parse(JSON.stringify(obj));
}