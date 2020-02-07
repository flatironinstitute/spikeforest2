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

class CopyableText extends Component {
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
            let style0 = {
                width: 300
            };
            link0 = <input type={"text"} value={this.props.text} readOnly={true} onFocus={e => e.target.select()} onBlur={this.handleUnclick} autoFocus={true} style={style0} />;
        }
        else {
            let text = this.props.text;
            if (this.props.abbreviate) {
                text = abbreviate(text, this.props.abbreviate);
            }

            link0 = (
                <span title={`Click to copy text`}>
                    <Link2 onClick={this.handleClick}>{text}</Link2>
                </span>
            );
        }
        return link0;
    }
}

const abbreviate = (val, max_chars) => {
    let str0 = '' + val;
    if (str0.length > max_chars) {
      return str0.slice(0, max_chars - 3) + '...';
    }
    else {
      return str0;
    }
  }

export default CopyableText;
