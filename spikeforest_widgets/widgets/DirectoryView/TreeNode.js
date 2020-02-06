import React from 'react';
import { FaFile, FaFolder, FaFolderOpen, FaChevronDown, FaChevronRight, FaBed, FaBullhorn, FaBullseye, FaCircle } from 'react-icons/fa';
import styled from 'styled-components';
import PropTypes from 'prop-types';
// import Sha1PathLink from './Sha1PathLink';
import CopyableText from './CopyableText'
// import { notEqual } from 'assert';

const getPaddingLeft = (level, type) => {
  let paddingLeft = level * 20;
  if (type === 'file') paddingLeft += 20;
  return paddingLeft;
}

const StyledTreeNode = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  // padding: 5px 8px;
  margin-top: 8px;
  margin-bottom: 8px;
  margin-left: ${props => getPaddingLeft(props.level, props.type)}px;
  cursor: pointer;

  &.selected {
    background: #E2E2E2;
  }

  // &:hover {
  //   background: lightgray;
  // }
`;

const NodeIcon = styled.div`
  font-size: 12px;
  margin-right: ${props => props.marginRight ? props.marginRight : 5}px;
`;

const abbreviate = (val, max_chars) => {
  let str0 = '' + val;
  if (str0.length > max_chars) {
    return str0.slice(0, max_chars - 3) + '...';
  }
  else {
    return str0;
  }
}

const objectType = (obj) => {
  if ((obj._attrs) && (obj._attrs.neurodata_type) && (obj._attrs.namespace))
    return 'nwb:' + obj._attrs.namespace + ':' + obj._attrs.neurodata_type;
  return null;
}

const getNodeLabel = (node) => {
  let ret;
  if (node.type === 'value') {
    if (typeof(node.data.value) == 'string') {
      // if ((node.data.value.startsWith('sha1://')) || (node.data.value.startsWith('sha1dir://'))) {
      //   return <span>{`${node.name || '/'}: `}<Sha1PathLink path={node.data.value} canCopy={true} abbreviate={true} /></span>;
      // }
    }
    ret = <span>{`${node.name || '/'}: `}<CopyableText text={node.data.value} abbreviate={30} /></span>;
  }
  else {
    ret = node.name || '/';
  }
  if (node.type === 'object') {
    if (objectType(node.data.object)) {
      ret = `${ret} (${objectType(node.data.object)})`;
    }
  }
  return ret;
}

const TreeNode = (props) => {
  const { node, selectedNodePath, expandedNodePaths, getChildNodes, level, onToggle, onNodeSelect } = props;

  if (!node) {
    return <div>TreeNode: no node</div>;
  }

  let isExpanded = expandedNodePaths[node.path];
  let canExpand = getChildNodes(node).length > 0;

  return (
    <React.Fragment>
      <StyledTreeNode level={level} type={node.type} className={(node.path === selectedNodePath ) ? 'selected' : '' } onClick={() => onNodeSelect(node)}>
        <NodeIcon key={'expanded-icon'} onClick={(e) => {e.stopPropagation(); canExpand && onToggle(node)}}>
          { node.type === 'dir' && (isExpanded ? <FaChevronDown /> : canExpand ? <FaChevronRight /> : <FaBullseye />) }
          { node.type === 'object' && (isExpanded ? <FaChevronDown /> : canExpand ? <FaChevronRight /> : <FaBullseye />) }
          { node.type === 'array-parent' && (isExpanded ? <FaChevronDown /> : canExpand ? <FaChevronRight /> : <FaBullseye />) }
        </NodeIcon>
        
        <NodeIcon key={'item-icon'} marginRight={10}>
          { node.type === 'file' && <FaFile /> }
          {/* { node.type === 'value' && <FaCircle /> } */}
          { node.type === 'value' && <span /> }
          { node.type === 'dir' && isExpanded && <FaFolderOpen /> }
          { node.type === 'dir' && !isExpanded && <FaFolder /> }
          { node.type === 'object' && isExpanded && <FaCircle /> }
          { node.type === 'object' && !isExpanded && <FaCircle /> }
          { node.type === 'array-parent' && isExpanded && <FaBullhorn /> }
          { node.type === 'array-parent' && !isExpanded && <FaBullhorn /> }
        </NodeIcon>
        

        <span key={'label'} role="button" style={{cursor: 'pointer'}}>
          { getNodeLabel(node) }
        </span>
      </StyledTreeNode>

      { isExpanded && getChildNodes(node).map(childNode => (
        <TreeNode 
          {...props}
          key={childNode.path}
          node={childNode}
          level={level + 1}
        />
      ))}
    </React.Fragment>
  );
}

TreeNode.propTypes = {
  node: PropTypes.object.isRequired,
  selectedNodePath: PropTypes.string,
  expandedNodePaths: PropTypes.object.isRequired,
  getChildNodes: PropTypes.func.isRequired,
  level: PropTypes.number.isRequired,
  onToggle: PropTypes.func.isRequired,
  onNodeSelect: PropTypes.func.isRequired,
};

TreeNode.defaultProps = {
  level: 0,
};

export default TreeNode;