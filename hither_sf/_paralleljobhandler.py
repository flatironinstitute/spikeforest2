from typing import List, Dict, Any
import time
import multiprocessing
from multiprocessing.connection import Connection
import time
import hither_sf as hither

class ParallelJobHandler:
    def __init__(self, num_workers):
        self._num_workers = num_workers
        self._processes: List[dict] = []
        self._halted = False

    def handle_job(self, job):
        import kachery as ka
        pipe_to_parent, pipe_to_child = multiprocessing.Pipe()
        process = multiprocessing.Process(target=_pjh_run_job, args=(pipe_to_parent, job, ka.get_config()))
        self._processes.append(dict(
            job=job,
            process=process,
            pipe_to_child=pipe_to_child,
            pjh_status='pending'
        ))
    
    def iterate(self):
        if self._halted:
            return

        for p in self._processes:
            if p['pjh_status'] == 'running':
                if p['pipe_to_child'].poll():
                    result_obj = p['pipe_to_child'].recv()
                    p['pipe_to_child'].send('okay!')
                    result0 = hither.Result()
                    result0.deserialize(result_obj)
                    hither._set_result(p['job'], result0)
                    p['pjh_status'] = 'finished'
        
        num_running = 0
        for p in self._processes:
            if p['pjh_status'] == 'running':
                num_running = num_running + 1

        for p in self._processes:
            if p['pjh_status'] == 'pending':
                if num_running < self._num_workers:
                    p['pjh_status'] = 'running'
                    p['process'].start()
                    num_running = num_running + 1

        time.sleep(1)
    def cleanup(self):
        pass

def _pjh_run_job(pipe_to_parent: Connection, job: Dict[str, Any], kachery_config: dict) -> None:
    import kachery as ka
    ka.set_config(**kachery_config)
    hither._run_job(job)
    pipe_to_parent.send(job['result'].serialize())
    # wait for message to return
    while True:
        if pipe_to_parent.poll():
            pipe_to_parent.recv()
            return
        time.sleep(0.1)