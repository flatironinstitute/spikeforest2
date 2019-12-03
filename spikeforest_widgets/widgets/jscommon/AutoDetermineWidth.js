import React, { Component } from 'react';
import { maxHeight } from '@material-ui/system';

export default class AutoDetermineWidth extends Component {
    constructor(props) {
        super(props);
        this.state = {
            width: null
        };
        this._polling = true;
    }

    async componentDidMount() {
        this.updateDimensions();
        // window.addEventListener("resize", this.resetWidth);
        this._nextPoll();
    }

    componentWillUnmount() {
        // window.removeEventListener("resize", this.resetWidth);
        this._polling = false;
    }

    _nextPoll = () => {
        if (!this._polling) return;
        setTimeout(() => {this._nextPoll()}, 1000);
        this.updateDimensions();
    }

    resetWidth = () => {
        if (this.state.width) {
            this.setState({
                width: null
            });
        }
    }

    async componentDidUpdate(prevProps, prevState) {
        if (!this.state.width) {
            this.updateDimensions();
        }
    }

    updateDimensions() {
        if ((this.container) && (this.container.offsetWidth)) {
            let newWidth = this.container.offsetWidth - 2; // Subtract 2 because of jupyterlab (in the future only do this for jupyterlab)
            if (this.state.width !== newWidth) {
                this.setState({
                    width: newWidth // see render()
                });
                if (!this.container.sensor) {
                    //this.container.sensor = new ResizeSensor(this.container, () => {this.updateDimensions();});
                    /*
                    // The following was causing problems in Accordion view on Jupyter Lab
                    this.container.sensor = new ResizeObserver(() => {
                        this.updateDimensions()
                    }).observe(this.container);
                    */
                }
            }
        }
    }

    render() {
        const elmt = React.Children.only(this.props.children)
        if (this.props.width) {
            let new_props = {};
            for (let key in elmt.props) {
                new_props[key] = elmt.props[key];
            }
            new_props.width = this.props.width;
            return <elmt.type {...new_props}  />;
        }
        else if (elmt.props.width) {
            return elmt;
        }
        else {
            let width = this.state.width || undefined;
            if (!width) width = 0;

            let new_props = {};
            for (let key in elmt.props) {
                new_props[key] = elmt.props[key];
            }
            new_props.width = width;

            let style_for_jupyterlab = {maxWidth: width, overflow: 'hidden'};

            return (
                <div>
                    <div
                        className="determiningWidth2"
                        ref={el => (this.container = el)}
                        style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 0 }}
                    />
                    <elmt.type {...new_props} style={style_for_jupyterlab}  />
                </div>
            );
        }
    }
}

function ResizeSensor(element, callback)
{
    let zIndex = parseInt(getComputedStyle(element));
    if(isNaN(zIndex)) { zIndex = 0; };
    zIndex--;

    let expand = document.createElement('div');
    expand.style.position = "absolute";
    expand.style.left = "0px";
    expand.style.top = "0px";
    expand.style.right = "0px";
    expand.style.bottom = "0px";
    expand.style.overflow = "hidden";
    expand.style.zIndex = zIndex;
    expand.style.visibility = "hidden";

    let expandChild = document.createElement('div');
    expandChild.style.position = "absolute";
    expandChild.style.left = "0px";
    expandChild.style.top = "0px";
    expandChild.style.width = "10000000px";
    expandChild.style.height = "10000000px";
    expand.appendChild(expandChild);

    let shrink = document.createElement('div');
    shrink.style.position = "absolute";
    shrink.style.left = "0px";
    shrink.style.top = "0px";
    shrink.style.right = "0px";
    shrink.style.bottom = "0px";
    shrink.style.overflow = "hidden";
    shrink.style.zIndex = zIndex;
    shrink.style.visibility = "hidden";

    let shrinkChild = document.createElement('div');
    shrinkChild.style.position = "absolute";
    shrinkChild.style.left = "0px";
    shrinkChild.style.top = "0px";
    shrinkChild.style.width = "200%";
    shrinkChild.style.height = "200%";
    shrink.appendChild(shrinkChild);

    element.appendChild(expand);
    element.appendChild(shrink);

    function setScroll()
    {
        expand.scrollLeft = 10000000;
        expand.scrollTop = 10000000;

        shrink.scrollLeft = 10000000;
        shrink.scrollTop = 10000000;
    };
    setScroll();

    let size = element.getBoundingClientRect();

    let currentWidth = size.width;
    let currentHeight = size.height;

    let onScroll = function()
    {
        let size = element.getBoundingClientRect();

        let newWidth = size.width;
        let newHeight = size.height;

        if(newWidth != currentWidth || newHeight != currentHeight)
        {
            currentWidth = newWidth;
            currentHeight = newHeight;

            callback();
        }

        setScroll();
    };

    expand.addEventListener('scroll', onScroll);
    shrink.addEventListener('scroll', onScroll);
};