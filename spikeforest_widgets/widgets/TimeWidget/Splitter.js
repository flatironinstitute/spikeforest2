import React, { Component } from 'react';
import Draggable from 'react-draggable';

export default class Splitter extends Component {
    constructor(props) {
        super(props);
        this.state={
            gripPosition: null
        };
    }
    _handleGripDrag = (evt, ui) => {
    }
    _handleGripDragStop = (evt, ui) => {
        const newGripPosition = ui.x;
        if (newGripPosition === this.state.gripPosition) {
            return;
        }
        this.setState({
            gripPosition: newGripPosition
        });
        this.props.onChange && this.props.onChange();
    }
    render() {
        let child1 = this.props.children[0];
        let child2 = this.props.children[1];

        if (!child2) {
            let child0 = this.props.children;
            return <child0.type {...child0.props} width={this.props.width} height={this.props.height} left={this.props.left} />
        }

        const { width, height } = this.props;
        let { gripPosition } = this.state;

        if (gripPosition === null) {
            gripPosition = 300;
        }
        const gripWidth = 12;
        const width1 = gripPosition;
        const width2 = width - width1 - gripWidth;
        
        let style0 = {
            position: 'absolute',
            left: 0,
            top: 0,
            left: this.props.left,
            width: width,
            height: height
        };
        let style1 = {
            position: 'absolute',
            left: 0,
            top: 0,
            width: width1,
            height: height
        };
        let style2 = {
            position: 'absolute',
            left: width1 + gripWidth,
            top: 0,
            width: width2,
            height: height
        };
        let styleGrip = {
            position: 'absolute',
            top: 0,
            width: gripWidth,
            height: height,
            background: 'rgb(230, 230, 230)',
            cursor: 'col-resize',
            zIndex: 100
        };
        let styleGripInner = {
            position: 'absolute',
            top: 0,
            left: 0,
            width: 4,
            height: height,
            background: 'gray',
            cursor: 'col-resize'
        };
        return (
            <div style={style0}>
                <div key="child1" style={style1} className="SplitterChild">
                    <child1.type {...child1.props} width={width1} height={height} />
                </div>
                <Draggable
                    key="drag"
                    position={{x: gripPosition, y: 0}}
                    axis="x"
                    onDrag={this._handleGripDrag}
                    onStop={this._handleGripDragStop}
                >
                    <div style={styleGrip}>
                        <div style={styleGripInner} />
                    </div>
                </Draggable>
                
                <div key="child2" style={style2} className="SplitterChild">
                    <child2.type {...child2.props} width={width2} height={height} />
                </div>
            </div>
        )
    }
}