import React, { Component } from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell } from '@material-ui/core';

export default class StudyAnalysisResults extends Component {
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
            {key: 'studyName', label: 'Study'},
            {key: 'studySetName', label: 'Study set'},
            {key: 'num-recordings', label: 'Num. recordings', func: function(obj) {return obj.recordingNames.length}},
            {key: 'num-sorting-results', label: 'Num. sorting results', func: function(obj) {return obj.sortingResults.length}},
            {key: 'num-units', label: 'Num. g.t. units', func: function(obj) {return obj.trueUnitIds.length}}
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
                        object.map((result) => {
                            return (
                                <TableRow key={result.studyName}>
                                    {
                                        columns.map((col) => {
                                            return (
                                                <TableCell key={col.key}>{col.func ? col.func(result) : createElement(col, result[col.key])}</TableCell>
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

function createElement(col, val) {
    if ((val) && ('linkText' in col)) {
        // a hack!
        val = val.replace('spikeforest/spikesorters', 'spikeforest/spikeforestsorters');

        return <a target='_blank' href={val}>{col.linkText}</a>;
    }
    else {
        return val;
    }
}