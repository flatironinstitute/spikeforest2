import React, { Component } from 'react';
import { PythonInterface } from 'reactopya';
import Accordion from '../jscommon/Accordion/Accordion';
import StudySets from './StudySets';
import Sorters from './Sorters';
import Algorithms from './Algorithms';
import StudyAnalysisResults from './StudyAnalysisResults';
import Study from './Study';
import Recording from '../Recording/Recording';
import { Table, TableHead, TableBody, TableRow, TableCell } from '@material-ui/core';
const config = require('./Analysis.json');

export default class Analysis extends Component {
    static title = 'View a SpikeForest analysis'
    static reactopyaConfig = config
    constructor(props) {
        super(props);
        this.state = {
            // javascript state
            path: null,
            
            // python state
            object: null, // output from python or passed directly
            status: '',
            status_message: ''
        }
    }
    componentDidMount() {
        if (this.props.object) {
            this.setState({
                status: 'finished'
            });
        }
        else if (this.props.path) {
            this.pythonInterface = new PythonInterface(this, config);
            this.pythonInterface.start();
            this.setState({
                status: 'starting',
                status_message: 'Starting python backend'
            });
            this.pythonInterface.setState({
                path: this.props.path
            });
        }
        else {
            this.setState({
                status: 'error',
                status_message: 'Missing object or props'
            });
        }
    }
    componentWillUnmount() {
        this.pythonInterface.stop();
    }
    render() {
        let { object } = this.state;
        return (
            <RespectStatus {...this.state}>
                <AnalysisWidget object={object} reactopyaParent={this} />
            </RespectStatus>
        )
    }
}

class AnalysisWidget extends Component {
    constructor(props) {
        super(props);
        this.state = {
            pageStack: [{name: 'home', data: []}]
        };
        this.handlerProps = {
            onOpenStudySet: this._openStudySet,
            onOpenStudy: this._openStudy,
            onOpenRecording: this._openRecording
        };
    }
    componentDidMount() {
        console.log('object:', this.props.object);
    }
    _openPage = (name, data) => {
        console.log('open page', name, data);
        let pageStack = this.state.pageStack;
        pageStack.push({name: name, data: data});
        this.setState({
            pageStack: pageStack
        });
    }
    _openStudySet = (studySet) => {
        console.log('---', studySet.name);
    }
    _openStudy = (study) => {
        console.log('--- study', study.name);
        this._openPage('study', {study: study});
    }
    _openRecording = (recording) => {
        console.log('--- openrecording', recording);
        this._openPage('recording', {recording: recording});
    }
    _renderTopLevelWidget(key, object) {
        let map = {
            Stats: (
                <Stats
                    object={object}
                    {...this.handlerProps}
                />
            ),
            StudySets: (
                <StudySets
                    object={object}
                    {...this.handlerProps}
                />
            ),
            Sorters: (
                <Sorters
                    object={object}
                    {...this.handlerProps}
                />
            ),
            Algorithms: (
                <Algorithms
                    object={object}
                    {...this.handlerProps}
                />
            ),
            StudyAnalysisResults: (
                <StudyAnalysisResults
                    object={object}
                    {...this.handlerProps}
                />
            ),
            General: (
                <div><pre>{JSON.stringify(object, null, 4)}</pre></div>
            )
        };
        if (key in map) {
            return map[key];
        }
        else {
            return <div>Not yet implemented: <pre>{object.length}</pre> <pre>{JSON.stringify(Object.keys((object || [])[0] || {}))}</pre></div>;
        }
    }
    _renderHome() {
        const { object } = this.props;
        let panels = [];
        panels.push({key: 'Stats', label: 'Stats', object: object})
        for (let key in object) {
            if (key !== 'mode') {
                panels.push({
                    key: key,
                    label: key,
                    object: object[key]
                });
            }
        }
        return (
            <Accordion
                panels={panels}
            >
                {
                    panels.map((panel) => (
                        <div key={panel.key}>
                            {this._renderTopLevelWidget(panel.key, panel.object)}
                        </div>
                    ))
                }
            </Accordion>
        );
    }
    _renderStudy(data) {
        const { object } = this.props;
        return (
            <Study
                object={data.study}
                {...this.handlerProps}
            />
        );
        return <pre>{JSON.stringify(data)}</pre>
    }
    _renderRecording(data) {
        return (
            <Recording
                object={data.recording}
                reactopyaParent={this.props.reactopyaParent}
                reactopyaChildId={'recording'}
                {...this.handlerProps}
            />
        );
    }
    render() {
        let page = this.state.pageStack[this.state.pageStack.length - 1];
        if (page.name == 'home') {
            return this._renderHome();
        }
        else if (page.name == 'study') {
            return this._renderStudy(page.data);
        }
        else if (page.name == 'recording') {
            return this._renderRecording(page.data);
        }
        else {
            return <div>Unexpected page name: {page.name}</div>;
        }
    }
}

class Stats extends Component {
    state = {};
    render() {
        let object = this.props.object || {};
        let stats = {
            numStudySets: 0,
            numStudies: 0,
            numRecordings: 0,
            numTrueUnits: 0,
            totalDurationSec: 0,
            numSortingResults: 0,
            totalComputeTimeSec: 0
        }
        for (let studySet of (object.StudySets || [])) {
            stats.numStudySets++;
            for (let study of studySet.studies) {
                stats.numStudies++;
                for (let recording of study.recordings) {
                    stats.numRecordings++;
                    stats.numTrueUnits += recording.numTrueUnits;
                    stats.totalDurationSec += recording.durationSec;
                }
            }
        }
        for (let sortingResult of object.SortingResults) {
            stats.numSortingResults++;
            stats.totalComputeTimeSec+=sortingResult.cpuTimeSec || 0;
        }
        return (
            <Table>
                <TableHead>
                </TableHead>
                <TableBody>
                    {
                        Object.keys(stats).map((key) => {
                            return (
                                <TableRow key={key}>
                                    <TableCell key="key">
                                        {key}
                                    </TableCell>
                                    <TableCell key="value">
                                        {stats[key]}
                                    </TableCell>
                                </TableRow>
                            );
                        })
                    }
                </TableBody>
            </Table>
        );
    }
}

class RespectStatus extends Component {
    state = {}
    render() {
        switch (this.props.status) {
            case 'starting':
                return <div>Starting: {this.props.status_message}</div>
            case 'running':
                return <div>Running: {this.props.status_message}</div>
            case 'error':
                return <div>Error: {this.props.status_message}</div>
            case 'finished':
                return this.props.children;
            default:
                return <div>Unknown status: {this.props.status}</div>
        }
    }
}