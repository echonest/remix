'use strict';

var WaveSurfer = {
    init: function (params) {
        var my = this;
        this.drawer = Object.create(WaveSurfer.Drawer);
        this.drawer.init(params);
    },

    loadBuffer: function(quanta) {
        var my = this;
        my.drawer.remixedData = quanta;
        my.drawer.drawBuffer()
    },

};
