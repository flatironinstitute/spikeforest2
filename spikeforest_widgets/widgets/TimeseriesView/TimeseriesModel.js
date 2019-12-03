export default function TimeseriesModel(params) {
    let m_samplerate = params.samplerate;
    let m_num_channels = params.num_channels;
    let m_num_timepoints = params.num_timepoints;
    let m_segment_size = params.segment_size;
    let m_data_segments = {};
    let m_request_data_segment_handlers = [];
    let m_data_segment_set_handlers = [];
    let m_data_segments_requested = {};

    this.clear = function() {
      m_data_segments = {};
      m_data_segments_requested.clear();
    }
  
    this.setDataSegment = function (ds_factor, segment_num, X) {
      let timer = new Date()
      if (!m_data_segments[ds_factor]) m_data_segments[ds_factor] = {};
      m_data_segments[ds_factor][segment_num] = X;
      for (let ih in m_data_segment_set_handlers) {
        m_data_segment_set_handlers[ih](ds_factor, m_segment_size * ds_factor * segment_num, m_segment_size * ds_factor * (segment_num + 1));
      }
    }
    this.onRequestDataSegment = function (handler) {
      m_request_data_segment_handlers.push(handler);
    }
    this.onDataSegmentSet = function (handler) {
      m_data_segment_set_handlers.push(handler);
    }
  
    this.waitForChannelData = async function(ch, t1, t2, ds_factor, opts) {
      let timer = new Date();
      while (true) {
        let data0 = this.getChannelData(ch, t1, t2, ds_factor, opts);
        if ((data0.length == 0) || (!isNaN(data0[0]))) return data0;
        await timeout(100);
        if (opts.timeout) {
          let elapsed = (new Date()) - timer;
          if (elapsed > opts.timeout)
            return null;
        }
      }
    }
  
    this.getChannelData = function (ch, t1, t2, ds_factor, opts) {
      opts = opts || {};
      let ret = [];
      if (ds_factor == 1) {
        for (let t = t1; t < t2; t++) {
          ret.push(NaN);
        }
      }
      else {
        for (let t = t1; t < t2; t++) {
          ret.push(NaN);
          ret.push(NaN);
        }
      }
      let s1 = Math.floor(t1 / m_segment_size);
      let s2 = Math.floor(t2 / m_segment_size);
      if (!opts.request_only) {
        if (s1 == s2) {
          let X = (m_data_segments[ds_factor] || {})[s1] || null;
          let t1_rel = (t1 - s1 * m_segment_size);
          if (X) {
            if (ds_factor == 1) {
              for (let ii = 0; ii < t2 - t1; ii++) {
                ret[ii] = X.value(ch, t1_rel + ii);
              }
            }
            else {
              for (let ii = 0; ii < t2 - t1; ii++) {
                ret[ii * 2] = X.value(ch, (t1_rel + ii) * 2);
                ret[ii * 2 + 1] = X.value(ch, (t1_rel + ii) * 2 + 1);
              }
            }
          }
        }
        else {
          let ii_0 = 0;
          for (let ss = s1; ss <= s2; ss++) {
            let X = (m_data_segments[ds_factor] || {})[ss] || null;
            if (ss == s1) {
              let t1_rel = (t1 - ss * m_segment_size);
              if (X) {
                if (ds_factor == 1) {
                  for (let ii = 0; ii < m_segment_size - t1_rel; ii++) {
                    ret[ii] = X.value(ch, t1_rel + ii);
                  }
                }
                else {
                  for (let ii = 0; ii < m_segment_size - t1_rel; ii++) {
                    ret[ii * 2] = X.value(ch, (t1_rel + ii) * 2);
                    ret[ii * 2 + 1] = X.value(ch, (t1_rel + ii) * 2 + 1);
                  }
                }
              }
              ii_0 = m_segment_size - t1_rel;
            }
            else if (ss == s2) {
              let t2_rel = (t2 - ss * m_segment_size);
              if (X) {
                if (ds_factor == 1) {
                  for (let ii = ii_0; ii < ii_0 + t2_rel; ii++) {
                    ret[ii] = X.value(ch, ii - ii_0);
                  }
                }
                else {
                  for (let ii = ii_0; ii < ii_0 + t2_rel; ii++) {
                    ret[ii * 2] = X.value(ch, (ii - ii_0) * 2);
                    ret[ii * 2 + 1] = X.value(ch, (ii - ii_0) * 2 + 1);
                  }
                }
              }
              ii_0 = ii_0 + t2_rel;
            }
            else {
              if (X) {
                if (ds_factor == 1) {
                  for (let ii = ii_0; ii < ii_0 + m_segment_size; ii++) {
                    ret[ii] = X.value(ch, ii - ii_0);
                  }
                }
                else {
                  for (let ii = ii_0; ii < ii_0 + m_segment_size; ii++) {
                    ret[ii * 2] = X.value(ch, (ii - ii_0) * 2);
                    ret[ii * 2 + 1] = X.value(ch, (ii - ii_0) * 2 + 1);
                  }
                }
              }
              ii_0 = ii_0 + m_segment_size;
            }
          }
        }
      }
      //for (let ss=s1; ss<=s2; ss++) {
      for (let ss = s1 - 1; ss <= s2 + 1; ss++) {
        if ((ss >= 0) && (ss < Math.ceil(m_num_timepoints / m_segment_size))) {
          if (!(m_data_segments[ds_factor] || {})[ss]) {
            let code0 = ds_factor + '--' + ss;
            if (!(code0 in m_data_segments_requested)) {
              for (let ih in m_request_data_segment_handlers) {
                m_request_data_segment_handlers[ih](ds_factor, ss);
              }
              m_data_segments_requested[code0] = true;
            }
          }
        }
      }
      return ret;
    };
    this.numChannels = function () {
      return m_num_channels;
    };
    this.numTimepoints = function () {
      return m_num_timepoints;
    };
    this.getSampleRate = function () {
      return m_samplerate;
    }
  }
  
  function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }