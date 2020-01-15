import React, { Component, useState } from 'react';
import { PythonInterface } from 'reactopya';
import { TextField, Checkbox, FormGroup, FormControlLabel, Button } from '@material-ui/core';
import { Table, TableBody, TableHead, TableRow, TableCell } from '@material-ui/core';
const config = require('./MultiSort.json');

export default class MultiSort extends Component {
    static title = 'Sort a recording using multiple spike sorters'
    static reactopyaConfig = config
    constructor(props) {
        super(props);
        const defaultSorters = [
            {
                name: 'ironclust',
                label: 'IronClust',
                use: false
            },
            {
                name: 'kilosort2',
                label: 'KiloSort2',
                use: false
            },
            {
                name: 'mountainsort4',
                label: 'MountainSort4',
                use: true
            }
        ];
        this.state = {
            // javascript state
            recordingPath: 'sha1dir://51570fce195942dcb9d6228880310e1f4ca1395b.paired_kampff/2014_11_25_Pair_3_0',
            sorters: clone(defaultSorters),
            sortingJobs: [],
            spikeSortingStatus: 'not-started',
        }
    }
    componentDidMount() {
        this.pythonInterface = new PythonInterface(this, config);
        this.pythonInterface.start();
        this.pythonInterface.onMessage(msg => this.handleMessage(msg));
        // Use this.pythonInterface.setState(...) to pass data to the python backend
    }
    componentWillUnmount() {
        this.pythonInterface.stop();
    }
    handleMessage = msg => {
        if (msg.name == 'updateSpikeSortingJob') {
            let job = msg.job;
            let j = findSortingJob(this.state.sortingJobs, job.sorterName, job.recordingPath);
            if (j) {
                for (let k in job) {
                    j[k] = job[k];
                }
                this.setState({sortingJobs: this.state.sortingJobs});
            }
        }
    }
    handleStartSpikeSorting = () => {
        this.setState({spikeSortingStatus: 'running'});
        let sortingJobs = this.state.sortingJobs;
        for (let s of this.state.sorters) {
            if (s.use) {
                let j = findSortingJob(sortingJobs, s.name, this.props.recordingPath);
                if (!j) {
                    j = {
                        sorterName: s.name,
                        recordingPath: this.state.recordingPath,
                        status: 'starting'
                    };
                    sortingJobs.push(j);
                    this.pythonInterface.sendMessage({
                        name: 'startSpikeSortingJob',
                        job: j
                    });
                }
            }
        }
        this.setState({sortingJobs});
    }
    handleStopSpikeSorting = () => {
        this.setState({spikeSortingStatus: 'not-started'});
    }
    render() {
        return (
            <Sections>
                <SelectRecording
                    recordingPath={this.state.recordingPath}
                    onRecordingPathChanged={recordingPath => {this.setState({recordingPath})}}
                />
                <SelectSorters
                    sorters={this.state.sorters}
                    onSortersChanged={sorters => {this.setState({sorters})}}
                />
                <RunSpikeSorting
                    recordingPath={this.state.recordingPath}
                    sorters={this.state.sorters}
                    sortingJobs={this.state.sortingJobs}
                    status={this.state.spikeSortingStatus}
                    onStart={this.handleStartSpikeSorting}
                    onStop={this.handleStopSpikeSorting}
                />
                <VisualizeSortings />
            </Sections>
        )
    }
}

function Sections(props) {
    return (
        <div>
            {props.children}
        </div>
    );
}

function SelectRecording(props) {
    return (
        <div>
            <h3>Select recording</h3>
             <TextField
                id="filled-basic"
                label="Recording path"
                variant="filled"
                value={props.recordingPath}
                fullWidth={true}
                onChange={evt => {props.onRecordingPathChanged && props.onRecordingPathChanged(evt.target.value)}}
            />
            <hr />
        </div>
    )
}

function SelectSorters(props) {
    const toggleSorter = (name) => {
        for (let s of props.sorters) {
            if (s.name == name) {
                s.use = ! s.use;
            }
        }
        props.onSortersChanged(props.sorters);
    }
    return (
        <div>
            <h3>Select spike sorters</h3>
            {
                <FormGroup row>
                    {
                        props.sorters.map(sorter => (
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={sorter.use}
                                        onClick={() => {toggleSorter(sorter.name)}}
                                    />    
                                }
                                label={sorter.name}
                            />
                        ))
                    }
                </FormGroup>
            }
            <hr />
        </div>
    )
}

function RunSpikeSorting(props) {
    let status = props.status;

    let button;
    if (status == 'not-started') {
        button = (
            <Button variant="contained" color="primary" onClick={() => {props.onStart && props.onStart()}}>
                Start
            </Button>
        );
    }
    else if (status == 'running') {
        button = (
            <Button variant="contained" color="primary" onClick={() => {props.onStop && props.onStop()}}>
                Stop
            </Button>
        );
    }
    const findSortingJobStatus = (sorterName) => {
        let job = findSortingJob(props.sortingJobs, sorterName, props.recordingPath);
        if (job) {
            return job.status;
        }
        else {
            return 'not-started';
        }
    }
    return (
        <div>
            <h3>Run spike sorting</h3>
            {button}
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Sorter</TableCell>
                        <TableCell>Status</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>    
                    {
                        props.sorters.filter(s => s.use).map(s => (
                            <TableRow>
                                <TableCell>
                                    {s.name}
                                </TableCell>
                                <TableCell>
                                    {findSortingJobStatus(s.name)}
                                </TableCell>
                            </TableRow>
                        ))
                    }
                </TableBody>
            </Table>
            <hr />
        </div>
    )
}

function VisualizeSortings(props) {
    return (
        <div>
            <h3>Visualize sortings</h3>
            <hr />
        </div>
    )
}

function findSortingJob(sortingJobs, sorterName, recordingPath) {
    console.log('--- findSortingJob', sortingJobs, sorterName, recordingPath);
    for (let j of sortingJobs) {
        if ((j.sorterName == sorterName) && (j.recordingPath == recordingPath)) {
            return j;
        }
    }
    return null;
}

function clone(obj) {
    return JSON.parse(JSON.stringify(obj));
}