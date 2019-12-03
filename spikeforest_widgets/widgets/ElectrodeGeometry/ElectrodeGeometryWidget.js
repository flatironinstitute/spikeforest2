import React, { Component } from "react";
import CanvasWidget, { CanvasWidgetLayer } from '../jscommon/CanvasWidget';
import AutoDetermineWidth from '../jscommon/AutoDetermineWidth';
const stable_stringify = require('json-stable-stringify');

export default class ElectrodeGeometryWidget extends Component {
    render() {
        return (
            <AutoDetermineWidth>
                <ElectrodeGeometryWidgetInner {...this.props} />
            </AutoDetermineWidth>
        );
    }
}

class ElectrodeGeometryWidgetInner extends Component {
    constructor(props) {
        super(props);
        this.xmin = 0;
        this.xmax = 1;
        this.ymin = 0;
        this.ymax = 2;
        this.transpose = false;
        this.channel_rects = {};
        this.dragSelectRect = null;

        this.state = {
            hoveredElectrodeIds: {},
            _canvasWidth: 0,
            _canvasHeight: 0
        }

        this.dragSelectLayer = new CanvasWidgetLayer(this.paintDragSelect);
        this.mainLayer = new CanvasWidgetLayer(this.paintMainLayer);
    }

    componentDidMount() {
        this.computeSize();
    }

    componentWillUnmount() {
    }

    componentDidUpdate(prevProps) {
        if (
            (this.props.locations != prevProps.locations) ||
            (this.props.ids != prevProps.ids) ||
            (this.props.width != prevProps.width) ||
            (this.props.height != prevProps.height) ||
            (this.props.maxWidth != prevProps.maxWidth) ||
            (this.props.maxHeight != prevProps.maxHeight)
        ) {
            this.computeSize();
            this.mainLayer.repaint();
        }
        else {
            this.mainLayer.repaint();
        }
    }

    computeSize() {
        this.updatePositions();

        let W = this.props.width;
        if (!W) W=400;
        
        let H = this.props.height;
        let x1 = this.xmin - this.mindist, x2 = this.xmax + this.mindist;
        let y1 = this.ymin - this.mindist, y2 = this.ymax + this.mindist;
        let w0 = x2 - x1, h0 = y2 - y1;
        if (this.transpose) {
            let w0_tmp = w0;
            w0 = h0;
            h0 = w0_tmp;
        }

        if (!H) {
            if (!w0) {
                H = 100;
            }
            else {
                H = h0 / w0 * W;
            }
        }
        const maxWidth = this.props.maxWidth || 500;
        const maxHeight = this.props.maxHeight || 500;
        if (W > maxWidth) {
            W = maxWidth;
            H = h0 * W / w0;
        }
        if (H > maxHeight) {
            H = maxHeight;
            W = w0 * H / h0;
        }
        this.setState({
            _canvasWidth: W,
            _canvasHeight: H
        });
    }

    paintDragSelect = (painter) => {
        if (this.dragSelectRect) {
            painter.fillRect(this.dragSelectRect, 'lightgray');
        }
    }

    ids() {
        if (this.props.ids) {
            return this.props.ids;
        }
        else if (this.props.locations) {
            let ids = [];
            for (let i=0; i<this.props.locations.length; i++) {
                ids.push(i);
            }
            return ids;
        }
        else {
            return [];
        }
    }

