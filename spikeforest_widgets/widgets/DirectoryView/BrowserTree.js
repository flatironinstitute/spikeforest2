import React, { Component } from 'react';
import Tree from './Tree.js';
import styled from 'styled-components'

const STATUS_WAITING = 'waiting';
const STATUS_LOADED = 'loaded';
const STATUS_LOADING = 'loading';
const STATUS_FAILED_TO_LOAD = 'failed-to-load';

const HistoryLine = styled.div`
  height:8px;
  width: 100%;
  background: #E2E2E2;
  cursor: arrow;
  margin-top: 6px;

  :hover {
    background: gray;
  }
`;

class NodeCreator {
    createObjectNode(obj, name, basepath, part_of_list) {
        const max_array_children = 20;
        let childNodes = [];
        let path0 = this.joinPaths(basepath, name, '.', part_of_list);
        let type0 = 'object';
        if (Array.isArray(obj)) {
            childNodes = this.createArrayHierarchyChildNodes(obj, max_array_children, 0, obj.length, path0);
        }
        else {
            let keys = Object.keys(obj);
            keys.sort();
            for (let key of keys) {
                let val = obj[key];
                if ((val) && (typeof (val) == 'object')) {
                    childNodes.push(this.createObjectNode(val, key, path0));
                }
                else {
                    childNodes.push(this.createValueNode(val, key, path0));
                }
            }
        }
        return {
            type: type0,
            name: name,
            childNodes: childNodes,
            path: path0,
            data: {
                object: obj
            }
        }
    }

    createArrayHierarchyChildNodes(X, max_array_children, i1, i2, path0) {
        let childNodes = [];
        if (i2 - i1 <= max_array_children) {
            for (let ii = i1; ii < i2; ii++) {
                let val = X[ii];
                if ((val) && (typeof (val) == 'object')) {
                    childNodes.push(this.createObjectNode(val, '' + ii, path0, true));
                }
                else {
                    childNodes.push(this.createValueNode(val, '' + ii, path0, true));
                }
            }
        }
        else {
            let stride = 1;
            while ((i2 - i1) / stride > max_array_children / 2) {
                stride = stride * 10;
            }
            for (let jj = i1; jj < i2; jj += stride) {
                let jj2 = jj + stride;
                if (jj2 >= i2) jj2 = i2;
                childNodes.push({
                    type: 'array-parent',
                    name: `${jj} - ${jj2 - 1}`,
                    path: path0 + `[${jj}-${jj2 - 1}]`,
                    data: {},
                    childNodes: this.createArrayHierarchyChildNodes(X, max_array_children, jj, jj2, path0),
                });
            }
        }
        return childNodes;

    }

    createValueNode(val, name, basepath) {
        let path0 = this.joinPaths(basepath, name, '.');
        return {
            type: 'value',
            name: name,
            path: path0,
            data: {
                value: val
            }
        };
    }

    createDirNode(X, name, basepath) {
        let childNodes = [];
        let path0 = this.joinPaths(basepath, name, '/');
        let dnames = Object.keys(X.dirs);
        dnames.sort();
        for (let dname of dnames) {
            childNodes.push(this.createDirNode(X.dirs[dname], dname, path0));
        }
        let fnames = Object.keys(X.files);
        fnames.sort();
        for (let fname of fnames) {
            childNodes.push(this.createFileNode(X.files[fname], fname, path0));
        }
        return {
            type: 'dir',
            name: name,
            path: path0,
            data: {
                dir: X
            },
            childNodes: childNodes
        };
    }

    createFileNode(X, name, basepath) {
        let path0 = this.joinPaths(basepath, name, '/');
        return {
            type: 'file',
            name: name,
            path: path0,
            data: {
                file: X
            },
            childNodes: []
        };
    }

    joinPaths(path1, path2, sep, part_of_list) {
        if (!path2) return path1;
        if (!path1) return path2;
        if (part_of_list) {
            return `${path1}.${path2}`;
        }
        else {
            return `${path1}${sep}${path2}`;
        }
    }
}

