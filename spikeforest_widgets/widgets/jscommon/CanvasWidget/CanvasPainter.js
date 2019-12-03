export function CanvasPainter(context2d, canvasLayer) {
    var that = this;
    var ctx = context2d;

    var m_pen = { color: 'black' };
    var m_font = { "pixel-size": 12, family: 'Arial' };
    var m_brush = { color: 'black' };
    let m_use_coords = false;
    let m_exporting_figure = false;

    this.pen = function () { return shallowClone(m_pen); };
    this.setPen = function (pen) { setPen(pen); };
    this.font = function () { return shallowClone(m_font); };
    this.setFont = function (font) { setFont(font); };
    this.brush = function () { return shallowClone(m_brush); };
    this.setBrush = function (brush) { setBrush(brush); };
    this.useCoords = function() { m_use_coords = true; };
    this.usePixels = function() { m_use_coords = false; };
    this.newPainterPath = function() { return new PainterPath(); };

    this.setExportingFigure = function(val) { m_exporting_figure = val; };
    this.exportingFigure = function() { return m_exporting_figure; }; 

    this._initialize = function (W, H) {
        //ctx.fillStyle='black';
        //ctx.fillRect(0,0,W,H);
        // m_width = W;
        // m_height = H;
    };
    this._finalize = function () {
    };
    this.clear = function() {
        return _clearRect(0, 0, canvasLayer.width(), canvasLayer.height());
    }
    this.clearRect = function (x, y, W, H) {
        this.fillRect(x, y, W, H, {color: 'transparent'});
        return;

        if (typeof(x) === 'object') {
            let a = x;
            x = a[0];
            y = a[1];
            W = a[2];
            H = a[3];
        }
        let a = transformXYWH(x, y, W, H);
        return _clearRect(a[0], a[1], a[2], a[3]);
    };
    function _clearRect(x, y, W, H) {
        ctx.clearRect(x, y, W, H);
    }

    this.fillRect = function (x, y, W, H, brush) {
        if (typeof(x) === 'object') {
            let a = x;
            brush = y;
            x = a[0];
            y = a[1];
            W = a[2];
            H = a[3];
        }
        let a = transformXYWH(x, y, W, H);
        return _fillRect(a[0], a[1], a[2], a[3], brush);
    }
    function _fillRect(x, y, W, H, brush) {
        if (typeof(x) === 'object') {
            let rect2 = x;
            let brush2 = y;
            that.fillRect(rect2[0], rect2[1], rect2[2], rect2[3], brush2);
            return;
        }
        if (typeof brush === 'string') brush = { color: brush };
        if (!('color' in brush)) brush = { color: brush };
        ctx.fillStyle = to_color(brush.color);
        ctx.fillRect(x, y, W, H);
    };

    this.drawRect = function (x, y, W, H) {
        if (typeof(x) === 'object') {
            let a = x;
            x = a[0];
            y = a[1];
            W = a[2];
            H = a[3];
        }
        let a = transformXYWH(x, y, W, H);
        return _drawRect(a[0], a[1], a[2], a[3]);
    }
    function _drawRect(x, y, W, H) {
        apply_pen(ctx, m_pen);
        ctx.strokeRect(x, y, W, H);
    };

    this.drawPath = function (painter_path) {
        apply_pen(ctx, m_pen);
        painter_path._draw(ctx, transformXY);
    };
    this.drawLine = function (x1, y1, x2, y2) {
        var ppath = new PainterPath();
        ppath.moveTo(x1, y1);
        ppath.lineTo(x2, y2);
        that.drawPath(ppath);
    };
    this.drawText = function (rect, alignment, txt) {
        let rect2 = transformRect(rect);
        return _drawText(rect2, alignment, txt);
    }
    function _drawText(rect, alignment, txt) {
        var x, y, textAlign, textBaseline;
        if (alignment.AlignLeft) {
            x = rect[0];
            textAlign = 'left';
        }
        else if (alignment.AlignCenter) {
            x = rect[0] + rect[2] / 2;
            textAlign = 'center';
        }
        else if (alignment.AlignRight) {
            x = rect[0] + rect[2];
            textAlign = 'right';
        }
        else {
            console.error('Missing horizontal alignment in drawText');
        }

        if (alignment.AlignTop) {
            y = rect[1];
            textBaseline = 'top';
        }
        else if (alignment.AlignBottom) {
            y = rect[1] + rect[3];
            textBaseline = 'bottom';
        }
        else if (alignment.AlignVCenter) {
            y = rect[1] + rect[3] / 2;
            textBaseline = 'middle';
        }
        else {
            console.error('Missing vertical alignment in drawText');
        }

        ctx.font = m_font['pixel-size'] + 'px ' + m_font.family;
        ctx.textAlign = textAlign;
        ctx.textBaseline = textBaseline;
        apply_pen(ctx, m_pen);
        ctx.fillStyle = to_color(m_brush.color);
        ctx.fillText(txt, x, y);
    }
    this.drawMarker = function(x, y, radius, shape, opts) {
        opts = opts || {};
        let pt = transformXY(x, y);
        _drawMarker(pt[0], pt[1], radius, shape, opts);
    }
    function _drawMarker(x, y, radius, shape, opts) {
        shape = shape || 'circle';
        let rect = [x-radius, y-radius, 2*radius, 2*radius];
        if (shape == 'circle') {
            if (opts.fill) {
                _fillEllipse(rect);
            }
            else {
                _drawEllipse(rect);
            }
        }
        else {
            console.error(`Unrecognized marker shape ${shape}`);
        }
    }
    this.fillMarker = function(x, y, radius, shape) {
        let pt = transformXY(x, y);
        _drawMarker(pt[0], pt[1], radius, shape, {fill: true});
    }
    this.drawEllipse = function (rect) {
        let rect2 = transformRect(rect);
        return _drawEllipse(rect2);
    }
    function _drawEllipse(rect) {
        apply_pen(ctx, m_pen);
        ctx.beginPath();
        ctx.ellipse(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2, rect[2] / 2, rect[3] / 2, 0, 0, 2 * Math.PI);
        ctx.stroke();
    }
    this.fillEllipse = function (rect, brush) {
        let rect2 = transformRect(rect);
        return _fillEllipse(rect2, brush);
    }
    function _fillEllipse(rect, brush) {
        if (brush) {
            if (typeof brush === 'string') brush = { color: brush };
            if (!('color' in brush)) brush = { color: brush };
            ctx.fillStyle = to_color(brush.color);
        }
        else {
            ctx.fillStyle = to_color(m_brush.color);
        }
        ctx.beginPath();
        ctx.ellipse(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2, rect[2] / 2, rect[3] / 2, 0, 0, 2 * Math.PI);
        ctx.fill();
    }

    function setPen(pen) {
        m_pen = shallowClone(pen);
    }

    function setFont(font) {
        m_font = shallowClone(font);
    }

    function setBrush(brush) {
        m_brush = shallowClone(brush);
    }

    function to_color(col) {
        if (typeof col === 'string') return col;
        return 'rgb(' + Math.floor(col[0]) + ',' + Math.floor(col[1]) + ',' + Math.floor(col[2]) + ')';
    }

    function apply_pen(context, pen) {
        if ('color' in pen)
            context.strokeStyle = to_color(pen.color);
        else
            context.strokeStyle = 'black';
        if ('width' in pen)
            context.lineWidth = pen.width;
        else
            context.lineWidth = 1;
    }

    function transformRect(rect) {
        return transformXYWH(rect[0], rect[1], rect[2], rect[3]);
    }
    function transformXYWH(x, y, W, H) {
        let pt1 = transformXY(x, y);
        let pt2 = transformXY(x + W, y + H);
        return [Math.min(pt1[0], pt2[0]), Math.min(pt1[1], pt2[1]), Math.abs(pt2[0] - pt1[0]), Math.abs(pt2[1] - pt1[1])];
    }
    function transformXY(x, y) {
        const margins = canvasLayer.margins();
        if (m_use_coords) {
            const xr = canvasLayer.coordXRange();
            const yr = canvasLayer.coordYRange();
            let W = canvasLayer.width() - margins[0] - margins[1];
            let H = canvasLayer.height() - margins[2] - margins[3];
            // const xextent = xr[1] - xr[0];
            // const yextent = yr[1] - yr[0];
            // if (canvasLayer.preserveAspectRatio()) {
            //     if ((W * yextent > H * xextent) && (yextent)) {
            //         W = H * xextent / yextent;
            //     }
            //     else if ((H * xextent > W * yextent) && (xextent)) {
            //         H = W * yextent / xextent;
            //     }
            // }
            const xpct = (x - xr[0]) / (xr[1] - xr[0]);
            const ypct = 1 - (y - yr[0]) / (yr[1] - yr[0]);
            return [margins[0] + W * xpct, margins[2] + H * ypct];
        }
        else {
            return [margins[0] + x, margins[2] + y];
        }
    }
}

