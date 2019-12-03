import React, { Component } from 'react';
import CanvasWidget, { CanvasWidgetLayer } from '../jscommon/CanvasWidget';
import TimeWidgetBottomBar from './TimeWidgetBottomBar';
import TimeWidgetToolBar from './TimeWidgetToolBar';
import SpanWidget from './SpanWidget';
import Splitter from './Splitter';
export { PainterPath } from '../jscommon/CanvasWidget';

function g_elapsed() {
    return (new Date()) - 0;
}

export default class TimeWidget extends Component {
    constructor(props) {
        super(props);
        this.state = {
            bottomBarInfo: {show: true},
            spanWidgetInfo: {}
        };

        this._anchorTimeRange = null;
        this._dragging = false;
        this._toolbarWidth = 50;
        this._spanWidgetHeight = 50;
        this._bottomBarHeight = 0;
        this._paintPanelIndex = 0;
        this._paintPanelCode = 0;
        this._statusText = '';
        this._timeRange = [0, 10000];
        this._currentTime = null;

        this._timeAxisLayer = new CanvasWidgetLayer(this.paintTimeAxisLayer);
        this._mainLayer = new CanvasWidgetLayer(this.paintMainLayer);
        this._cursorLayer = new CanvasWidgetLayer(this.paintCursorLayer);
        this._panelLabelLayer = new CanvasWidgetLayer(this.paintPanelLabelLayer);

        this._allLayers = [
            this._timeAxisLayer,
            this._mainLayer,
            this._cursorLayer,
            this._panelLabelLayer
        ];

        this._cursorLayer.setMargins(50, 10, 15, 50);
    }
    componentDidMount() {
        this.props.registerRepainter && this.props.registerRepainter(() => {this._mainLayer.repaint()});
        this._updateInfo();
        if (this.props.currentTime !== undefined) {
            this._currentTime = this.props.currentTime;            
        }
        if (this.props.timeRange !== undefined) {
            this.setTimeRange(this.props.timeRange);
        }
        this.updateLayout();
    }
    componentDidUpdate(prevProps) {
        if (this.props.currentTime != prevProps.currentTime) {
            this.setCurrentTime(this.props.currentTime);
        }
        if (this.props.timeRange != prevProps.timeRange) {
            this.setTimeRange(this.props.timeRange);
        }
        this._updateInfo();
        this.updateLayout();
    }
    paintMainLayer = (painter) => {
        let timer = new Date();
        this._paintPanelIndex = 0;
        this._paintPanelCode++;
        painter.useCoords();
        this._mainLayer.setCoordXRange(0, 1);
        this._mainLayer.setCoordYRange(0, 1);
        this._mainLayer.setMargins(50, 10, 15, 50);
        painter.setPen({color: 'gray'});
        painter.drawLine(0, 0, 0, 1);
        painter.drawLine(1, 0, 1, 1);
        painter.drawLine(0, 1, 1, 1);

        // Keep this for highlighting spike raster plots
        // // highlight selected
        // for (let panel of this.props.panels) {
        //     if (panel.selected()) {
        //         this._mainLayer.setMargins(50, 15, panel._yRange[0], this._mainLayer.height() - panel._yRange[1]);
        //         this._mainLayer.setCoordXRange(0, 1);
        //         this._mainLayer.setCoordYRange(0, 1);
        //         painter.fillRect(0, 0, 1, 1, 'yellow');
        //     }
        // }

        this._paintPanels(painter, this._paintPanelCode);
    }

