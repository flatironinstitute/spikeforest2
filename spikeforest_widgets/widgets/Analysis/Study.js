import React, { Component } from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell } from '@material-ui/core';
import { Link } from '@material-ui/core';
import Sha1PathLink from '../jscommon/Sha1PathLink';

export default class Study extends Component {
    constructor(props) {
        super(props);
    }
    componentDidMount() {
    }
    componentWillUnmount() {
    }
    render() {
        const object = this.props.object || [];
        let columns = [
            {key: 'name', label: 'Recording', onClick: (rec) => {this.props.onOpenRecording && this.props.onOpenRecording(rec)}},
            {key: 'directory', label: 'Directory', sha1Link: true},
            {key: 'firingsTrue', label: 'True firings', sha1Link: true},
            {key: 'sampleRateHz', label: 'Sample rate (Hz)'},
            {key: 'numChannels', label: 'Num. channels'},
            {key: 'durationSec', label: 'Duration (sec)'},
            {key: 'numTrueUnits', label: 'Num. true units'}
        ]
        return (
            <Table>
                <TableHead>
                    <TableRow>
                        {
                            columns.map((col) => {
                                return (
                                    <TableCell key={col.key}>{col.label}</TableCell>
                                )
                            })
                        }
                    </TableRow>
                </TableHead>
                <TableBody>
                    {
                        object.recordings.map((rec) => {
                            return (
                                <TableRow key={rec.label}>
                                    {
                                        columns.map((col) => {
                                            return (
                                                <TableCell key={col.key}>{createElement(col, rec[col.key], rec)}</TableCell>
                                            );
                                        })
                                    }
                                </TableRow>
                            );
                        })
                    }
                </TableBody>
            </Table>
        )
    }
}

function createElement(col, val, rec) {
    if (col.onClick) {
        return <Link2 onClick={() => {col.onClick(rec)}}>{val}</Link2>;
    }
    else if ((val) && (col.sha1Link)) {
        return <Sha1PathLink path={val} canCopy={true} abbreviate={true}></Sha1PathLink>
    }
    else {
        return val;
    }
}

function Link2(props) {
    return (
        <Link
            component="button" variant="body2"
            onClick={props.onClick}
        >
            {props.children}
        </Link>
    )
}