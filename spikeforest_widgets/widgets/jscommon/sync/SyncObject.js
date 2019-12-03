class SyncObject {
    components = [];
    state = {};
    addComponent(component, sync) {
        this.components.push({
            component: component,
            sync: sync
        });
    }
    removeComponent(component, sync) {
        let new_components = [];
        for (let comp of this.components) {
            if (comp.component != component)
                new_components.push(comp);
        }
        this.components = new_components;
    }
    updateComponent(component) {
        for (let comp of this.components) {
            if (comp.component == component) {
                let new_state = {};
                for (let key in comp.sync.syncState) {
                    new_state[comp.sync.syncState[key]] = comp.component.state[key];
                }
                this.setState(new_state);
            }
        }
    }
    setState(state) {
        let changed_state = {};
        let something_changed = false;
        for (let key in state) {
            if (JSON.stringify(state[key]) !== JSON.stringify(this.state[key])) {
                this.state[key] = state[key];
                changed_state[key] = state[key];
                something_changed = true;
            }
        }
        if (something_changed) {
            for (let comp of this.components) {
                let changed_state2 = {};
                let something_changed2 = false;
                for (let key in comp.sync.syncState) {
                    let key2 = comp.sync.syncState[key];
                    if (key2 in changed_state) {
                        if (JSON.stringify(comp.component.state[key]) !== JSON.stringify(changed_state[key2])) {
                            changed_state2[key] = changed_state[key2];
                            something_changed2 = true;
                        }
                    }
                }
                if (something_changed2) {
                    comp.component.setState(changed_state2);
                }
            }
        }
    }
}

function get_sync_object(id) {
    window.reactopya_sync_objects = window.reactopya_sync_objects || {};
    if (!(id in window.reactopya_sync_objects)) {
        window.reactopya_sync_objects[id] = new SyncObject();
    }
    return window.reactopya_sync_objects[id];
}

function start_sync(component, sync) {
    if (!sync) return;
    for (let sync0 of sync) {
        let X = get_sync_object(sync0.id);
        X.addComponent(component, sync0);
    }
}

function stop_sync(component, sync) {
    if (!sync) return;
    for (let sync0 of sync) {
        let X = get_sync_object(sync0.id);
        X.removeComponent(component);
    }
}

function update_sync(component, sync) {
    if (!sync) return;
    for (let sync0 of sync) {
        let X = get_sync_object(sync0.id);
        X.updateComponent(component);
    }
}

export default function createSync(sync) {
    if (!sync) return undefined;
    return {
        start: function(component) {start_sync(component, sync);},
        stop: function(component) {stop_sync(component, sync);},
        update: function(component) {update_sync(component, sync);},
    }
}