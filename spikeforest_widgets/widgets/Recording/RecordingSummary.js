import React, { Component } from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell } from '@material-ui/core';

export default class RecordingSummary extends Component {
    constructor(props) {
        super(props);
    }
    componentDidMount() {
    }
    componentWillUnmount() {
    }
    render() {
        let {
            recording,
            num_channels, channel_locations,
            num_timepoints, samplerate
        } = this.props;
        recording = recording || {};
        let rows = [
            {value: recording.path || '', label: 'Recording'},
            {value: num_channels || '', label: 'Num. channels'},
            {value: num_timepoints ? Math.floor(num_timepoints / samplerate) : '', label: 'Duration (sec)'},
            {value: samplerate || '', label: 'Sampling freq. (Hz)'}
        ]
        return (
            <Table>
                <TableHead>
                </TableHead>
                <TableBody>
                    {
                        rows.map((row) => {
                            return (
                                <TableRow key={row.label}>
                                    <TableCell key="label">{row.label}</TableCell>
                                    <TableCell key="value">{row.value}</TableCell>
                                </TableRow>
                            );
                        })
                    }
                </TableBody>
            </Table>
        )
    }
}