    _paintPanels = (painter, paintPanelCode) => {
        if (paintPanelCode !== this._paintPanelCode) {
            // we have started a new painting
            return;
        }
        const panels = this.props.panels;
        const indexPermutation = _getIndexPermutation(panels.length);
        let timer = new Date();
        while (this._paintPanelIndex < panels.length) {
            const panel = panels[indexPermutation[this._paintPanelIndex]];
            this._mainLayer.setCoordXRange(this._timeRange[0], this._timeRange[1]);
            this._mainLayer.setMargins(50, 15, panel._yRange[0], this._mainLayer.height() - panel._yRange[1]);
            // v1=-1 => y1
            //  v2=1 => y2
            // (v1-a) / (b-a) * H = y1
            // (v2-a) / (b-a) * H = y2
            // v1 - a = y1/H * (b-a) 
            // v2 - a = y2/H * (b-a) 
            // (v2 - v1) = (y2-y1)/H * (b-a)
            // b-a = (v2-v1) / (y2-y1) * H
            // a = v1 - y1/H*(b-a)

            // let v1 = panel._coordYRange[0];
            // let v2 = panel._coordYRange[1];
            // let b_minus_a = (v2 - v1) / (panel._yRange[1] - panel._yRange[0]) * (this.props.height - this._spanWidgetHeight - this._bottomBarHeight);
            // let a = v1 - panel._yRange[0] * b_minus_a / (this.props.height - this._spanWidgetHeight - this._bottomBarHeight);
            // let b = a + b_minus_a;

            //this._mainLayer.setCoordYRange(a, b);
            this._mainLayer.setCoordYRange(panel._coordYRange[0], panel._coordYRange[1]);
            panel.paint(painter, clone(this._timeRange));
            this._paintPanelIndex++;

            let elapsed = (new Date()) - timer;
            if ((elapsed > 200) && (!painter.exportingFigure())) {
                setTimeout(() => {
                    this._paintPanels(painter, paintPanelCode);
                }, 100);
                return;
            }
        }
    }
    paintCursorLayer = (painter) => {
        if (painter.exportingFigure()) return;
        this._cursorLayer.setCoordXRange(this._timeRange[0], this._timeRange[1]);
        this._cursorLayer.setCoordYRange(0, 1);
        painter.useCoords();

        if (this._currentTime !== null) {
            if ((this._timeRange[0] <= this._currentTime) && (this._currentTime <= this._timeRange[1])) {
                painter.setPen({width:2, color: 'blue'});
                painter.drawLine(this._currentTime, 0, this._currentTime, 1);
            }
        }
    }
    paintTimeAxisLayer = (painter) => {
        let W = this._timeAxisLayer.width();
        let H = this._timeAxisLayer.height();
        this._timeAxisLayer.setMargins(50, 10, H-50, 0);
        this._timeAxisLayer.setCoordXRange(this._timeRange[0], this._timeRange[1]);
        this._timeAxisLayer.setCoordYRange(0, 1);
        painter.useCoords();
        painter.setPen({color: 'rgb(22, 22, 22)'});
        painter.drawLine(this._timeRange[0], 1, this._timeRange[1], 1);
        let samplerate = this.props.samplerate;
        let ticks = get_ticks(this._timeRange[0], this._timeRange[1], W, samplerate);
        for (let tick of ticks) {
            if (!tick.scale_info) {
                painter.drawLine(tick.t, 1, tick.t, 1 - tick.height);
            }
            else {                let info = tick;
                painter.drawLine(info.t1, 0.45, info.t2, 0.45);
                painter.drawLine(info.t1, 0.45, info.t1, 0.5);
                painter.drawLine(info.t2, 0.45, info.t2, 0.5);
                let rect = [info.t1, 0, info.t2 - info.t1, 0.35];
                let alignment = {AlignTop: true, AlignCenter: true};
                painter.drawText(rect, alignment, info.label + '');
            }
        }
    }
    paintPanelLabelLayer = (painter) => {
        let W = this._mainLayer.width();
        let H = this._mainLayer.height();
        
        painter.useCoords();

        const panels = this.props.panels;

        for (let i = 0; i < panels.length; i++) {
            let panel = panels[i];
            let p1 = i / panels.length;
            let p2 = (i + 1) / panels.length;
            this._panelLabelLayer.setMargins(0, W - 50, 15 + (H - 50 - 15) * p1, H - (15 + (H - 50 - 15) * p2));
            this._panelLabelLayer.setCoordXRange(0, 1);
            this._panelLabelLayer.setCoordYRange(0, 1);
            
            let rect = [0.2, 0.2, 0.6, 0.6];
            let alignment = {AlignRight: true, AlignVCenter: true};
            panel._opts.label + '' && painter.drawText(rect, alignment, panel._opts.label + '');
        }
    }
    numTimepoints() {
        return this.props.numTimepoints;
    }
    setCurrentTime(t) {
        if (t < 0) t = 0;
        if (t >= this.numTimepoints())
            t = this.numTimepoints() - 1;
        if (this._currentTime === t)
            return;
        this._currentTime = t;
        this._cursorLayer.repaint();
        this._updateInfo();
        this.props.onCurrentTimeChanged && this.props.onCurrentTimeChanged(t);
    }
    setStatusText(txt) {
        if (txt != this._statusText) {
            this._statusText = txt;
            this._updateInfo();
        }
    }
    setTimeRange(trange) {
        let tr = clone(trange);
        if (tr[1] >= this.numTimepoints()) {
            let delta = this.numTimepoints() -1 - tr[1];
            tr[0] += delta;
            tr[1] += delta;
        }
        if (tr[0] < 0) {
            let delta = -tr[0];
            tr[0] += delta;
            tr[1] += delta;
        }
        if (tr[1] >= this.numTimepoints()) {
            tr[1] = this.numTimepoints() - 1;
        }
        if (this.props.maxTimeSpan) {
            if (tr[1] - tr[0] > this.props.maxTimeSpan) {
                return;
                // tr[0] = Math.max(0, Math.floor((tr[0] + tr[1]) / 2 - this.props.maxTimeSpan / 2));
                // tr[1] = tr[0] + this.props.maxTimeSpan;
            }
        }
        if ((this._timeRange[0] === tr[0]) && (this._timeRange[1] === tr[1])) {
            return;
        }
        this._timeRange = tr;
        // this._timeAxisLayer.repaintImmediate();
        this._repaintAllLayers();
        this._updateInfo();
        this.props.onTimeRangeChanged && this.props.onTimeRangeChanged(tr);
    }
    updateLayout() {
        const panels = this.props.panels;
        let H0 = this.props.height - this._spanWidgetHeight - this._bottomBarHeight - 10 - 50;
        let panelHeight = H0 / panels.length;
        let y0 = 10;
        for (let panel of panels) {
            panel.setYRange(y0, y0+panelHeight);
            y0 += panelHeight;
        }
        this._updateInfo();
    }
    pixToTime(pix) {
        let coords = this._mainLayer.pixToCoords(pix);
        return coords[0];
    }
    _repaintAllLayers = () => {
        for (let L of this._allLayers) {
            L.repaint();
        }
    }
    _updateSpanWidgetInfo() {
        let info = {
            numTimepoints: this.numTimepoints(),
            currentTime: this._currentTime,
            timeRange: clone(this._timeRange),
            samplerate: this.props.samplerate,
            statusText: this._statusText
        };
        this._setSpanWidgetInfo(info);
    }
    _setSpanWidgetInfo(info) {
        if (JSON.stringify(info) != JSON.stringify(this.state.spanWidgetInfo)) {
            this.setState({
                spanWidgetInfo: info
            });
        }
    }
    _updateInfo() {
        this._updateBottomBarInfo();
        this._updateSpanWidgetInfo();
    }
    _updateBottomBarInfo() {
        let info = {
            show: true,
            currentTime: this._currentTime,
            timeRange: clone(this._timeRange),
            samplerate: this.props.samplerate,
            statusText: this._statusText
        };
        this._setBottomBarInfo(info);
    }
    _setBottomBarInfo(info) {
        if (JSON.stringify(info) != JSON.stringify(this.state.bottomBarInfo)) {
            this.setState({
                bottomBarInfo: info
            });
        }
        let height = info.show ? 40 : 0;
        if (height !== this._bottomBarHeight) {
            this._bottomBarHeight = height;
            this._updateInfo();
        }
    }
    handle_mouse_press = (X) => {
        let t = this.pixToTime(X.pos);
        this._anchorTimeRange = clone(this._timeRange);
        this._dragging = false;
    }

