import React, { Component } from 'react';
import TimeWidget, { PainterPath, TimeWidgetPanel } from '../TimeWidget/TimeWidget';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import { MdGridOn as SelectElectrodesIcon } from 'react-icons/md';
import SelectElectrodes from './SelectElectrodes';

export default class TimeseriesWidget extends Component {
    constructor(props) {
        super(props);
        this.state = {
            panels: [],
            timeRange: [0, 30000],
            currentTime: null,
            leftPanelMode: null,
            selectedElectrodeIds: {},
            selectElectrodesPrefs: {viewOnlySelectedChannels: false}
        }
        this._downsampleFactor = 1;
        this.channel_colors = mv_default_channel_colors(); // colors of the channel traces
        this.y_scale_factor = 1;
        this._repainter = null;
    }
    componentDidMount() {
        this.y_scale_factor = this.props.y_scale_factor;

        if (this.props.timeseriesModel) {
            // this happens when the timeseries model receives new data
            this.props.timeseriesModel.onDataSegmentSet((ds_factor, t1, t2) => {
                let trange = this.timeRange();
                if (!trange) return;
                if ((t1 <= trange[1]) && (t2 >= trange[0])) {
                    // if the new chunk is in range of what we are viewing, we repaint
                    this._repaint();
                }
            });

            this.updateDownsampleFactor();

            this.updatePanels();
        }
    }
    componentDidUpdate(prevProps, prevState) {
        this.updateDownsampleFactor();
        if ((this.props.width !== prevProps.width) || (this.props.height !== prevProps.height)) {
            this.updatePanels();
        }
        else if (this.state.selectedElectrodeIds != prevState.selectedElectrodeIds) {
            this.updatePanels();
        }
        else if (this.state.selectElectrodesPrefs.viewOnlySelectedChannels != prevState.selectElectrodesPrefs.viewOnlySelectedChannels) {
            this.updatePanels();
        }
        else if (this.state.timeRange != prevState.timeRange) {
            this._repaint();
        }
        else if (this.state.panels != prevState.panels) {
            this._repaint();
        }
    }
    updateDownsampleFactor() {
        let trange = this.timeRange();
        if (!trange) return;
        let factor0 = 1.3; // this is a tradeoff between rendering speed and appearance
        if ((this.props.num_channels) && (this.props.num_channels > 32)) {
            factor0 = 0.5;
        }
        let downsample_factor = determine_downsample_factor_from_num_timepoints(this.props.width * factor0, trange[1] - trange[0]);
        if (downsample_factor !== this._downsampleFactor) {
            this._downsampleFactor = downsample_factor;
            this._repaint();
        }
    }
    updatePanels() {
        const { num_channels, channel_ids } = this.props;
        if (!num_channels) return;
        let channelIndsToView = [];
        if (!this.state.selectElectrodesPrefs.viewOnlySelectedChannels) {
            for (let i=0; i<num_channels; i++) {
                channelIndsToView.push(i);
            }
        }
        else {
            for (let i=0; i<num_channels; i++) {
                if (this.state.selectedElectrodeIds[channel_ids[i]]) {
                    channelIndsToView.push(i);
                }
            }
        }
        let num_channels_to_view = channelIndsToView.length;
        
        const maxChannelsToLabel = Math.max(1, this.props.height / 18);
        let channelIndsToLabel = {};
        let incr = Math.ceil(num_channels_to_view / maxChannelsToLabel);
        for (let ii = 0; ii < num_channels_to_view; ii += incr) {
            channelIndsToLabel[channelIndsToView[ii]] = true;
        }
        let panels = [];
        for (let m of channelIndsToView) {
            let label = channelIndsToLabel[m] ? channel_ids[m] : '';
            let selected = (this.state.selectedElectrodeIds[channel_ids[m]]);
            let panel = new TimeWidgetPanel(
                (painter, timeRange) => {this.paintChannel(painter, timeRange, m, selected)},
                {label: label, selected: selected}
            );
            panel.setCoordYRange(-1, 1);
            panels.push(panel);
        }
        this.setState({
            panels: panels
        });
    }
    _toggleLeftPanelMode = (mode) => {
        if (mode === this.state.leftPanelMode) {
            this.setState({leftPanelMode: null});
        }
        else {
            this.setState({leftPanelMode: mode});
        }
    }
    _handleTimeRangeChanged = (tr) => {
        this.setState({
            timeRange: tr
        });
        this.updateDownsampleFactor();
    }
    _handleCurrentTimeChanged = (t) => {
        this.setState({
            currentTime: t
        });
    }
    timeRange() {
        return this.state.timeRange;
    }
    currentTime() {
        return this.state.currentTime;
    }
    paintChannel = (painter, timeRange, m, selected) => {
        let trange = timeRange;
        if (!trange) return;
        let y_offset = this.props.y_offsets[m];
        painter.setPen({color: 'black', width: 1});
        // painter.drawLine(trange[0], 0, trange[1], 0);

        let y_scale_factor = this.y_scale_factor;

        let t1 = Math.floor(trange[0]);
        let t2 = Math.floor(trange[1] + 1);
        if (t1 < 0) t1 = 0;
        if (t2 >= this.props.num_timepoints) t2 = this.props.num_timepoints;
        let downsample_factor = this._downsampleFactor;
        let t1b = Math.floor(t1 / downsample_factor);
        let t2b = Math.floor(t2 / downsample_factor);
        let pp = new PainterPath();
        // this.setStatusText(`Painting timepoints ${t1b} to ${t2b}; downsampling ${downsample_factor}`);
        let data0 = this.props.timeseriesModel.getChannelData(m, t1b, t2b, downsample_factor);

        // check to see if we actually got the data... if we did, then we will preload
        let gotAllTheData = true;
        for (let val of data0) {
            if (isNaN(val)) {
                gotAllTheData = false;
                break;
            }
        }
        // if (gotAllTheData) {
        //     // trigger pre-loading
        //     this.props.timeseriesModel.getChannelData(m, Math.floor(t1b / 3), Math.floor(t2b / 3), downsample_factor * 3, { request_only: true });
        //     if ((downsample_factor > 1) && (this.currentTime >= 0)) {
        //         let t1c = Math.floor(Math.max(0, (this.currentTime - 800) / (downsample_factor / 3)))
        //         let t2c = Math.floor(Math.min(this.props.timeseriesModel.numTimepoints(), (this.currentTime + 800) / (downsample_factor / 3)))
        //         this.props.timeseriesModel.getChannelData(m, t1c, t2c, downsample_factor / 3, { request_only: true });
        //     }
        // }

        if (downsample_factor == 1) {
            let penDown = false;
            for (let tt = t1; tt < t2; tt++) {
                let val = data0[tt - t1];
                if (!isNaN(val)) {
                    let val2 = (val + y_offset) * y_scale_factor;
                    if (penDown) {
                        pp.lineTo(tt, val2);    
                    }
                    else {
                        pp.moveTo(tt, val2);
                        penDown = true;
                    }
                }
                else {
                    penDown = false;
                }
            }
        }
        else {
            let penDown = false;
            for (let tt = t1b; tt < t2b; tt++) {
                let val_min = data0[(tt - t1b) * 2];
                let val_max = data0[(tt - t1b) * 2 + 1];
                if ((!isNaN(val_min)) && (!isNaN(val_max))) {
                    let val2_min = (val_min + y_offset) * y_scale_factor;
                    let val2_max = (val_max + y_offset) * y_scale_factor;
                    if (penDown) {
                        pp.lineTo(tt * downsample_factor, val2_min);
                        pp.lineTo(tt * downsample_factor, val2_max);
                    }
                    else {
                        pp.moveTo(tt * downsample_factor, val2_min);
                        pp.lineTo(tt * downsample_factor, val2_max);
                        penDown = true;
                    }
                }
                else {
                    penDown = false;
                }
            }
        }
        if ((selected) && (!this.state.selectElectrodesPrefs.viewOnlySelectedChannels)) {
            painter.setPen({ 'color': 'yellow', width: 6 });
            painter.drawPath(pp);
        }
        // Note that using width=2 here had some bad side-effects on the rendering - and I think it's the browser's fault
        painter.setPen({ 'color': this.channel_colors[m % this.channel_colors.length], width: 1 });
        painter.drawPath(pp);
    }
    _zoomAmplitude = (factor) => {
        this.y_scale_factor *= factor;
        this._repaint();
    }
    _repaint = () => {
        this._repainter && this._repainter();
    }
    _handleSelectedElectrodeIdsChanged = (ids) => {
        this.setState({
            selectedElectrodeIds: ids
        });
    }
    render() {
        let leftPanels = [
            {
                key: 'select-electrodes',
                title: "Select electrodes",
                icon: <SelectElectrodesIcon />,
                render: () => (
                    <SelectElectrodes
                        num_channels={this.props.num_channels}
                        locations={this.props.channel_locations}
                        labels={this.props.channel_ids}
                        selectedElectrodeIds={this.state.selectedElectrodeIds}
                        onChange={this._handleSelectedElectrodeIdsChanged}
                        prefs={this.state.selectElectrodesPrefs}
                        onPrefsChange={(prefs) => {this.setState({selectElectrodesPrefs: prefs})}}
                    />
                )
            }
        ];
        for (let lp of (this.props.leftPanels || [])) {
            leftPanels.push(lp);
        }
        let actions = [
            {
                callback: () => {this._zoomAmplitude(1.15)},
                title: 'Scale amplitude up [up arrow]',
                icon: <FaArrowUp />,
                key: 38
            },
            {
                callback: () => {this._zoomAmplitude(1 / 1.15)},
                title: 'Scale amplitude down [down arrow]',
                icon: <FaArrowDown />,
                key: 40
            },
            {
                type: 'divider'
            }
        ];
        leftPanels.forEach((lp) => {
            actions.push({
                callback: () => {this._toggleLeftPanelMode(lp.key)},
                title: lp.title,
                icon: lp.icon,
                selected: (this.state.leftPanelMode === lp.key)
            })
        });

        let { num_channels, timeseriesModel } = this.props;
        if (!num_channels) {
            return <span>Loading.</span>;
        }
        let leftPanel=undefined;
        for (let lp of leftPanels) {
            if (this.state.leftPanelMode === lp.key) {
                leftPanel = lp.render();
            }
        }
        return (
            <TimeWidget
                panels={this.state.panels}
                actions={actions}
                width={this.props.width}
                height={this.props.height}
                registerRepainter={(repaintFunc) => {this._repainter=repaintFunc}}
                samplerate={timeseriesModel ? timeseriesModel.getSampleRate() : 0}
                maxTimeSpan={1e6 / num_channels}
                numTimepoints={timeseriesModel ? timeseriesModel.numTimepoints() : 0}
                currentTime={this.state.currentTime}
                timeRange={this.state.timeRange}
                onCurrentTimeChanged={this._handleCurrentTimeChanged}
                onTimeRangeChanged={this._handleTimeRangeChanged}
                leftPanel={leftPanel}
            />
        )
    }
}


function determine_downsample_factor_from_num_timepoints(target_num_pix, num) {
    // determine what the downsample factor should be based on the number
    // of timepoints in the view range
    // we also need to consider the number of pixels it corresponds to
    if (target_num_pix < 500) target_num_pix = 500;
    let ds_factor = 1;
    let factor = 3;
    while (num / (ds_factor * factor) > target_num_pix) {
        ds_factor *= factor;
    }
    return ds_factor;
}

function mv_default_channel_colors() {
    var ret = [];
    ret.push('rgb(80,80,80)');
    ret.push('rgb(104,42,42)');
    ret.push('rgb(42,104,42)');
    ret.push('rgb(42,42,152)');
    return ret;
}
