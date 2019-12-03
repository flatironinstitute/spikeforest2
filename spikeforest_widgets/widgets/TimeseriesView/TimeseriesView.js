import { PythonInterface } from 'reactopya';
import React, { Component } from 'react';
import Mda from './Mda';
import TimeseriesWidget from "./TimeseriesWidget";
import TimeseriesModel from "./TimeseriesModel";
import AutoDetermineWidth from '../jscommon/AutoDetermineWidth';
import { MdGridOn as FilterOptsIcon } from 'react-icons/md';
import FilterOpts from './FilterOpts';
const config = require('./TimeseriesView.json');


export default class TimeseriesView extends Component {
    static title = 'Timeseries view'
    static reactopyaConfig = config;
    render() {
        return (
            <AutoDetermineWidth>
                <TimeseriesViewFO {...this.props} />
            </AutoDetermineWidth>
        );
    }
}

class TimeseriesViewFO extends Component {
    constructor(props) {
        super(props);
        this.state = {
            filterOpts: props.filterOpts || {type: 'none', freq_min: 300, freq_max: 6000, freq_wid: 1000}
        };
    }
    render() {
        // let leftPanels = [
        //     {
        //         key: 'filter-options',
        //         title: "Filter options",
        //         icon: <FilterOptsIcon />,
        //         render: () => (
        //             <FilterOpts
        //                 filterOpts={this.state.filterOpts}
        //                 onChange={(newOpts) => {this.setState({filterOpts: newOpts})}}
        //             />
        //         )
        //     }
        // ];
        let leftPanels = [];
        // let fo = {type: 'none', freq_min: 300, freq_max: 6000, freq_wid: 1000};
        return (
            <TimeseriesViewInner
                {...this.props}
                key={keyFromObject(this.state.filterOpts)}
                filterOpts={this.state.filterOpts}
                // filterOpts={fo}
                leftPanels={leftPanels}
            />
        );
    }
}

function keyFromObject(obj) {
    return JSON.stringify(obj);
}

class TimeseriesViewInner extends Component {
    constructor(props) {
        super(props)
        this.state = {
            // javascript state
            recording: null,

            // python state
            num_channels: null,
            channel_locations: null,
            channel_ids: null,
            num_timepoints: null,
            channel_ids: null,
            samplerate: null,
            y_offsets: null,
            y_scale_factor: null,
            segment_size: null,
            status_message: '',

            // other
            timeseriesModelSet: 0 // to trigger re-render
        }
        this.timeseriesModel = null;
    }

    componentDidMount() {
        this.pythonInterface = new PythonInterface(this, config);
        this.pythonInterface.onMessage((msg) => {
            if (msg.command == 'setSegment') {
                let X = new Mda();
                X.setFromBase64(msg.data);
                this.timeseriesModel.setDataSegment(msg.ds_factor, msg.segment_num, X);
            }
        })
        let recording = this.props.recording;
        if (this.props.filterOpts.type === 'bandpass_filter') {
            recording = {
                recording: recording,
                filters: [
                    this.props.filterOpts
                ]
            };
        }
        this.pythonInterface.setState({
            recording: recording
        });

        this.pythonInterface.start();
        this.updateData();
    }
    componentDidUpdate(prevProps, prevState) {
        this.updateData();
    }
    componentWillUnmount() {
        this.pythonInterface.stop();
    }

    updateData() {
        if (!this.state.num_channels) return;
        if (!this.timeseriesModel) {
            if (!this.state.samplerate) {
                return;
            }
            const params = {
                samplerate: this.state.samplerate,
                num_channels: this.state.num_channels,
                num_timepoints: this.state.num_timepoints,
                segment_size: this.state.segment_size
            };
            this.timeseriesModel = new TimeseriesModel(params);
            this.timeseriesModel.onRequestDataSegment((ds_factor, segment_num) => {
                this.pythonInterface.sendMessage({
                    command: 'requestSegment',
                    ds_factor: ds_factor,
                    segment_num: segment_num
                });
            });
            this.setState({
                timeseriesModelSet: this.state.timeseriesModelSet + 1
            });
        }
    }
    render() {
        if (this.timeseriesModel) {
            let leftPanels = [];
            for (let lp of this.props.leftPanels)
                leftPanels.push(lp);
            let width = Math.min(this.props.width, this.props.maxWidth || 99999);
            let height = Math.min(this.props.height || 800, this.props.maxHeight || 99999);
            return (
                <div>
                    <TimeseriesWidget
                        timeseriesModel={this.timeseriesModel}
                        num_channels={this.state.num_channels}
                        channel_ids={this.state.channel_ids}
                        channel_locations={this.state.channel_locations}
                        num_timepoints={this.state.num_timepoints}
                        y_offsets={this.state.y_offsets}
                        y_scale_factor={this.state.y_scale_factor * (this.props.initial_y_scale_factor || 1)}
                        width={width}
                        height={height}
                        leftPanels={leftPanels}
                    />
                </div>
            )
        }
        else {
            return (
                <div>Loading timeseries... {this.state.status_message}</div>
            );
        }
    }
}