    handle_mouse_release = (X) => {
        if (!this._dragging) {
            const t = this.pixToTime(X.pos);
            this.setCurrentTime(t);
        }
    }

    handle_mouse_drag = (X) => {
        if (!this._anchorTimeRange) return;
        this._dragging = true;
        let t1 = this.pixToTime(X.anchor);
        let t2 = this.pixToTime(X.pos);
        let tr = clone(this._anchorTimeRange);
        tr[0] += t1 - t2;
        tr[1] += t1 - t2;
        this.setTimeRange(tr);
    }

    handle_mouse_drag_release = (X) => {
        this._dragging = false;
    }

    handle_key_press = (event) => {
        for (let a of this.props.actions || []) {
            if (a.key === event.keyCode) {
                a.callback();
                event.preventDefault();
                return false;
            }
        }
        switch (event.keyCode) {
            case 37: this.handle_key_left(event); event.preventDefault(); return false;
            case 39: this.handle_key_right(event); event.preventDefault(); return false;
            case 187: this.zoomTime(1.15); event.preventDefault(); return false;
            case 189: this.zoomTime(1 / 1.15); event.preventDefault(); return false;
            case 35 /*end*/: this.handle_end(event); event.preventDefault(); return false;
            case 36 /*end*/: this.handle_home(event); event.preventDefault(); return false;
            default: console.info('key: ' + event.keyCode);
        }
    }

