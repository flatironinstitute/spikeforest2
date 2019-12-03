function Mda(arg1,arg2,arg3,arg4,arg5) {
	var that=this;
	this.allocate=function(n1,n2,n3,n4,n5) {return _allocate(n1,n2,n3,n4,n5);};
	this.N1=function() {return _N1();};
	this.N2=function() {return _N2();};
	this.N3=function() {return _N3();};
	this.N4=function() {return _N4();};
	this.N5=function() {return _N5();};
	this.totalSize=function() {return _totalSize();};
	this.value=function(i1,i2,i3,i4,i5) {return _value(i1,i2,i3,i4,i5);};
	this.setValue=function(val,i1,i2,i3,i4,i5) {return _setValue(val,i1,i2,i3,i4,i5);};
	this.data=function() {return _data();};
	this.dataCopy=function() {return _dataCopy();};
	this.setData=function(data) {return _setData(data);};
	this.clone=function() {return _clone();};
	this.reshape=function(n1,n2,n3,n4,n5) {return _reshape(n1,n2,n3,n4,n5);};
	this.getChunk=function(i,size) {return _getChunk(i,size);};
	this.subArray=function(arg1,arg2,arg3,arg4,arg5,arg6) {return _subArray(arg1,arg2,arg3,arg4,arg5,arg6);};
	this.load=function(url,callback) {return _load(url,callback);};
	this.setFromArrayBuffer=function(buf) {return _setFromArrayBuffer(buf);};
	this.setFromBase64=function(x) {return _setFromBase64(x);};
	this.minimum=function() {return _minimum();};
	this.maximum=function() {return _maximum();};
	this.toList=function() {return _toList();};
	
	function _allocate(n1,n2,n3,n4,n5) {
		n1=n1||1; n2=n2||1; n3=n3||1;
		n4=n4||1; n5=n5||1;
		m_total_size=n1*n2*n3*n4*n5;
		m_dims[0]=n1; m_dims[1]=n2; m_dims[2]=n3; m_dims[3]=n4; m_dims[4]=n5;
		m_data=new Float32Array(m_total_size);
		for (var i=0; i<m_total_size; i++) m_data[i]=0;
	};
	function _N1() {return m_dims[0];};
	function _N2() {return m_dims[1];};
	function _N3() {return m_dims[2];};
	function _N4() {return m_dims[3];};
	function _N5() {return m_dims[4];};
	function _totalSize() {return m_total_size;};
	function _value(i1,i2,i3,i4,i5) {
		if (i2===undefined) {
			return m_data[i1];
		}
		else if (i3===undefined) {
			return that.value(i1+m_dims[0]*i2);
		}
		else if (i4===undefined) {
			return that.value(i1+m_dims[0]*i2+m_dims[0]*m_dims[1]*i3);
		}
		else if (i5===undefined) {
			return that.value(i1+m_dims[0]*i2+m_dims[0]*m_dims[1]*i3+m_dims[0]*m_dims[1]*m_dims[2]*i4);
		}
		else {
			return that.value(i1 +m_dims[0]*i2 +m_dims[0]*m_dims[1]*i3 +m_dims[0]*m_dims[1]*m_dims[2]*i4 +m_dims[0]*m_dims[1]*m_dims[2]*m_dims[3]*i5);
		}
	};
	function _setValue(val,i1,i2,i3,i4,i5) {
		if (i2===undefined) {
			m_data[i1]=val;
		}
		else if (i3===undefined) {
			that.setValue(val,i1+m_dims[0]*i2);
		}
		else if (i4===undefined) {
			that.setValue(val,i1+m_dims[0]*i2+m_dims[0]*m_dims[1]*i3);
		}
		else if (i5===undefined) {
			that.setValue(val,i1+m_dims[0]*i2+m_dims[0]*m_dims[1]*i3+m_dims[0]*m_dims[1]*m_dims[2]*i4);
		}
		else {
			that.setValue(val,i1 +m_dims[0]*i2 +m_dims[0]*m_dims[1]*i3 +m_dims[0]*m_dims[1]*m_dims[2]*i4 +m_dims[0]*m_dims[1]*m_dims[2]*m_dims[3]*i5);
		}
	};
	function _data() {return m_data;};
	function _dataCopy() {
		var ret=new Float32Array(m_total_size);
		for (var i=0; i<m_total_size.length; i++) {
			ret[i]=m_data[i];
		}
		return ret;
	};
	function _setData(data) {
		m_data=data;
	};
	function _clone() {
		var ret=new Mda();
		ret.allocate(that.N1(),that.N2(),that.N3(),that.N4(),that.N5());
		ret.setData(that.dataCopy());
		return ret;
	};
	function _toList() {
		let A = [];
		for (let a of m_data)
			A.push(a);
		return A;
	}
	function _reshape(n1,n2,n3,n4,n5) {
		n2=n2||1; n3=n3||1; n4=n4||1; n5=n5||1;
		var tot=n1*n2*n3*n4*n5;
		if (tot!=m_total_size) {
			console.error('Unable to reshape... incompatible size: '+n1+'x'+n2+'x'+n3+'x'+n4+'x'+n5+'    '+that.N1()+'x'+that.N2()+'x'+that.N3()+'x'+that.N4()+'x'+that.N5());
			return;
		}
		m_dims[0]=n1; m_dims[1]=n2; m_dims[2]=n3; m_dims[3]=n4; m_dims[4]=n5;		
	};
	function _getChunk(i,size) {
		var ret=new Mda();
		ret.allocate(size,1);
		ret.setData(m_data.subarray(i,i+size));
		return ret;
	};
	function _subArray(arg1,arg2,arg3,arg4,arg5,arg6) {
		if (arg3===undefined) {
			return that.getChunk(arg1,arg2);
		}
		else if (arg5===undefined) {
			if ((arg3!=that.N1())||(arg1!==0)) {
				console.error('This case not supported yet: subArray.');
				return null;
			}
			var iii=arg2*that.N1();
			var sss=arg4*that.N1();
			var ret=that.getChunk(iii,sss);
			ret.reshape(arg3,arg4);
			return ret;
		}
		else {
			if ((arg4!=that.N1())||(arg1!==0)) {
				console.error('This case not supported yet: subArray.');
				return null;
			}
			if ((arg5!=that.N2())||(arg2!==0)) {
				console.error('This case not supported yet: subArray.');
				return null;
			}
			var iii=arg3*that.N1()*that.N2();
			var sss=arg6*that.N1()*that.N2();
			var ret=that.getChunk(iii,sss);
			ret.reshape(arg4,arg5,arg6);
			return ret;
		}
	};
	function _load(url,callback) {
		if (!(url in s_mda_binary_loaders)) {
			s_mda_binary_loaders[url]=new MdaBinaryLoader(url);
		}

		s_mda_binary_loaders[url].load(function(ret) {
			that.allocate(ret.mda.N1(),ret.mda.N2(),ret.mda.N3());
			that.setData(ret.mda.data());
			callback({success:true});
			/*
			if (ret.data.length>0) {
				var dims=ret.dims;
				that.allocate(dims[0],dims[1]||1,dims[2]||1,dims[3]||1,dims[4]||1);
				m_data=ret.data;
				callback({success:true});
			}
			else {
				callback({success:false});
			}
			*/
		});
	};
	function _setFromBase64(x) {
		_setFromArrayBuffer(_base64ToArrayBuffer(x));
	}
	function _setFromArrayBuffer(buf) {
		var X=new Int32Array(buf.slice(0,64));
		var num_bytes_per_entry=X[1];
		var num_dims=X[2];
		m_dims=[];
		if ((num_dims<1)||(num_dims>5)) {
			console.error('Invalid number of dimensions: '+num_dims);
			return false;
		} 
		for (var i=0; i<num_dims; i++) {
			m_dims.push(X[3+i]);
		}
		var dtype=get_dtype_string(X[0]);
		var header_size=(num_dims+3)*4;
		if (dtype=='float32') {
			m_data=new Float32Array(buf.slice(header_size));
			return true;
		}
		else if (dtype=='float64') {
			m_data=new Float64Array(buf.slice(header_size));
			return true;	
		}
		else if (dtype=='int16') {
			m_data=new Int16Array(buf.slice(header_size));
			return true;	
		}
		else {
			console.error('Unsupported dtype: '+dtype);
			m_data=[];
			return false;
		}
	}
	function _minimum() {
		if (m_data.length===0) return 0;
		var ret=m_data[0];
		for (var i=0; i<m_data.length; i++) {
			if (m_data[i]<ret) ret=m_data[i];
		}
		return ret;
	};
	function _maximum() {
		if (m_data.length===0) return 0;
		var ret=m_data[0];
		for (var i=0; i<m_data.length; i++) {
			if (m_data[i]>ret) ret=m_data[i];
		}
		return ret;
	};
	function get_dtype_string(num) {
		if (num==-2) return 'byte';
		if (num==-3) return 'float32';
		if (num==-4) return 'int16';
		if (num==-5) return 'int32';
		if (num==-6) return 'uint16';
		if (num==-7) return 'float64';
		return '';
	}
	
	var m_data=new Float32Array(1);
	var m_dims=[1,1,1,1,1];
	var m_total_size=1;

	that.allocate(arg1||1,arg2||1,arg3||1,arg4||1,arg5||1);
}