export class TreeData {
    rootNode = null
    status = null;
    nodeCreator = new NodeCreator();
    findNodeByPath(path, startAt) {
        if (!startAt) {
            startAt = this.rootNode;
        }
        if (!startAt)
            return null;
        if (startAt.path === path)
            return startAt;
        if (startAt.childNodes) {
            for (let ch of startAt.childNodes) {
                let x = this.findNodeByPath(path, ch);
                if (x)
                    return x;
            }
        }
        return null;
    }
    // async updateContent(path, kacheryManager) {
    //     this.rootNode = null;
    //     this.path = path;
    //     if (path.endsWith('.json')) {
    //         let A = await kacheryManager.loadObject(path, {});
    //         if (!A) {
    //             this.status = STATUS_FAILED_TO_LOAD;
    //             return;
    //         }
    //         this.rootNode = this.nodeCreator.createObjectNode(A, '');
    //         this.status = STATUS_LOADED;
    //     }
    //     else {
    //         let X = await kacheryManager.loadDirectory(path, {});
    //         if (!X) {
    //             this.status = STATUS_FAILED_TO_LOAD;
    //             return;
    //         }
    //         this.rootNode = this.nodeCreator.createDirNode(X, '', path);
    //         this.status = STATUS_LOADED;
    //     }
    // }
    async updateContentFromObject(obj) {
        this.rootNode = this.nodeCreator.createObjectNode(obj, '');
        this.status = STATUS_LOADED;
    }
    async updateContentFromDir(dirContent, basePath) {
        this.rootNode = this.nodeCreator.createDirNode(dirContent, '', basePath);
        this.status = STATUS_LOADED;
    }
}

class BrowserTree extends Component {
    state = {
        status: STATUS_WAITING,
        rootNode: null,
        selectedNodePath: null
    };


    async componentDidMount() {
        await this.updateContent();
        this.setState({
            selectedNodePath: this.props.selectedNodePath
        });
    }

    async componentDidUpdate(prevProps) {
        if (this.props.path !== prevProps.path) {
            await this.updateContent()
        }
        if (this.props.selectedNodePath !== prevProps.selectedNodePath) {
            this.setState({
                selectedNodePath: this.props.selectedNodePath
            });
        }
    }

    async updateContent() {
        this.setState({
            status: STATUS_LOADING
        });
        // const { path, object, dirContent, kacheryManager } = this.props;
        const { object, dirContent, basePath } = this.props;
        if (dirContent) {
            await this.props.treeData.updateContentFromDir(dirContent, basePath);
        }
        else if (object) {
            await this.props.treeData.updateContentFromObject(object);
        }
        this.setState({
            status: this.props.treeData.status,
            rootNode: this.props.treeData.rootNode
        });
        this.handleNodeSelected(this.props.treeData.rootNode);
    }

    handleNodeSelected = (node) => {
        this.setState({
            selectedNodePath: node ? node.path : null
        });
        this.props.onItemSelected && this.props.onItemSelected({
            type: node.type,
            name: node.name,
            path: node.path,
            data: JSON.parse(JSON.stringify(node.data))
        });
    }

    handleHistoryLineClick(ind) {
        this.props.onGotoHistory && this.props.onGotoHistory(ind);
    }

    render() {
        const { status } = this.state;
        switch (status) {
            case STATUS_WAITING:
                return <div>Waiting to load...</div>;
            case STATUS_LOADING:
                return <div>{`Loading ${this.props.path}...`}</div>;
            case STATUS_FAILED_TO_LOAD:
                return <div>{`Failed to load ${this.props.path}...`}</div>;
            case STATUS_LOADED:
                return (
                    <React.Fragment>
                        {
                            this.props.pathHistory ? (
                                this.props.pathHistory.map((p, ind) => (
                                    <HistoryLine key={ind} title={p} onClick={() => { this.handleHistoryLineClick(ind) }} />
                                ))
                            ) : <span />
                        }
                        <Tree
                            rootNode={this.state.rootNode}
                            selectedNodePath={this.state.selectedNodePath}
                            onNodeSelected={this.handleNodeSelected}
                        />
                    </React.Fragment>
                );
            default:
                return <div>Loading: {status}</div>;
        }
    }
}

export default BrowserTree;