    handle_key_left = (X) => {
        let span = this._timeRange[1] - this._timeRange[0];
        this.translateTime(-span * 0.2);
    }
    handle_key_right = (X) => {
        let span = this._timeRange[1] - this._timeRange[0];
        this.translateTime(span * 0.2);
    }
    handle_home = (X) => {
        this.translateTime(-this._currentTime);
    }
    handle_end = (X) => {
        this.translateTime(this.numTimepoints()-this._currentTime);
    }
    translateTime = (delta_t) => {
        let tr = clone(this._timeRange);
        tr[0] += delta_t;
        tr[1] += delta_t;
        let t0 = this._currentTime + delta_t;
        this.setCurrentTime(t0);
        this.setTimeRange(tr);
    }
    zoomTime = (factor) => {
        let anchor_time = this._currentTime;
        let tr = clone(this._timeRange);
        if ((anchor_time < tr[0]) || (anchor_time > tr[1]))
            anchor_time = tr[0];
        let old_t1 = tr[0];
        let old_t2 = tr[1];
        let t1 = anchor_time + (old_t1 - anchor_time) / factor;
        let t2 = anchor_time + (old_t2 - anchor_time) / factor;
        this.setTimeRange([t1, t2]);
    }
    ensureCurrentTimeVisibleByChangingTimeRange = () => {
        if (this._currentTime === null)
            return;
        if ((this._timeRange[0] < this._currentTime) && (this._currentTime < this._timeRange[1]))
            return;
        const span = this._timeRange[1] - this._timeRange[0];
        let tr = [this._currentTime - span / 2, this._currentTime + span / 2];
        this.setTimeRange(tr);
    }

    ensureCurrentTimeVisibleByChangingCurrentTime = () => {
        if (this._currentTime === null)
            return;
        if ((this._timeRange[0] < this._currentTime) && (this._currentTime < this._timeRange[1]))
            return;
        let t = (this._timeRange[0] + this._timeRange[1]) / 2;
        this.setCurrentTime(t);
    }

    render() {
        let layers = this._allLayers;
        let innerContainer = (
            <InnerContainer>
                <SpanWidget
                    width={this.props.width}
                    height={this._spanWidgetHeight}
                    info={this.state.spanWidgetInfo || {}}
                    onCurrentTimeChanged={(t) => {this.setCurrentTime(t); this.ensureCurrentTimeVisibleByChangingTimeRange();}}
                    onTimeRangeChanged={(tr) => {if (tr) {this.setTimeRange(tr); this.ensureCurrentTimeVisibleByChangingCurrentTime();}}}
                />
                <CanvasWidget
                    layers={layers}
                    width={this.props.width}
                    height={this.props.height - this._spanWidgetHeight - this._bottomBarHeight}
                    onMousePress={this.handle_mouse_press}
                    onMouseRelease={this.handle_mouse_release}
                    onMouseDrag={this.handle_mouse_drag}
                    onMouseDragRelease={this.handle_mouse_drag_release}
                    onKeyPress={this.handle_key_press}
                    menuOpts={{exportSvg: true}}
                />
                <TimeWidgetBottomBar
                    width={this.props.width}
                    height={this._bottomBarHeight}
                    info={this.state.bottomBarInfo || {}}
                    onCurrentTimeChanged={(t) => {this.setCurrentTime(t); this.ensureCurrentTimeVisibleByChangingTimeRange();}}
                    onTimeRangeChanged={(tr) => {if (tr) {this.setTimeRange(tr); this.ensureCurrentTimeVisibleByChangingCurrentTime();}}}
                />
            </InnerContainer>
        );
        let leftPanel = this.props.leftPanel
        return (
            <OuterContainer
                width={this.props.width}
                height={this.props.height}
            >
                <TimeWidgetToolBar
                    width={this._toolbarWidth}
                    height={this.props.height}
                    top={this._spanWidgetHeight}
                    onZoomIn={() => {this.zoomTime(1.15)}}
                    onZoomOut={() => {this.zoomTime(1 / 1.15)}}
                    onShiftTimeLeft={() => {this.handle_key_left()}}
                    onShiftTimeRight={() => {this.handle_key_right()}}
                    customActions={this.props.actions || []}
                />
                <Splitter
                    width={this.props.width - this._toolbarWidth}
                    height={this.props.height}
                    left={this._toolbarWidth}
                >
                    {
                        leftPanel ? (
                            [leftPanel, innerContainer]
                        ) : (
                            innerContainer
                        )
                    }
                </Splitter>
            </OuterContainer>
        );
    }
}

