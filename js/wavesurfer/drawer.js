'use strict';

WaveSurfer.Drawer = {
    defaultParams: {
        waveColor: '#333',
        progressColor: '#999',
        cursorWidth: 1,
        loadingColor: '#333',
        loadingBars: 20,
        barHeight: 1,
        barMargin: 10
    },

    init: function (params) {
        var my = this;
        this.params = Object.create(params);
        Object.keys(this.defaultParams).forEach(function (key) {
            if (!(key in params)) { params[key] = my.defaultParams[key]; }
        });

        this.canvas = params.canvas;

        this.width = this.canvas.clientWidth;
        this.height = this.canvas.clientHeight;
        this.cc = this.canvas.getContext('2d');

        if (params.image) {
            this.loadImage(params.image, this.drawImage.bind(this));
        }

        if (!this.width || !this.height) {
            console.error('Canvas size is zero.');
        }
    },

    getPeaks: function (remixedData) {
        var my = this;

        // k is the samples per pixel
        var k = remixedData[0].track.buffer.getChannelData(0).length / this.width;
        var slice = Array.prototype.slice;
        var sums = [];
        var currentBuffer;

        // This gets only the frames that match the selected chunks
        if (remixedData != null) {
            var peakIndex = 0;
            for (var index = 0; index < remixedData.length; index++) {
                var startSample = parseFloat(remixedData[index].start) * 44100;
                var endSample = (parseFloat(remixedData[index].start) + parseFloat(remixedData[index].duration)) * 44100;
                var numPixels = (endSample - startSample) / k;

                currentBuffer = remixedData[index].track.buffer;
            
                for (var i = 0; i < numPixels; i++) {
                    var sum = 0;
                    for (var c = 0; c < currentBuffer.numberOfChannels; c++) {
                        var chan = currentBuffer.getChannelData(c);
                        var vals = slice.call(chan, startSample + (i * k), startSample + ((i + 1) * k));
                        var peak = Math.max.apply(Math, vals.map(Math.abs));
                        sum += peak;
                    }
                    sums[peakIndex] = sum;
                    peakIndex++;
                }
            }
        
        }
        return sums;
    },

    progress: function (percents) {
        this.cursorPos = ~~(this.width * percents);
        this.redraw();
    },

    drawBuffer: function () {
        this.peaks = this.getPeaks(this.remixedData);
        this.maxPeak = Math.max.apply(Math, this.peaks);
        this.progress(0);
    },

    /**
     * Redraws the entire canvas on each audio frame.
     */
    redraw: function () {
        var my = this;

        this.clear();

        // Draw WebAudio buffer peaks.
        if (this.peaks) {
            this.peaks && this.peaks.forEach(function (peak, index) {
                my.drawFrame(index, peak, my.maxPeak);
            });
        // Or draw an image.
        } else if (this.image) {
            this.drawImage();
        }
    },

    clear: function () {
        this.cc.clearRect(0, 0, this.width, this.height);
    },

    drawFrame: function (index, value, max) {
        var w = 1;
        var h = Math.round(value * (this.height / max));

        var x = index * w;
        var y = Math.round((this.height - h) / 2);

        this.cc.fillStyle = this.params.waveColor;
        this.cc.fillRect(x, y, w, h);
    },


    /**
     * Loads and caches an image.
     */
    loadImage: function (url, callback) {
        var my = this;
        var img = document.createElement('img');
        var onLoad = function () {
            img.removeEventListener('load', onLoad);
            my.image = img;
            callback(img);
        };
        img.addEventListener('load', onLoad, false);
        img.src = url;
    },

    /**
     * Draws a pre-drawn waveform image.
     */
    drawImage: function () {
        var cc = this.cc;
        cc.drawImage(this.image, 0, 0, this.width, this.height);
        cc.save();
        cc.globalCompositeOperation = 'source-atop';
        cc.fillStyle = this.params.progressColor;
        cc.fillRect(0, 0, this.cursorPos, this.height);
        cc.restore();
    },

    drawLoading: function (progress) {
        var color = this.params.loadingColor;
        var bars = this.params.loadingBars;
        var barHeight = this.params.barHeight;
        var margin = this.params.barMargin;
        var barWidth = ~~(this.width / bars) - margin;
        var progressBars = ~~(bars * progress);
        var y = ~~(this.height - barHeight) / 2;

        this.cc.fillStyle = color;
        for (var i = 0; i < progressBars; i += 1) {
            var x = i * barWidth + i * margin;
            this.cc.fillRect(x, y, barWidth, barHeight);
        }
    }
};
