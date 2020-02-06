import React, { Component } from 'react';
import { PythonInterface } from 'reactopya';
import BrowserTree, { TreeData } from './BrowserTree';
const config = require('./DirectoryView.json');

export default class DirectoryView extends Component {
    static title = 'View a directory on a local or remote machine'
    static reactopyaConfig = config
    constructor(props) {
        super(props);
        this.state = {
            // javascript state
            path: null,
            
            // python state
            dir_content: {},
            status: '',
            status_message: ''
        }
        this.treeData = new TreeData;
    }
    componentDidMount() {
        this.pythonInterface = new PythonInterface(this, config);
        this.pythonInterface.start();
        // Use this.pythonInterface.setState(...) to pass data to the python backend
        this.pythonInterface.setState({
            path: this.props.path
        });
    }
    componentWillUnmount() {
        this.pythonInterface.stop();
    }
    render() {
        console.log('---', this.state.dir);
        return (
            <RespectStatus {...this.state}>
                <BrowserTree
                    treeData={this.treeData}
                    dirContent={this.state.dir_content}
                    basePath={this.props.path}
                />
            </RespectStatus>
        )
    }
}

class RespectStatus extends Component {
    state = {}
    render() {
        switch (this.props.status) {
            case 'started':
                return <div>Started: {this.props.status_message}</div>
            case 'running':
                return <div>{this.props.status_message}</div>
            case 'error':
                return <div>Error: {this.props.status_message}</div>
            case 'finished':
                return this.props.children;
            default:
                return <div>Unknown status: {this.props.status}</div>
        }
    }
}