class InnerContainer extends Component {
    render() {
        let style0 = {
            position: 'absolute',
            left: this.props.left || 0,
            top: 0,
            width: this.props.width,
            height: this.props.height
        }
        return (
            <div style={style0}>
                {
                    this.props.children.map((child, ii) => (
                        <child.type key={ii} {...child.props} width={this.props.width} />
                    ))
                }
            </div>
        )
    }
}

class OuterContainer extends Component {
    render() {
        let style0 = {
            position: 'relative',
            left: 0,
            top: 0,
            width: this.props.width,
            height: this.props.height
        }
        return (
            <div style={style0}>
                {this.props.children}
            </div>
        )
    }
}



function get_ticks(t1, t2, width, samplerate) {

    let W = width;

    // adapted from MountainView
    const min_pixel_spacing_between_ticks = 15;
    const tickinfo = [
        {
            name: '1 ms',
            interval: 1e-3 * samplerate
        },
        {
            name: '10 ms',
            interval: 10 * 1e-3 * samplerate
        },
        {
            name: '100 ms',
            interval: 100 * 1e-3 * samplerate
        },
        {
            name: '1 s',
            interval: 1 * samplerate
        },
        {
            name: '10 s',
            interval: 10 * samplerate
        },
        {
            name: '1 m',
            interval: 60 * samplerate
        },
        {
            name: '10 m',
            interval: 10 * 60 * samplerate
        },
        {
            name: '1 h',
            interval: 60 * 60 * samplerate
        },
        {
            name: '1 day',
            interval: 24 * 60 * 60 * samplerate
        }
    ];

    let ticks = [];
    let first_scale_shown = true;
    let height = 0.2;
    for (let info of tickinfo) {
        const scale_pixel_width = W / (t2 - t1) * info.interval;
        let show_scale = false;
        if (scale_pixel_width >= min_pixel_spacing_between_ticks) {
            show_scale = true;
        }
        else {
            show_scale = false;
        }
        if (show_scale) {
            // msec
            let u1 = Math.floor(t1 / info.interval);
            let u2 = Math.ceil(t2 / info.interval);
            let first_tick = true;
            for (let u = u1; u <= u2; u++) {
                let t = u * info.interval;
                if ((t1 <= t) && (t <= t2)) {
                    let tick = {
                        t: t,
                        height: height
                    };
                    if (first_scale_shown) {
                        if (first_tick) {
                            ticks.push({
                                scale_info: true,
                                t1: t1,
                                t2: t1 + info.interval,
                                label: info.name
                            });
                            first_tick = false;
                        }
                        first_scale_shown = false;
                    }
                    ticks.push(tick);
                }
            }
            height += 0.1;
            height = Math.min(height, 0.45);
        }
    }
    // remove duplicates
    let ticks2 = [];
    for (let i = 0; i < ticks.length; i++) {
        let tick = ticks[i];
        let duplicate = false;
        if (!tick.scale_info) {
            for (let j = i + 1; j < ticks.length; j++) {
                if (Math.abs(ticks[j].t - tick.t) < 1) {
                    duplicate = true;
                    break;
                }
            }
        }
        if (!duplicate) {
            ticks2.push(tick);
        }
    }
    return ticks2;
}

export class TimeWidgetPanel {
    constructor(onPaint, opts) {
        this.onPaint = onPaint;
        this._opts = opts;
        this.timeRange = null;
        this._yRange = [0, 1];
        this._coordYRange = [-1, 1];
    }
    selected() {
        return this._opts.selected ? true : false;
    }
    label() {
        return this._opts.label;
    }
    setYRange(y1, y2) {
        this._yRange = [y1, y2];
    }
    setCoordYRange(y1, y2) {
        this._coordYRange = [y1, y2];
    }
    paint(painter, timeRange) {
        this.onPaint(painter, timeRange);
    }
}

function _getIndexPermutation(N) {
    let ret = [];
    let indices = [];
    for (let i = 0; i < N; i++)
        indices.push(i);
    let used = [];
    for (let i of indices) {
        used.push(false);
    }
    let cur = 0;
    let increment = Math.floor(N / 2);
    if (increment < 1) increment = 1;
    while (ret.length < N) {
        if (!used[cur]) {
            ret.push(cur);
            used[cur] = true;
        }
        cur += increment;
        if (cur >= N) {
            cur = 0;
            if (increment <= 1) {
                increment = 1;
            }
            else {
                increment = Math.floor(increment / 2);
            }
        }
    }
    return ret;
}

function clone(obj) {
    return JSON.parse(JSON.stringify(obj));
}