import React, { Component } from 'react';
import { Toolbar } from '@material-ui/core';
import { Link } from "@material-ui/core";

export default class TimeWidgetBottomBar extends Component {
    render() {
        const { info } = this.props;
        const style0 = {
            position: 'relative',
            width: this.props.width,
            height: this.props.height
        };
        return (
            <Toolbar style={{minHeight: this.props.height}}>
                <CurrentTimeControl
                    width={180}
                    currentTime={info.currentTime}
                    samplerate={info.samplerate}
                    onChange={this.props.onCurrentTimeChanged}
                />
                &nbsp;
                <TimeRangeControl
                    width={250}
                    timeRange={info.timeRange}
                    samplerate={info.samplerate}
                    onChange={this.props.onTimeRangeChanged}
                />
                <span>{info.statusText}</span>
            </Toolbar>
        );
    }
}

class CurrentTimeControl extends Component {
    state = {  }
    _handleChange = (txt) => {
        let t = fromHumanTime(txt, this.props.samplerate);
        if (t !== undefined) {
            this.props.onChange(t);
        }
        else {
            console.warn(`Invalid human time string: ${txt}`);
        }
    }
    render() { 
        const { currentTime, samplerate } = this.props;
        let style0 = {
            width: this.props.width,
            padding: 5,
            border: 'solid 1px lightgray'
        };
        return (
            <div style={style0}>
                Time:&nbsp;
                <EditableText
                    width={this.props.width - 50}
                    title="Click to edit current time"
                    text={toHumanTime(currentTime, samplerate)}
                    onChange={this._handleChange}
                />
            </div>
        );
    }
}

class TimeRangeControl extends Component {
    state = {  }
    _handleChange = (txt) => {
        let tr = fromHumanTimeRange(txt, this.props.samplerate);
        if (tr !== undefined) {
            this.props.onChange(tr);
        }
        else {
            console.warn(`Invalid human time range string: ${txt}`);
        }
    }
    render() { 
        const { timeRange, samplerate } = this.props;
        let style0 = {
            width: this.props.width,
            padding: 5,
            border: 'solid 1px lightgray'
        };
        return (
            <div style={style0}>
                Range:&nbsp;
                <EditableText
                    width={this.props.width - 50}
                    title="Click to edit time range"
                    text={toHumanTimeRange(timeRange, samplerate)}
                    onChange={this._handleChange}
                />
            </div>
        );
    }
}

function toHumanTimeRange(tr, samplerate) {
    if (!tr) return 'none';
    return `${toHumanTime(tr[0], samplerate, {nounits: true, num_digits: 3})} - ${toHumanTime(tr[1], samplerate, {num_digits: 3})}`;
}

function fromHumanTimeRange(txt, samplerate) {
    if (txt === 'none') return null;
    let a = txt.split('-');
    if (a.length !== 2) return undefined;
    let t1 = fromHumanTime(a[0], samplerate, {nounits: true});
    let t2 = fromHumanTime(a[1], samplerate);
    if ((t1 === undefined) || (t2 === undefined))
        return undefined;
    return [t1, t2];
}

function toHumanTime(t, samplerate, opts) {
    opts = opts || {};
    if (t === null) return 'none';
    let sec = round(t / samplerate, opts.num_digits || 6);
    if (opts.nounits) return sec;
    else return `${sec} s`;
}

function fromHumanTime(txt, samplerate, opts) {
    opts = opts || {};
    if (txt === 'none') return null;
    const list = txt.split(/(\s+)/).filter( e => e.trim().length > 0);
    if (list.length === 1) {
        if (opts.nounits) {
            return fromHumanTime(txt + ' s', samplerate, {nounits: false});
        }
        if (txt.endsWith('s'))
            return fromHumanTime(txt.slice(0, txt.length - 1) + ' s', samplerate);
        else
            return undefined;
    }
    else if (list.length === 2) {
        let val = Number(list[0]);
        if (isNaN(val)) return undefined;
        let units = list[1];
        if (units === 's') {
            return val * samplerate;
        }
        else {
            return undefined;
        }
    }
    else {
        return undefined;
    }
}

function round(val, num_digits) {
    return Math.round(val * Math.pow(10, num_digits)) / Math.pow(10, num_digits);
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