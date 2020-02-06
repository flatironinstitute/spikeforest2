import React, { Component } from 'react';
import PropTypes from 'prop-types';

import TreeNode from './TreeNode';

export default class Tree extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedNodePath: this.props.selectedNodePath || null,
            expandedNodePaths: {}
        };
    }

    componentDidMount() {
        const { expandedNodePaths } = this.state;
        expandedNodePaths[this.props.rootNode.path] = true;
        this.setState({
            expandedNodePaths: expandedNodePaths,
            selectedNodePath: this.props.selectedNodePath
        });
        this.adjustExpandedNodePaths();
    }

    componentDidUpdate(prevProps) {
        if (this.props.selectedNodePath !== prevProps.selectedNodePath) {
            this.setState({
                selectedNodePath: this.props.selectedNodePath
            });
            this.adjustExpandedNodePaths();
        }
    }

    adjustExpandedNodePaths() {
        let { expandedNodePaths } = this.state;
        let { selectedNodePath } = this.props;
        if (selectedNodePath) {
            let pathsToExpand = this.getAllAncestorPaths(selectedNodePath);
            for (let path0 of pathsToExpand) {
                expandedNodePaths[path0] = true;
            }
        }
        this.setState({
            expandedNodePaths: expandedNodePaths
        });
    }

    getChildNodes = (node) => {
        if (!node.childNodes) {
            return [];
        }
        return node.childNodes;
    }

    handleToggle = (node) => {
        const { expandedNodePaths } = this.state;
        expandedNodePaths[node.path] = !(expandedNodePaths[node.path]);
        this.setState({ expandedNodePaths });
    }

    handleNodeSelected = node => {
        const { onNodeSelected } = this.props;
        this.setState({
            selectedNodePath: node ? node.path : null
        });
        if (onNodeSelected) {
            onNodeSelected(node);
        }
    }

    getAllAncestorPaths(path) {
        let ret = [];
        let a = path.split('.');
        for (let i = 0; i < a.length - 1; i++) {
            ret.push(a.slice(0, i + 1).join('.'));
        }
        return ret;
    }

    render() {
        const { rootNode, selectedNodePath } = this.props
        const { expandedNodePaths } = this.state;
        if (!rootNode) {
            return <div>No root node.</div>;
        }
        return (
            <div>
                <TreeNode
                    node={rootNode}
                    selectedNodePath={selectedNodePath}
                    expandedNodePaths={expandedNodePaths}
                    getChildNodes={this.getChildNodes}
                    onToggle={this.handleToggle}
                    onNodeSelect={this.handleNodeSelected}
                    level={0}
                />
            </div>
        )
    }
}

Tree.propTypes = {
    rootNode: PropTypes.object.isRequired,
    selectedNodePath: PropTypes.string,
    onNodeSelected: PropTypes.func
};