    paintMainLayer = (painter) => {
        let ids = this.ids();

        const W = this.state._canvasWidth;
        const H = this.state._canvasHeight;

        let W1 = W, H1 = H;
        if (this.transpose) {
            W1 = H;
            H1 = W;
        }

        let x1 = this.xmin - this.mindist, x2 = this.xmax + this.mindist;
        let y1 = this.ymin - this.mindist, y2 = this.ymax + this.mindist;
        let w0 = x2 - x1, h0 = y2 - y1;
        let offset, scale;
        if (w0 * H1 > h0 * W1) {
            scale = W1 / w0;
            offset = [0 - x1 * scale, (H1 - h0 * scale) / 2 - y1 * scale];
        } else {
            scale = H1 / h0;
            offset = [(W1 - w0 * scale) / 2 - x1 * scale, 0 - y1 * scale];
        }
        this.channel_rects = {};
        if (this.props.locations) {
            for (let i in this.props.locations) {
                let id0 = ids[i];
                let pt0 = this.props.locations[i];
                let x = pt0[0] * scale + offset[0];
                let y = pt0[1] * scale + offset[1];
                let rad = this.mindist * scale / 3;
                let x1 = x, y1 = y;
                if (this.transpose) {
                    x1 = y;
                    y1 = x;
                }
                let col = this.getElectrodeColor(id0);
                let rect0 = [x1 - rad, y1 - rad, rad * 2, rad * 2];
                painter.fillEllipse(rect0, col);
                this.channel_rects[i] = rect0;
                painter.setBrush({ color: 'white' });
                painter.setFont({ 'pixel-size': rad });
                painter.drawText(rect0, { AlignCenter: true, AlignVCenter: true }, id0);
            }
        }
    }

    updatePositions() {
        if (!this.props.locations) {
            return;
        }
        let pt0 = this.props.locations[0] || [0, 0];
        let xmin = pt0[0], xmax = pt0[0];
        let ymin = pt0[1], ymax = pt0[1];
        for (let i in this.props.locations) {
            let pt = this.props.locations[i];
            xmin = Math.min(xmin, pt[0]);
            xmax = Math.max(xmax, pt[0]);
            ymin = Math.min(ymin, pt[1]);
            ymax = Math.max(ymax, pt[1]);
        }
        // if (xmax === xmin) xmax++;
        // if (ymax === ymin) ymax++;

        this.xmin = xmin; this.xmax = xmax;
        this.ymin = ymin; this.ymax = ymax;

        // this.transpose = (this.ymax - this.ymin > this.xmax - this.xmin);

        let mindists = [];
        for (var i in this.props.locations) {
            let pt0 = this.props.locations[i];
            let mindist = -1;
            for (let j in this.props.locations) {
                let pt1 = this.props.locations[j];
                let dx = pt1[0] - pt0[0];
                let dy = pt1[1] - pt0[1];
                let dist = Math.sqrt(dx * dx + dy * dy);
                if (dist > 0) {
                    if ((dist < mindist) || (mindist < 0))
                        mindist = dist;
                }
            }
            if (mindist > 0) mindists.push(mindist);
        }
        let avg_mindist = compute_average(mindists);
        if (avg_mindist <= 0) avg_mindist = 1;
        this.mindist = avg_mindist;
    }

    getElectrodeColor(id) {
        let color = 'rgb(0, 0, 255)';
        let color_hover = 'rgb(100, 100, 255)';
        let color_current = 'rgb(200, 200, 100)';
        let color_current_hover = 'rgb(220, 220, 100)';
        let color_selected = 'rgb(180, 180, 150)';
        let color_selected_hover = 'rgb(200, 200, 150)';

        if (id === this.props.currentElectrodeId) {
            if (id in this.state.hoveredElectrodeIds) {
                return color_current_hover;
            }
            else {
                return color_current;
            }
        }
        else if ((this.props.selectedElectrodeIds || {})[id]) {
            if (id in this.state.hoveredElectrodeIds) {
                return color_selected_hover;
            }
            else {
                return color_selected;
            }
        }
        else {
            if (id in this.state.hoveredElectrodeIds) {
                return color_hover;
            }
            else {
                return color;
            }
        }
    }

    electrodeIdAtPixel(pos) {
        const ids = this.ids();
        for (let i in this.channel_rects) {
            let rect0 = this.channel_rects[i];
            if ((rect0[0] <= pos[0]) && (pos[0] <= rect0[0] + rect0[2])) {
                if ((rect0[1] <= pos[1]) && (pos[1] <= rect0[1] + rect0[2])) {
                    return ids[i];
                }
            }
        }
        return null;
    }

    electrodeIdsInRect(rect) {
        const ids = this.ids();
        let ret = [];
        for (let i in this.channel_rects) {
            let rect0 = this.channel_rects[i];
            if (rects_intersect(rect, rect0)) {
                ret.push(ids[i]);
            }
        }
        return ret;
    }

    setHoveredElectrodeId(id) {
        this.setHoveredElectrodeIds([id]);
    }