export function PainterPath() {
    this.moveTo = function (x, y) { moveTo(x, y); };
    this.lineTo = function (x, y) { lineTo(x, y); };

    this._draw = function (ctx, transformXY) {
        ctx.beginPath();
        for (var i = 0; i < m_actions.length; i++) {
            apply_action(ctx, m_actions[i], transformXY);
        }
        ctx.stroke();
    }
    var m_actions = [];

    function moveTo(x, y) {
        if (y === undefined) { moveTo(x[0], x[1]); return; }
        m_actions.push({
            name: 'moveTo',
            x: x, y: y
        });
    }
    function lineTo(x, y) {
        if (m_actions.length === 0) {
            moveTo(x, y);
            return;
        }
        if (y === undefined) { lineTo(x[0], x[1]); return; }
        m_actions.push({
            name: 'lineTo',
            x: x, y: y
        });
    }

    function apply_action(ctx, a, transformXY) {
        let pos;
        if (transformXY) {
            pos = transformXY(a.x, a.y);
        }
        else {
            pos = [a.x, a.y];
        }
        if (a.name === 'moveTo') {
            ctx.moveTo(pos[0], pos[1]);
        }
        else if (a.name === 'lineTo') {
            ctx.lineTo(pos[0], pos[1]);
        }
    }
}

