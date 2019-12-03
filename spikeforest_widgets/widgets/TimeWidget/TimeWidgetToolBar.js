import React, { Component } from 'react';

import { Toolbar, IconButton } from '@material-ui/core';
import { FaSearchMinus, FaSearchPlus, FaArrowUp, FaArrowDown, FaArrowLeft, FaArrowRight } from "react-icons/fa";

export default class TimeWidgetToolBar extends Component {
    render() {
        const style0 = {
            position: 'relative',
            width: this.props.width,
            height: this.props.height,
            top: this.props.top,
            overflow: 'hidden'
        };
        let buttons = [];
        buttons.push({
            type: 'button',
            title: "Time zoom in (+)",
            onClick: this.props.onZoomIn,
            icon: <FaSearchPlus />
        });
        buttons.push({
            type: 'button',
            title: "Time zoom out (-)",
            onClick: this.props.onZoomOut,
            icon: <FaSearchMinus />
        });
        buttons.push({
            type: 'button',
            title: "Shift time left [left arrow]",
            onClick: this.props.onShiftTimeLeft,
            icon: <FaArrowLeft />
        });
        buttons.push({
            type: 'button',
            title: "Shift time right [right arrow]",
            onClick: this.props.onShiftTimeRight,
            icon: <FaArrowRight />
        });
        buttons.push({
            type: 'divider'
        });
        for (let a of this.props.customActions) {
            buttons.push({
                type: a.type || 'button',
                title: a.title,
                onClick: a.callback,
                icon: a.icon,
                selected: a.selected
            });
        }
        return (
            <div style={style0}>
                {
                    buttons.map((button, ii) => {
                        if (button.type === 'button') {
                            let color = 'inherit';
                            if (button.selected) color = 'primary';
                            return (
                                <IconButton title={button.title} onClick={button.onClick} key={ii} color={color}>
                                    {button.icon}
                                </IconButton>
                            );
                        }
                        else if (button.type === 'divider') {
                            return <hr key={ii} />;
                        }
                    })
                }
            </div>
        );
    }
}