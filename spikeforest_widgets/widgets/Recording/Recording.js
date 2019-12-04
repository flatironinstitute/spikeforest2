import React, { Component } from 'react';
import { PythonInterface } from 'reactopya';
import TimeseriesView from '../TimeseriesView/TimeseriesView';
import Accordion from '../jscommon/Accordion/Accordion';
import RecordingSummary from './RecordingSummary';
import ElectrodeGeometry from '../ElectrodeGeometry/ElectrodeGeometry';
const config = require('./Recording.json');

export default class Recording extends Component {
    static title = 'View a recording from a SpikeForest analysis'
    static reactopyaConfig = config
    constructor(props) {
        super(props);
        this.state = {
            // javascript state
            recording: null,
            
            // python state
            num_channels: null,
            channel_ids: null,
            channel_locations: null,
            num_timepoints: null,
            samplerate: null,
            status: '',
            status_message: ''
        }
    }
    componentDidMount() {
        this.pythonInterface = new PythonInterface(this, config);
        this.pythonInterface.start();
        if ((this.props.recording) && (!this.props.recording.path)) this.props.recording.path = this.props.recording.directory;
        this.pythonInterface.setState({
            recording: this.props.recording
        });
    }
    componentWillUnmount() {
        this.pythonInterface.stop();
    }
    render() {
        const { recording } = this.props;
        let panels = [
            {label: 'Timeseries'},
            {label: 'Electrode geometry'}
        ];
        return (
            <React.Fragment>
                <div>
                    <RecordingSummary
                        {...this.state}
                    />
                </div>
                <Accordion
                    panels={panels}
                    allowMultipleExpanded={true}
                >
                    <TimeseriesView
                        recording={recording}
                        reactopyaParent={this}
                        reactopyaChildId="timeseries"
                    />
                    <ElectrodeGeometry
                        locations={this.state.channel_locations}
                        ids={this.state.channel_ids}
                    />
                </Accordion>
            </React.Fragment>
        );
    }
}