export function MouseHandler() {
    this.setElement = function (elmt) { m_element = elmt; };
    this.onMousePress = function (handler) { m_handlers['press'].push(handler); };
    this.onMouseRelease = function (handler) { m_handlers['release'].push(handler); };
    this.onMouseMove = function (handler) { m_handlers['move'].push(handler); };
    this.onMouseEnter = function (handler) { m_handlers['enter'].push(handler); };
    this.onMouseLeave = function (handler) { m_handlers['leave'].push(handler); };
    this.onMouseWheel = function (handler) { m_handlers['wheel'].push(handler); };
    this.onMouseDrag = function (handler) { m_handlers['drag'].push(handler); };
    this.onMouseDragRelease = function (handler) { m_handlers['drag_release'].push(handler); };

    this.mouseDown = function (e) { report('press', mouse_event(e)); return true; };
    this.mouseUp = function (e) { report('release', mouse_event(e)); return true; };
    this.mouseMove = function (e) { report('move', mouse_event(e)); return true; };
    this.mouseEnter = function (e) { report('enter', mouse_event(e)); return true; };
    this.mouseLeave = function (e) { report('leave', mouse_event(e)); return true; };
    this.mouseWheel = function (e) { report('wheel', wheel_event(e)); return true; };
    // elmt.on('dragstart',function() {return false;});
    // elmt.on('mousewheel', function(e){report('wheel',wheel_event($(this),e)); return false;});

    let m_element = null;
    let m_handlers = {
        press: [], release: [], move: [], enter: [], leave: [], wheel: [], drag: [], drag_release: []
    };
    let m_dragging = false;
    let m_drag_anchor = null;
    let m_drag_pos = null;
    let m_drag_rect = null;
    let m_last_report_drag = new Date();
    let m_scheduled_report_drag_X = null;

    function report(name, X) {
        if (name == 'drag') {
            let elapsed = (new Date()) - m_last_report_drag;
            if (elapsed < 50) {
                schedule_report_drag(X, 50 - elapsed + 10);
                return;
            }
            m_last_report_drag = new Date();
        }
        for (let i in m_handlers[name]) {
            m_handlers[name][i](X);
        }
        drag_functionality(name, X);
    }

    function schedule_report_drag(X, timeout) {
        if (m_scheduled_report_drag_X) {
            m_scheduled_report_drag_X = X;
            return;
        }
        else {
            m_scheduled_report_drag_X = X;
            setTimeout(() => {
                let X2 = m_scheduled_report_drag_X;
                m_scheduled_report_drag_X = null;
                report('drag', X2);
            }, timeout)
        }
        
    }

    function drag_functionality(name, X) {
        if (name == 'press') {
            m_dragging = false;
            m_drag_anchor = cloneSimpleArray(X.pos);
            m_drag_pos = null;
        }
        else if (name == 'release') {
            if (m_dragging) {
                report('drag_release', { anchor: cloneSimpleArray(m_drag_anchor), pos: cloneSimpleArray(m_drag_pos), rect: cloneSimpleArray(m_drag_rect) });
            }
            m_dragging = false;
        }
        if ((name === 'move') && (X.buttons === 1)) {
            // move with left button
            if (m_dragging) {
                m_drag_pos = cloneSimpleArray(X.pos);
            }
            else {
                if (!m_drag_anchor) {
                    m_drag_anchor = cloneSimpleArray(X.pos);
                }
                const tol = 4;
                if ((Math.abs(X.pos[0] - m_drag_anchor[0]) > tol) || (Math.abs(X.pos[1] - m_drag_anchor[1]) > tol)) {
                    m_dragging = true;
                    m_drag_pos = cloneSimpleArray(X.pos);
                }
            }
            if (m_dragging) {
                m_drag_rect = [Math.min(m_drag_anchor[0], m_drag_pos[0]), Math.min(m_drag_anchor[1], m_drag_pos[1]), Math.abs(m_drag_pos[0] - m_drag_anchor[0]), Math.abs(m_drag_pos[1] - m_drag_anchor[1])];
                report('drag', { anchor: cloneSimpleArray(m_drag_anchor), pos: cloneSimpleArray(m_drag_pos), rect: cloneSimpleArray(m_drag_rect) });
            }
        }
    }

    function mouse_event(e) {
        if (!m_element) return {};
        //var parentOffset = $(this).parent().offset(); 
        //var offset=m_element.offset(); //if you really just want the current element's offset
        var rect = m_element.getBoundingClientRect();
        window.m_element = m_element;
        window.dbg_m_element = m_element;
        window.dbg_e = e;
        var posx = e.clientX - rect.x;
        var posy = e.clientY - rect.y;
        return {
            pos: [posx, posy],
            modifiers: { ctrlKey: e.ctrlKey, shiftKey: e.shiftKey },
            buttons: e.buttons
        };
    }
    function wheel_event(e) {
        return {
            delta: e.originalEvent.wheelDelta
        };
    }
}

function clone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

function shallowClone(obj) {
    return Object.assign({}, obj);
}

function cloneSimpleArray(x) {
    return x.slice(0);
}

