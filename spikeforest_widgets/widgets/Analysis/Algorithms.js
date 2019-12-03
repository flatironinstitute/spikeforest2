import React, { Component } from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell } from '@material-ui/core';

export default class Algorithms extends Component {
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
            {key: 'label', label: 'Algorithm'},
            {key: 'dockerfile', label: 'Dockerfile', linkText: 'Dockerfile'},
            {key: 'environment', label: 'Environment'},
            {key: 'wrapper', label: 'Wrapper', linkText: 'wrapper'},
            {key: 'website', label: 'Website', linkText: 'website'},
            {key: 'source_code', label: 'Source', linkText: 'source'},
            {key: 'authors', label: 'Authors'},
            {key: 'processor_name', label: 'Processor'},
            {key: 'doi', label: 'Doi'},
            {key: 'markdown_link', label: 'Markdown', linkText: 'markdown'}
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
                        object.map((alg) => {
                            return (
                                <TableRow key={alg.label}>
                                    {
                                        columns.map((col) => {
                                            return (
                                                <TableCell key={col.key}>{createElement(col, alg[col.key])}</TableCell>
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