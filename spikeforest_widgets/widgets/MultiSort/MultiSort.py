import hither_sf as hither
from spikeforest2 import sorters

class MultiSort:
    def __init__(self):
        super().__init__()
        self._job_manager = JobManager()
        self._job_manager.on_job_updated(lambda job: self._handle_job_updated(job))

    def javascript_state_changed(self, prev_state, state):
        self._set_status('running', 'Running MultiSort')

        # Processing code goes here
        # The state argument contains the state set from the javacript code
        # In .js file, use this.pythonInterface.setState({...})

        self._set_status('finished', 'Finished MultiSort')

    def on_message(self, msg):
        # process custom messages from JavaScript here
        # In .js file, use this.pythonInterface.sendMessage({...})
        if msg['name'] == 'startSpikeSortingJob':
            job = msg['job']
            self._job_manager.add_job(job)
            job['status'] = 'running'
            self._handle_job_updated(job)
    
    def _handle_job_updated(self, job):
        self._send_message(dict(
            name='updateSpikeSortingJob',
            job=job
        ))
    
    # Send a custom message to JavaScript side
    # In .js file, use this.pythonInterface.onMessage((msg) => {...})
    def _send_message(self, msg):
        self.send_message(msg)

    # Set the python state
    def _set_state(self, **kwargs):
        self.set_state(kwargs)
    
    # Set error status with a message
    def _set_error(self, error_message):
        self._set_status('error', error_message)
    
    # Set status and a status message. Use running', 'finished', 'error'
    def _set_status(self, status, status_message=''):
        self._set_state(status=status, status_message=status_message)

class JobManager:
    def __init__(self):
        self._jobs = []
        self._job_updated_handlers = []
    def add_job(self, job):
        self._jobs.append(job)
        sorter_name = job['sorterName']
        recording_path = job['recordingPath']
        sorter = getattr(sorters, sorter_name)
        with hither.config(container='default'), hither.job_queue():
            sorting_result = sorter.run(
                recording_path=recording_path,
                sorting_out=hither.File()
            )
        job['status'] = 'finished'
        for handler in self._job_updated_handlers:
            handler(job)
    def on_job_updated(self, handler):
        self._job_updated_handlers.append(handler)