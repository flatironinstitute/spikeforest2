import React, { Component } from 'react';
import CanvasWidget, { CanvasWidgetLayer } from '../../jscommon/CanvasWidget';
import Plotly from './plotly.patched.min.js';
import createPlotlyComponent from 'react-plotly.js/factory';
const Plot = createPlotlyComponent(Plotly);

export default Plot;

export class LightPlot extends CanvasWidget {
    constructor(props) {
        super(props);
        this.state({
            canvasWidth: 0,
            canvasHeight: 0
        })
        this.plotLayer = new CanvasWidgetLayer(this.paintPlotLayer);
        this.titleLayer = new CanvasWidgetLayer(this.paintTitleLayer);
    }

    componentDidMount() {
        this.updateSize();
    }

    componentWillUnmount() {
    }

    componentDidUpdate(prevProps) {
        this.updateSize();
    }

    updateSize() {
        const { data, layout } = this.props;
        let margin = layout.margin || {};
        this.plotLayer.setMargins(margin.l || 0, margin.r || 0, margin.t || 0, margin.b || 0);
        this.titleLayer.setMargins(margin.l || 0, margin.r || 0, margin.t || 0, margin.b || 0);

        {
            let xmin, xmax;
            if (layout.xaxis.autorange) {
                for (let i=0; i<data.length; i++) {
                    let data0 = data[i];
                    const xdata0 = data0.x;
                    let xmin0 = compute_min(xdata0);
                    let xmax0 = compute_max(xdata0);
                    if (i == 0) {
                        xmin = xmin0;
                        xmax = xmax0;
                    }
                    else {
                        xmin = Math.min(xmin, xmin0);
                        xmax = Math.max(xmax, xmax0);
                    }
                }
            }
            else {
                xmin = layout.xaxis.range[0],
                xmax = layout.xaxis.range[1]
            }
            this.plotLayer.setCoordXRange(xmin, xmax);
        }
        {
            let ymin, ymax;
            if (layout.yaxis.autorange) {
                for (let i=0; i<data.length; i++) {
                    let data0 = data[i];
                    const ydata0 = data0.y;
                    let ymin0 = compute_min(ydata0);
                    let ymax0 = compute_max(ydata0);
                    if (data0.type == 'bar') {
                        ymin0 = Math.min(ymin0, 0);
                    }
                    if (i == 0) {
                        ymin = ymin0;
                        ymax = ymax0;
                    }
                    else {
                        ymin = Math.min(ymin, ymin0);
                        ymax = Math.max(ymax, ymax0);
                    }
                }
            }
            else {
                ymin = layout.yaxis.range[0],
                ymax = layout.yaxis.range[1]
            }
            this.plotLayer.setCoordYRange(ymin, ymax);
        }
        this.setState({
            canvasWidth: layout.width,
            canvasHeight: layout.height
        });
    }

    paintPlotLayer = (painter) => {
        const { data, layout } = this.props;

        painter.useCoords();

        for (let data0 of data) {
            if (data0.type === 'bar') {
                const xdata = data0.x;
                const ydata = data0.y;
                let wid = xdata[1] - xdata[0];
                for (let i=0; i<xdata.length; i++) {
                    let x0 = xdata[i];
                    let y0 = ydata[i];
                    painter.fillRect(x0 - wid/2, 0, wid, y0, 'blue');
                }
            }
            else if (data0.type === 'scatter') {
                let mode = data0.mode || 'lines';
                const xdata = data0.x;
                const ydata = data0.y;
                let color = data0.color || 'black';
                
                if ((mode === 'lines') || (mode === 'line') || (mode == 'lines+markers')) {
                    let line_color = color;
                    if ((data0.line) && (data0.line.color))
                        line_color = data0.line.color;
                    let line_width = 1;
                    if ((data0.line) && ('width' in data0.line)) {
                        line_width = data0.line.width;
                    }
                    painter.setPen({color: line_color, width: line_width});
                    let path = painter.newPainterPath();
                    for (let i=0; i<xdata.length; i++) {
                        let x0 = xdata[i];
                        let y0 = ydata[i];
                        path.lineTo(x0, y0);
                    }
                    painter.drawPath(path);
                }
                if ((mode === 'markers') || (mode == 'lines+markers')) {
                    let marker_color = color;
                    if ((data0.marker) && (data0.marker.color))
                        marker_color = data0.marker.color;
                    painter.setPen({color: marker_color});
                    for (let i=0; i<xdata.length; i++) {
                        let x0 = xdata[i];
                        let y0 = ydata[i];
                        let rad0 = 4;
                        painter.drawMarker(x0, y0, rad0, 'circle');
                    }    
                }
            }
        }
    }
    paintTitleLayer = (painter) => {
        const { layout } = this.props;

        if (layout.title) {
            painter.drawText([0, 0, this.titleLayer.width(), (layout.margin || {}).t || 0], {AlignBottom: true, AlignCenter: true}, layout.title);
        }
    }

    render() {
        let layers = [
            this.plotLayer,
            this.titleLayer
        ];
        return <CanvasWidget
            layers={layers}
        />
    }
}

function compute_min(x) {
    if (x.length == 0) return 0;
    let ret = x[0];
    for (let i = 0; i < x.length; i++) {
        if (x[i] < ret) ret = x[i];
    }
    return ret;
}

function compute_max(x) {
    if (x.length == 0) return 0;
    let ret = x[0];
    for (let i = 0; i < x.length; i++) {
        if (x[i] > ret) ret = x[i];
    }
    return ret;
}