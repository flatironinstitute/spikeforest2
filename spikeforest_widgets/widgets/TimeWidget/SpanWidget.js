import React, { Component } from 'react';
import CanvasWidget, { CanvasWidgetLayer } from '../jscommon/CanvasWidget';

export default class SpanWidget extends CanvasWidget {
    constructor(props) {
        super(props);
        this.state = {
            dragTimeRange: null
        };
        this._dragging = false;
        this._mainLayer = new CanvasWidgetLayer(this.paintMainLayer);
        this._mainLayer.setMargins(50, 10, 0, 0);
    }
    componentDidMount() {
        this._mainLayer.repaint();
    }
    componentDidUpdate() {
        this._mainLayer.repaint();
    }
    paintMainLayer = (painter) => {
        const { info } = this.props;
        if (!info.numTimepoints) return;
        painter.useCoords();
        this._mainLayer.setCoordXRange(0, info.numTimepoints);
        this._mainLayer.setCoordYRange(0, 1);
        painter.fillRect(0, 0.4, info.numTimepoints, 0.2, 'lightgray');
        painter.fillRect(info.timeRange[0], 0.3, info.timeRange[1] - info.timeRange[0], 0.4, 'gray');
        painter.drawRect(info.timeRange[0], 0.3, info.timeRange[1] - info.timeRange[0], 0.4, {color: 'black', width: 2});
        if (this.state.dragTimeRange) {
            painter.drawRect(this.state.dragTimeRange[0], 0.3, this.state.dragTimeRange[1] - this.state.dragTimeRange[0], 0.4, {color: 'darkgreen', width: 2});
        }
    }
    _handleMousePress = (X) => {
    }
    _handleMouseRelease = (X) => {
        if (!this._dragging) {
            let coords = this._mainLayer.pixToCoords(X.pos);
            let t = coords[0];
            this.props.onCurrentTimeChanged(t);
        }
    }
    _handleMouseDrag = (X) => {
        const { info } = this.props;
        this._dragging = true;
        if (!info.timeRange) return;
        let c1 = this._mainLayer.pixToCoords(X.anchor);
        let c2 = this._mainLayer.pixToCoords(X.pos);
        let t1 = c1[0];
        let t2 = c2[0];
        let tr = info.timeRange;
        //if ((tr[0] <= t1) && (t1 <= tr[1])) {
        let tr2 = [tr[0] + t2 - t1, tr[1] + t2 - t1];
        this.setState({
            dragTimeRange: tr2
        });
        // }
    }
    _handleMouseDragRelease = (X) => {
        this._dragging = false;
        let tr = this.state.dragTimeRange;
        this.setState({
            dragTimeRange: null
        });
        this.props.onTimeRangeChanged(tr);
    }
    render() {
        let layers = [
            this._mainLayer
        ];
        return (
            <CanvasWidget
                layers={layers}
                width={this.props.width}
                height={this.props.height}
                onMousePress={this._handleMousePress}
                onMouseRelease={this._handleMouseRelease}
                onMouseDrag={this._handleMouseDrag}
                onMouseDragRelease={this._handleMouseDragRelease}
            />
        );
    }
}