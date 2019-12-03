import React, { Component } from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell } from '@material-ui/core';

export default class Sorters extends Component {
    constructor(props) {
        super(props);
    }
    componentDidMount() {
    }
    componentWillUnmount() {
    }
    render() {
        const object = this.props.object || [];
        return (
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Algorithm</TableCell>
                        <TableCell>Processor (version)</TableCell>
                        <TableCell>Sorting parameters</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {
                        object.map((sorter) => {
                            return (
                                <TableRow key={sorter.name}>
                                    <TableCell>
                                        <b>{sorter.name}</b>
                                    </TableCell>
                                    <TableCell>
                                        {sorter.algorithmName}
                                    </TableCell>
                                    <TableCell>
                                        {sorter.processorName} ({sorter.processorVersion})
                                    </TableCell>
                                    <TableCell>
                                        <pre>{JSON.stringify(sorter.sortingParameters)}</pre>
                                    </TableCell>
                                </TableRow>
                            );
                        })
                    }
                </TableBody>
            </Table>
        )
    }
}