var s_mda_binary_loaders={};
function MdaBinaryLoader(url) {
	this.load=function(callback) {
		if (m_done_loading) {
			callback(m_data.slice());
			return;
		}
		JSQ.connect(m_signaler,'loaded',0,function() {
			callback({mda:m_mda});	
		});
		if (!m_is_loading) {
			m_is_loading=true;
			start_loading();
		}
	}

	var m_signaler=new JSQObject();
	var m_is_loading=false;
	var m_done_loading=false;
	var m_mda=new Mda();

	function start_loading() {
		$.ajax({
			url: url,
			type: "GET",
			dataType: "binary",
			processData: false,
			responseType: 'arraybuffer',
			error: function(jqXHR, textStatus, errorThrown) {
				console.log (url);
				console.error('Error: '+textStatus+': '+errorThrown);
			},
			success: function(result) {
				if (result.byteLength<64) {
					console.error('Downloaded file is too small: '+result.byteLength);
					m_data=[];
					m_signaler.emit('loaded');
					return;
				}
				if (m_mda.setFromArrayBuffer(result)) {
					m_signaler.emit('loaded');
				}
				else {
					m_signaler.emit('loaded');
				}
				/*
				var X=new Int32Array(result.slice(0,64));
				var num_bytes_per_entry=X[1];
				var num_dims=X[2];
				m_dims=[];
				if ((num_dims<2)||(num_dims>5)) {
					console.error('Invalid number of dimensions: '+num_dims);
					m_data=[];
					m_signaler.emit('loaded');
					return;
				} 
				for (var i=0; i<num_dims; i++) {
					m_dims.push(X[3+i]);
				}
				var dtype=get_dtype_string(X[0]);
				var header_size=(num_dims+3)*4;
				if (dtype=='float32') {
					m_data=new Float32Array(result.slice(header_size));
					m_signaler.emit('loaded');
					return;
				}
				else if (dtype=='float64') {
					m_data=new Float64Array(result.slice(header_size));
					m_signaler.emit('loaded');
					return;	
				}
				else {
					callback({success:false,error:'Unsupported data type: '+dtype});
					console.error('Unsupported dtype: '+dtype);
					m_data=[];
					m_signaler.emit('loaded');
					return;
				}
				*/
			}
		});
	}
}

function _base64ToArrayBuffer(base64) {
	var binary_string =  window.atob(base64);
	var len = binary_string.length;
	var bytes = new Uint8Array( len );
	for (var i = 0; i < len; i++)        {
		bytes[i] = binary_string.charCodeAt(i);
	}
	return bytes.buffer;
}
 export default Mda;