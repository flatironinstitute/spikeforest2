import React, { Component } from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell, Link } from '@material-ui/core';

export default class StudySets extends Component {
    constructor(props) {
        super(props);
    }
    componentDidMount() {
    }
    componentWillUnmount() {
    }
    _createStudySetLink = (studySet) => {
        return (
            <Link2 onClick={() => {this.props.onOpenStudySet && this.props.onOpenStudySet(studySet)}}>
                <b>{studySet.name}</b>
            </Link2>
        );
    }
    _createStudyLink = (study) => {
        return (
            <Link2 onClick={() => {this.props.onOpenStudy && this.props.onOpenStudy(study)}}>
                {study.name}
            </Link2>
        );
    }
    render() {
        const object = this.props.object || [];
        console.log(object);
        return (
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Num. recordings</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {
                        object.map((studySet) => {
                            return (
                                <React.Fragment>
                                    <TableRow key={studySet.name}>
                                        <TableCell>
                                            {
                                                this._createStudySetLink(studySet)
                                            }
                                        </TableCell>
                                    </TableRow>
                                    {
                                        studySet.studies.map((study) => {
                                            return (
                                                <TableRow key={'study-' + study.name}>
                                                    <TableCell>
                                                        &nbsp;&nbsp;{this._createStudyLink(study)}
                                                    </TableCell>
                                                    <TableCell>
                                                        {study.recordings.length}
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })
                                    }
                                </React.Fragment>
                            );
                        })
                    }
                </TableBody>
            </Table>
        )
    }
}

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