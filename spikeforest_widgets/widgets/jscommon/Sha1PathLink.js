import React, { Component } from "react";
import { Link } from "@material-ui/core";

function Link2(props) {
    return (
        <Link
            component="button" variant="body2"
            onClick={props.onClick}
        >
            {props.children}
        </Link>
    )
}

class Sha1PathLink extends Component {
    constructor(props) {
        super(props);
        this.state = {
            clicked: false
        };
    }

    componentDidMount() {
    }

    handleClick = () => {
        this.setState({ clicked: true });
    }

    handleUnclick = () => {
        this.setState({ clicked: false });
    }

    render() {
        let link0 = <span></span>;
        if (this.state.clicked) {
            if (this.props.canCopy) {
                let style0 = {
                    width: this.props.abbreviate ? 300 : 600
                };
                link0 = <input type={"text"} value={this.props.path} readOnly={true} onFocus={e => e.target.select()} onBlur={this.handleUnclick} autoFocus={true} style={style0} />;
            }
            else {
                link0 = <span>{this.props.path}</span>
            }
        }
        else {
            let text = this.props.label || this.props.path;
            if (this.props.abbreviate) {
                let list0 = this.props.path.split('/');
                text = `${list0[0]}//${(list0[2]||'').slice(0,8)}.../${list0[list0.length - 1]}`;
            }

            if (this.props.canCopy) {
                link0 = (
                    <span title={`Click for more options for ${this.props.path}`}>
                        <Link2 onClick={this.handleClick}>{text}</Link2>
                    </span>
                );
            }
            else {
                link0 = <span title={`${this.props.path}`}>{text}</span>
            }
        }
        return link0;
    }
}

export default Sha1PathLink;
