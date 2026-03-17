/**
 * 历史英雄对决 - 音频管理
 * BGM 使用 static/audio/bgm/ 下文件（可选）；SFX 使用内置占位音效（Web Audio）或 static/audio/sfx/
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'history_heroes_audio';
    var defaults = { bgm: 0.5, sfx: 0.7, muted: false };

    function loadSettings() {
        try {
            var s = localStorage.getItem(STORAGE_KEY);
            return s ? Object.assign({}, defaults, JSON.parse(s)) : Object.assign({}, defaults);
        } catch (e) {
            return Object.assign({}, defaults);
        }
    }

    function saveSettings(s) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
        } catch (e) {}
    }

    // ---------- Web Audio 占位音效（无需音频文件） ----------
    var audioCtx = null;

    function getCtx() {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        return audioCtx;
    }

    function playTone(opts) {
        var ctx = getCtx();
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = opts.type || 'sine';
        osc.frequency.setValueAtTime(opts.freq || 440, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(opts.freqEnd || opts.freq || 440, ctx.currentTime + (opts.duration || 0.1));
        gain.gain.setValueAtTime(opts.volume !== undefined ? opts.volume : 0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + (opts.duration || 0.1));
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + (opts.duration || 0.1));
    }

    var sfxPresets = {
        click:   { freq: 600,  freqEnd: 400, duration: 0.06, volume: 0.12, type: 'sine' },
        success: { freq: 523,  freqEnd: 784, duration: 0.15, volume: 0.15, type: 'sine' },
        hit:     { freq: 200,  freqEnd: 100, duration: 0.12, volume: 0.2,  type: 'square' },
        crit:    { freq: 400,  freqEnd: 800, duration: 0.2,  volume: 0.18, type: 'sine' },
        heal:    { freq: 330,  freqEnd: 440, duration: 0.2,  volume: 0.12, type: 'sine' },
        summon_common:  { freq: 400, duration: 0.1, volume: 0.1, type: 'sine' },
        summon_rare:    { freq: 523, duration: 0.15, volume: 0.12, type: 'sine' },
        summon_epic:   { freq: 659, freqEnd: 880, duration: 0.25, volume: 0.14, type: 'sine' },
        summon_legendary: { freq: 523, freqEnd: 1047, duration: 0.4, volume: 0.16, type: 'sine' },
        victory: { freq: 523, freqEnd: 1047, duration: 0.3, volume: 0.15, type: 'sine' },
        defeat:  { freq: 200, freqEnd: 150, duration: 0.3, volume: 0.15, type: 'sine' }
    };

    // ---------- BGM：优先加载文件，无文件则静音 ----------
    var bgmEl = null;
    var currentBgmSrc = null;

    function getBgmUrl() {
        // 可放 main.ogg 或 main.mp3 到 static/audio/bgm/
        var base = window.__STATIC_URL__ || '';
        if (base && !base.endsWith('/')) base += '/';
        return base + 'audio/bgm/main.ogg';
    }

    function ensureBgmEl() {
        if (!bgmEl) {
            bgmEl = document.createElement('audio');
            bgmEl.loop = true;
            bgmEl.preload = 'auto';
        }
        return bgmEl;
    }

    function playBgm(volume) {
        var el = ensureBgmEl();
        var url = getBgmUrl();
        if (url !== currentBgmSrc) {
            el.src = url;
            currentBgmSrc = url;
            el.load();
        }
        el.volume = Math.max(0, Math.min(1, volume));
        el.play().catch(function () {});
    }

    function stopBgm() {
        if (bgmEl) {
            bgmEl.pause();
            bgmEl.currentTime = 0;
        }
    }

    // ---------- 对外 API ----------
    var settings = loadSettings();

    window.AudioManager = {
        playBgm: function () {
            if (settings.muted) return;
            playBgm(settings.bgm);
        },
        stopBgm: function () { stopBgm(); },
        setBgmVolume: function (v) {
            settings.bgm = Math.max(0, Math.min(1, v));
            saveSettings(settings);
            if (bgmEl) bgmEl.volume = settings.bgm;
        },
        setSfxVolume: function (v) {
            settings.sfx = Math.max(0, Math.min(1, v));
            saveSettings(settings);
        },
        playSfx: function (name) {
            if (settings.muted) return;
            var preset = sfxPresets[name];
            if (!preset) return;
            var vol = (preset.volume !== undefined ? preset.volume : 0.15) * settings.sfx;
            playTone(Object.assign({}, preset, { volume: vol }));
        },
        setMuted: function (muted) {
            settings.muted = !!muted;
            saveSettings(settings);
            if (settings.muted) stopBgm();
        },
        isMuted: function () { return settings.muted; },
        getBgmVolume: function () { return settings.bgm; },
        getSfxVolume: function () { return settings.sfx; }
    };

    // 供 Flask 在 base 中注入：window.__STATIC_URL__ = "{{ url_for('static', filename='') }}";
    if (typeof window.__STATIC_URL__ !== 'string') {
        window.__STATIC_URL__ = '';
    }
})();
