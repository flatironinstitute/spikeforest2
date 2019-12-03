import createSync from './createSync';

let sync_objects_by_id = {};

export default class Sync {
    constructor(component, sync_config) {
        this._component = component;
        if (!sync_config) return;
        if (!Array.isArray(sync_config))
            sync_config = [sync_config];
        this._sync_config = sync_config;
        if (this._sync_config) {
            this._syncer = createSync(this._sync_config);
        }
    }
    start() {
        if (this._syncer) this._syncer.start(this._component);
    }
    update() {
        if (this._syncer) this._syncer.update(this._component);
    }
    stop() {
        if (this._syncer) this._syncer.stop(this._component);
    }
}