    setHoveredElectrodeIds(ids) {
        let tmp = {};
        for (let id of ids)
            tmp[id] = true;
        if (JSON.parse(stable_stringify(tmp)) === this.state.hoveredElectrodeIds)
            return;
        this.setState({
            hoveredElectrodeIds: tmp
        });
    }

    setCurrentElectrodeId(id) {
        if (id === this.props.currentElectrodeId)
            return;
        this.props.onCurrentElectrodeIdChanged && this.props.onCurrentElectrodeIdChanged(id);
    }

    setSelectedElectrodeIds(ids) {
        let newsel = {};
        for (let id of ids) {
            newsel[id] = true;
        }
        if (stable_stringify(newsel) === stable_stringify(this.props.selectedElectrodeIds || {})) {
            return;
        }
        this.props.onSelectedElectrodeIdsChanged && this.props.onSelectedElectrodeIdsChanged(newsel);
    }

    selectElectrodeId(id) {
        let x = JSON.parse(JSON.stringify(this.props.selectedElectrodeIds || {}));
        x[id] = true;
        let ids = [];
        for (let id0 in x) ids.push(id0);
        this.setSelectedElectrodeIds(ids);
    }

    deselectElectrodeId(id) {
        let x = JSON.parse(JSON.stringify(this.props.selectedElectrodeIds || {}));
        delete x[id];
        let ids = [];
        for (let id0 in x) ids.push(id0);
        this.setSelectedElectrodeIds(ids);
    }

    handleMousePress = (X) => {
        if (!X) return;
        let elec_id = this.electrodeIdAtPixel(X.pos);
        if ((X.modifiers.ctrlKey) || (X.modifiers.shiftKey)) {
            if (elec_id in (this.props.selectedElectrodeIds || {})) {
                this.deselectElectrodeId(elec_id);
            }
            else {
                this.selectElectrodeId(elec_id);
            }
        }
        else {
            this.setCurrentElectrodeId(elec_id);
            this.setSelectedElectrodeIds([elec_id]);
        }
    }

    handleMouseRelease = (X) => {
    }

    handleMouseMove = (X) => {
        if (!X) return;
        if (!this.dragSelectRect) {
            let elec_id = this.electrodeIdAtPixel(X.pos);
            this.setHoveredElectrodeId(elec_id);
        }
    }

    handleMouseDrag = (X) => {
        if (JSON.stringify(X.rect) !== JSON.stringify(this.dragSelectRect)) {
            this.dragSelectRect = X.rect;
            this.setHoveredElectrodeIds(this.electrodeIdsInRect(this.dragSelectRect));
        }
    }

    handleMouseDragRelease = (X) => {
        let ids = this.electrodeIdsInRect(X.rect);
        this.setCurrentElectrodeId(null);
        this.setSelectedElectrodeIds(ids);
        if (ids.length === 1) {
            this.setCurrentElectrodeId(ids[0]);
        }
        this.dragSelectRect = null;
        this.setState({
            hoveredElectrodeIds: {}
        });
    }

    render() {
        if (this.props.locations === undefined) {
            return <span>
                <div>Loading...</div>
            </span>
        }
        else if (this.props.locations === null) {
            return <span>
                <div>Not found.</div>
            </span>
        }
        let layers = [
            this.dragSelectLayer,
            this.mainLayer
        ];
        return <CanvasWidget
            layers={layers}
            width={this.state._canvasWidth}
            height={this.state._canvasHeight}
            onMousePress={this.handleMousePress}
            onMouseRelease={this.handleMouseRelease}
            onMouseDrag={this.handleMouseDrag}
            onMouseDragRelease={this.handleMouseDragRelease}
        />;
    }
}

function rects_intersect(R1, R2) {
    if ((R2[0] + R2[2] < R1[0]) || (R2[0] > R1[0] + R1[2])) return false;
    if ((R2[1] + R2[3] < R1[1]) || (R2[1] > R1[1] + R1[3])) return false;
    return true;
}

function compute_average(list) {
    if (list.length === 0) return 0;
    var sum = 0;
    for (var i in list) sum += list[i];
    return sum / list.length;
}
