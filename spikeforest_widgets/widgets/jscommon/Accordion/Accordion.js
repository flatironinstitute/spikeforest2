import React, { Component } from 'react';
import { Accordion as Accordion2, AccordionItem, AccordionItemHeading, AccordionItemPanel, AccordionItemButton} from 'react-accessible-accordion';
import './AccordionStyle.css';
import AutoDetermineWidth from '../AutoDetermineWidth';

export default class Accordion extends Component {
    constructor(props) {
        super(props);
    }
    componentDidMount() {
    }
    componentDidUpdate() {
    }
    componentWillUnmount() {
    }
    render() {
        return (
            <AutoDetermineWidth>
                <AccordionInner {...this.props} />
            </AutoDetermineWidth>
        )
    }
}

class AccordionInner extends Component {
    constructor(props) {
        super(props);
        this.state={
            indicesSelected: {
            }
        }
    }
    componentDidMount() {
    }
    componentDidUpdate() {
    }
    componentWillUnmount() {
    }
    _handleChange = (expandedList) => {
        let a = this.state.indicesSelected;
        let somethingChanged = false;
        for (let i of expandedList) {
            if (!a[i]) {
                a[i] = true;
                somethingChanged = true;
            }
        }
        if (somethingChanged) {
            this.setState({
                indicesSelected: a
            });
        }
    }
    render() {
        let { panels } = this.props;
        return (
            <Accordion2
                allowMultipleExpanded={this.props.allowMultipleExpanded}
                allowZeroExpanded={true}
                preExpanded={[]}
                onChange={(expandedList) => {this._handleChange(expandedList)}}
                onSelect={(index, lastIndex, event) => {this._handleSelect(index);}}
            >
                {this.props.children.map((Child, i) => {
                    return (
                        <AccordionItem key={panels[i].label} uuid={i}>
                            <AccordionItemHeading>
                                <AccordionItemButton>
                                    {panels[i].label}
                                </AccordionItemButton>
                            </AccordionItemHeading>
                            <AccordionItemPanel>
                                {
                                    this.state.indicesSelected[i] ? <Child.type width={this.props.width - 40 /* because padding is 20 */ } {...Child.props} /> : <span>Waiting</span>
                                }
                            </AccordionItemPanel>
                        </AccordionItem>
                    );
                })}
            </Accordion2>
        )
    }
}