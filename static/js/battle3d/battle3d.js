/**
 * 3D Battle Engine - Low-Poly procedural characters with element particle effects
 * Built on Three.js r128
 */
(function () {
  'use strict';

  /* ==================== CONSTANTS ==================== */
  var ELEM = {
    fire:     { pri: 0xff6b35, sec: 0xff8c42, glow: 0xff4500 },
    water:    { pri: 0x4fc3f7, sec: 0x81d4fa, glow: 0x0288d1 },
    wood:     { pri: 0x4ade80, sec: 0x86efac, glow: 0x22c55e },
    metal:    { pri: 0x94a3b8, sec: 0xcbd5e1, glow: 0x64748b },
    earth:    { pri: 0xa1887f, sec: 0xbcaaa4, glow: 0x795548 },
    light:    { pri: 0xfff176, sec: 0xffee58, glow: 0xfdd835 },
    dark:     { pri: 0x7e57c2, sec: 0x9575cd, glow: 0x512da8 },
    electric: { pri: 0xfacc15, sec: 0xfde047, glow: 0xeab308 },
    ice:      { pri: 0x67e8f9, sec: 0xa5f3fc, glow: 0x06b6d4 },
    fighting: { pri: 0xfb923c, sec: 0xfdba74, glow: 0xf97316 },
    flying:   { pri: 0xa5b4fc, sec: 0xc7d2fe, glow: 0x818cf8 },
    ground:   { pri: 0xd97706, sec: 0xfbbf24, glow: 0xb45309 }
  };

  var POS = {
    '1v1': { ally: [{ x: 0, z: 4 }], enemy: [{ x: 0, z: -4 }] },
    '3v3': {
      ally:  [{ x: -3, z: 4 }, { x: 0, z: 4 }, { x: 3, z: 4 }],
      enemy: [{ x: -3, z: -4 }, { x: 0, z: -4 }, { x: 3, z: -4 }]
    },
    '5v5': {
      ally:  [{ x: -5, z: 4.5 }, { x: -2.5, z: 4 }, { x: 0, z: 4.5 }, { x: 2.5, z: 4 }, { x: 5, z: 4.5 }],
      enemy: [{ x: -5, z: -4.5 }, { x: -2.5, z: -4 }, { x: 0, z: -4.5 }, { x: 2.5, z: -4 }, { x: 5, z: -4.5 }]
    }
  };

  var SKIN = 0xffdbac;

  /* ==================== UTILITY ==================== */
  function elemColor(el) { return ELEM[el] || ELEM.fire; }

  function lerp(a, b, t) { return a + (b - a) * t; }

  function delay(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function makeCanvasTexture(text, hpPct, color, w, h) {
    var c = document.createElement('canvas');
    c.width = w || 256; c.height = h || 80;
    var ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 22px sans-serif';
    ctx.textAlign = 'center';
    ctx.shadowColor = '#000'; ctx.shadowBlur = 4;
    ctx.fillText(text, c.width / 2, 24);
    ctx.shadowBlur = 0;
    var barY = 34, barH = 14, barW = c.width - 40, barX = 20;
    ctx.fillStyle = '#222'; ctx.fillRect(barX, barY, barW, barH);
    ctx.fillStyle = color || '#22c55e';
    ctx.fillRect(barX, barY, barW * Math.max(0, Math.min(1, hpPct)), barH);
    ctx.strokeStyle = '#555'; ctx.lineWidth = 1;
    ctx.strokeRect(barX, barY, barW, barH);
    ctx.fillStyle = '#ddd'; ctx.font = '16px sans-serif';
    ctx.fillText(Math.round(hpPct * 100) + '%', c.width / 2, barY + barH + 18);
    return new THREE.CanvasTexture(c);
  }

  /* ==================== ENGINE ==================== */
  function Battle3DEngine() {
    this.scene = null; this.camera = null; this.renderer = null;
    this.chars = {};
    this.effects = [];
    this.clock = null;
    this.ready = false;
    this._raf = null;
    this.battleMode = '3v3';
    this.animSpeed = 1;
  }

  Battle3DEngine.prototype.init = function (container, alliesData, enemiesData, mode) {
    if (!container) { console.warn('Battle3D: no container'); return; }
    this.container = container;
    this.battleMode = mode || '3v3';
    this.clock = new THREE.Clock();
    this._setupScene();
    this._setupCamera();
    this._setupLights();
    this._setupGround();
    this._setupSkyParticles();
    this._createCharacters(alliesData, enemiesData);
    this._animate();
    this.ready = true;
  };

  /* --- Scene --- */
  Battle3DEngine.prototype._setupScene = function () {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0c1222);
    this.scene.fog = new THREE.FogExp2(0x0c1222, 0.025);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.appendChild(this.renderer.domElement);
    var self = this;
    window.addEventListener('resize', function () { self._onResize(); });
  };

  Battle3DEngine.prototype._setupCamera = function () {
    var w = this.container.clientWidth, h = this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 120);
    this.camera.position.set(0, 12, 16);
    this.camera.lookAt(0, 0, 0);
  };

  Battle3DEngine.prototype._setupLights = function () {
    this.scene.add(new THREE.AmbientLight(0x404060, 0.6));
    var dir = new THREE.DirectionalLight(0xffeedd, 0.9);
    dir.position.set(5, 15, 8); dir.castShadow = true;
    dir.shadow.mapSize.width = 1024; dir.shadow.mapSize.height = 1024;
    this.scene.add(dir);
    var fill = new THREE.DirectionalLight(0x6688cc, 0.35);
    fill.position.set(-6, 8, -4); this.scene.add(fill);
    var rim = new THREE.PointLight(0xff6644, 0.4, 30);
    rim.position.set(0, 5, -12); this.scene.add(rim);
  };

  Battle3DEngine.prototype._setupGround = function () {
    var canvas = document.createElement('canvas');
    canvas.width = 512; canvas.height = 512;
    var ctx = canvas.getContext('2d');
    ctx.fillStyle = '#1a1a3a'; ctx.fillRect(0, 0, 512, 512);
    ctx.strokeStyle = '#2a2a5a'; ctx.lineWidth = 1;
    for (var i = 0; i <= 16; i++) {
      var p = i * 32;
      ctx.beginPath(); ctx.moveTo(p, 0); ctx.lineTo(p, 512); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, p); ctx.lineTo(512, p); ctx.stroke();
    }
    var tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(4, 4);
    var mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.85, metalness: 0.1 });
    var ground = new THREE.Mesh(new THREE.PlaneGeometry(50, 50), mat);
    ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
    this.scene.add(ground);

    var ringGeo = new THREE.RingGeometry(5, 5.15, 64);
    var allyRing = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0x22c55e, transparent: true, opacity: 0.25, side: THREE.DoubleSide }));
    allyRing.rotation.x = -Math.PI / 2; allyRing.position.set(0, 0.02, 4); this.scene.add(allyRing);
    var enemyRing = new THREE.Mesh(ringGeo.clone(), new THREE.MeshBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.25, side: THREE.DoubleSide }));
    enemyRing.rotation.x = -Math.PI / 2; enemyRing.position.set(0, 0.02, -4); this.scene.add(enemyRing);
  };

  Battle3DEngine.prototype._setupSkyParticles = function () {
    var n = 200, pos = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 50;
      pos[i * 3 + 1] = 2 + Math.random() * 15;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 40;
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.skyParticles = new THREE.Points(geo, new THREE.PointsMaterial({ color: 0x8888cc, size: 0.08, transparent: true, opacity: 0.5 }));
    this.scene.add(this.skyParticles);
  };

  Battle3DEngine.prototype._onResize = function () {
    if (!this.container || !this.camera || !this.renderer) return;
    var w = this.container.clientWidth, h = this.container.clientHeight;
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  };

  /* --- Characters --- */
  Battle3DEngine.prototype._createCharacters = function (allies, enemies) {
    var cfg = POS[this.battleMode] || POS['3v3'];
    var self = this;
    (allies || []).forEach(function (d, i) {
      var pos = cfg.ally[i] || { x: i * 3 - 3, z: 4 };
      self._addChar('ally', i, d, pos, false);
    });
    (enemies || []).forEach(function (d, i) {
      var pos = cfg.enemy[i] || { x: i * 3 - 3, z: -4 };
      self._addChar('enemy', i, d, pos, true);
    });
  };

  Battle3DEngine.prototype._addChar = function (side, idx, data, pos, flip) {
    var g = new THREE.Group();
    var ec = elemColor(data.element);
    var rt = data.role_type || 'warrior';

    this._buildBody(g, rt, ec);
    this._addAura(g, ec);

    var shadow = new THREE.Mesh(new THREE.CircleGeometry(0.55, 24), new THREE.MeshBasicMaterial({ color: 0, transparent: true, opacity: 0.3 }));
    shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.02; g.add(shadow);

    g.position.set(pos.x, 0, pos.z);
    if (flip) g.rotation.y = Math.PI;

    var hpColor = side === 'ally' ? '#22c55e' : '#ef4444';
    var label = this._makeLabel(data.name + ' Lv.' + data.level, 1, hpColor);
    label.position.y = 3.4;
    if (flip) label.rotation.y = Math.PI;
    g.add(label);

    g.userData = {
      side: side, idx: idx, data: data,
      homeX: pos.x, homeZ: pos.z,
      hpPct: 1, label: label, hpColor: hpColor,
      time: Math.random() * 100, dead: false
    };
    this.scene.add(g);
    this.chars[side + '_' + idx] = g;
  };

  Battle3DEngine.prototype._makeLabel = function (name, hpPct, color) {
    var tex = makeCanvasTexture(name, hpPct, color);
    var mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
    var sp = new THREE.Sprite(mat);
    sp.scale.set(2.5, 0.8, 1);
    sp.userData._name = name; sp.userData._color = color;
    return sp;
  };

  Battle3DEngine.prototype.updateHp = function (side, idx, pct) {
    var ch = this.chars[side + '_' + idx]; if (!ch) return;
    ch.userData.hpPct = pct;
    var lb = ch.userData.label;
    if (lb && lb.material) {
      lb.material.map = makeCanvasTexture(lb.userData._name, pct, lb.userData._color);
      lb.material.map.needsUpdate = true;
    }
  };

  /* --- Body builder --- */
  Battle3DEngine.prototype._buildBody = function (g, roleType, ec) {
    var bodyMat = new THREE.MeshPhongMaterial({ color: ec.pri, flatShading: true, shininess: 30 });
    var skinMat = new THREE.MeshPhongMaterial({ color: SKIN, flatShading: true });
    var darkMat = new THREE.MeshPhongMaterial({ color: 0x333344, flatShading: true });

    switch (roleType) {
      case 'mage': this._buildMage(g, bodyMat, skinMat, ec); break;
      case 'archer': this._buildArcher(g, bodyMat, skinMat, darkMat, ec); break;
      case 'assassin': this._buildAssassin(g, bodyMat, skinMat, darkMat, ec); break;
      case 'healer': this._buildHealer(g, bodyMat, skinMat, ec); break;
      default: this._buildWarrior(g, bodyMat, skinMat, darkMat, ec); break;
    }
  };

  Battle3DEngine.prototype._buildWarrior = function (g, bMat, sMat, dMat, ec) {
    var body = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1, 0.55), bMat);
    body.position.y = 1.5; body.castShadow = true; g.add(body);
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), sMat);
    head.position.y = 2.4; head.castShadow = true; g.add(head);
    var helmet = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.35, 6), new THREE.MeshPhongMaterial({ color: 0x888899, flatShading: true, shininess: 80 }));
    helmet.position.y = 2.72; g.add(helmet);
    this._addLimbs(g, dMat, 0.9);
    var sword = this._makeSword(ec); sword.position.set(0.65, 1.4, 0.1); g.add(sword);
    g.userData.weapon = sword;
    var shield = new THREE.Mesh(new THREE.CircleGeometry(0.35, 6), new THREE.MeshPhongMaterial({ color: ec.pri, flatShading: true, shininess: 60 }));
    shield.position.set(-0.65, 1.4, 0.2); g.add(shield);
  };

  Battle3DEngine.prototype._buildMage = function (g, bMat, sMat, ec) {
    var robe = new THREE.Mesh(new THREE.ConeGeometry(0.6, 1.8, 8), bMat);
    robe.position.y = 0.9; robe.castShadow = true; g.add(robe);
    var torso = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.38, 0.7, 8), bMat);
    torso.position.y = 1.9; torso.castShadow = true; g.add(torso);
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 6), sMat);
    head.position.y = 2.5; head.castShadow = true; g.add(head);
    var hat = new THREE.Mesh(new THREE.ConeGeometry(0.42, 0.7, 6), new THREE.MeshPhongMaterial({ color: 0x1a1a3a, flatShading: true }));
    hat.position.y = 3.0; g.add(hat);
    var staff = this._makeStaff(ec); staff.position.set(0.6, 0, 0); g.add(staff);
    g.userData.weapon = staff;
  };

  Battle3DEngine.prototype._buildArcher = function (g, bMat, sMat, dMat, ec) {
    var body = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.9, 0.45), new THREE.MeshPhongMaterial({ color: 0x2d5a27, flatShading: true }));
    body.position.y = 1.5; body.castShadow = true; g.add(body);
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.28, 8, 6), sMat);
    head.position.y = 2.3; head.castShadow = true; g.add(head);
    var hood = new THREE.Mesh(new THREE.ConeGeometry(0.32, 0.35, 6), bMat);
    hood.position.y = 2.55; g.add(hood);
    this._addLimbs(g, dMat, 0.7);
    var bow = this._makeBow(ec); bow.position.set(0.55, 1.4, 0); g.add(bow);
    g.userData.weapon = bow;
  };

  Battle3DEngine.prototype._buildAssassin = function (g, bMat, sMat, dMat, ec) {
    var ninMat = new THREE.MeshPhongMaterial({ color: 0x1a1a2e, flatShading: true });
    var body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.85, 0.4), ninMat);
    body.position.y = 1.5; body.castShadow = true; g.add(body);
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.26, 8, 6), ninMat);
    head.position.y = 2.2; head.castShadow = true; g.add(head);
    var eyeMat = new THREE.MeshBasicMaterial({ color: ec.pri });
    var le = new THREE.Mesh(new THREE.SphereGeometry(0.04, 6, 4), eyeMat);
    le.position.set(-0.09, 2.23, 0.22); g.add(le);
    var re = le.clone(); re.position.set(0.09, 2.23, 0.22); g.add(re);
    this._addLimbs(g, ninMat, 0.6);
    var dg1 = this._makeDagger(ec); dg1.position.set(-0.48, 1.2, 0); dg1.rotation.z = -0.4; g.add(dg1);
    var dg2 = this._makeDagger(ec); dg2.position.set(0.48, 1.2, 0); dg2.rotation.z = 0.4; g.add(dg2);
    g.userData.weapon = dg1;
  };

  Battle3DEngine.prototype._buildHealer = function (g, bMat, sMat, ec) {
    var whiteMat = new THREE.MeshPhongMaterial({ color: 0xeeeeee, flatShading: true });
    var robe = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1.6, 8), whiteMat);
    robe.position.y = 0.8; robe.castShadow = true; g.add(robe);
    var torso = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.34, 0.65, 8), whiteMat);
    torso.position.y = 1.75; torso.castShadow = true; g.add(torso);
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.28, 8, 6), sMat);
    head.position.y = 2.35; head.castShadow = true; g.add(head);
    var halo = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.025, 6, 24), new THREE.MeshBasicMaterial({ color: 0xffdd00 }));
    halo.position.y = 2.75; halo.rotation.x = Math.PI / 2; g.add(halo);
    g.userData.halo = halo;
    var orb = new THREE.Mesh(new THREE.SphereGeometry(0.14, 8, 8), new THREE.MeshBasicMaterial({ color: ec.pri, transparent: true, opacity: 0.8 }));
    orb.position.set(0.5, 1.5, 0); g.add(orb);
    g.userData.weapon = orb;
  };

  Battle3DEngine.prototype._addLimbs = function (g, mat, bodyW) {
    var lGeo = new THREE.CylinderGeometry(0.12, 0.1, 0.7, 6);
    var ll = new THREE.Mesh(lGeo, mat); ll.position.set(-bodyW * 0.22, 0.35, 0); ll.castShadow = true; g.add(ll);
    var rl = new THREE.Mesh(lGeo, mat); rl.position.set(bodyW * 0.22, 0.35, 0); rl.castShadow = true; g.add(rl);
  };

  /* --- Weapons --- */
  Battle3DEngine.prototype._makeSword = function (ec) {
    var g = new THREE.Group();
    var blade = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.0, 0.02), new THREE.MeshPhongMaterial({ color: 0xccccdd, shininess: 120, flatShading: true }));
    blade.position.y = 0.5; g.add(blade);
    var guard = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.05, 0.05), new THREE.MeshPhongMaterial({ color: 0xdaa520, shininess: 80 }));
    g.add(guard);
    var handle = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.2, 6), new THREE.MeshPhongMaterial({ color: 0x5c3a1e }));
    handle.position.y = -0.12; g.add(handle);
    return g;
  };

  Battle3DEngine.prototype._makeStaff = function (ec) {
    var g = new THREE.Group();
    var rod = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.045, 2.2, 6), new THREE.MeshPhongMaterial({ color: 0x5c3a1e, flatShading: true }));
    rod.position.y = 1.1; g.add(rod);
    var gem = new THREE.Mesh(new THREE.OctahedronGeometry(0.14, 0), new THREE.MeshBasicMaterial({ color: ec.pri }));
    gem.position.y = 2.3; g.add(gem); g.userData.gem = gem;
    return g;
  };

  Battle3DEngine.prototype._makeBow = function (ec) {
    var g = new THREE.Group();
    var pts = [];
    for (var i = 0; i <= 20; i++) {
      var t = i / 20, a = t * Math.PI;
      pts.push(new THREE.Vector3(Math.sin(a) * 0.15, -0.6 + t * 1.2, 0));
    }
    var curve = new THREE.CatmullRomCurve3(pts);
    var bowGeo = new THREE.TubeGeometry(curve, 20, 0.025, 6, false);
    g.add(new THREE.Mesh(bowGeo, new THREE.MeshPhongMaterial({ color: 0x5c3a1e, flatShading: true })));
    var strGeo = new THREE.BufferGeometry().setFromPoints([pts[0], new THREE.Vector3(0, 0, -0.05), pts[pts.length - 1]]);
    g.add(new THREE.Line(strGeo, new THREE.LineBasicMaterial({ color: 0xeeeeee })));
    return g;
  };

  Battle3DEngine.prototype._makeDagger = function (ec) {
    var g = new THREE.Group();
    var blade = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.45, 4), new THREE.MeshPhongMaterial({ color: 0xccccdd, shininess: 120, flatShading: true }));
    blade.position.y = 0.22; g.add(blade);
    var handle = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.12, 6), new THREE.MeshPhongMaterial({ color: 0x1a1a1a }));
    handle.position.y = -0.04; g.add(handle);
    return g;
  };

  /* --- Element aura --- */
  Battle3DEngine.prototype._addAura = function (g, ec) {
    var n = 16, pos = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      var a = (i / n) * Math.PI * 2, r = 0.45 + Math.random() * 0.25;
      pos[i * 3] = Math.cos(a) * r;
      pos[i * 3 + 1] = 0.8 + Math.random() * 1.4;
      pos[i * 3 + 2] = Math.sin(a) * r;
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.add(new THREE.Points(geo, new THREE.PointsMaterial({ color: ec.glow, size: 0.09, transparent: true, opacity: 0.55 })));
  };

  /* --- Animation loop --- */
  Battle3DEngine.prototype._animate = function () {
    var self = this;
    function loop() {
      self._raf = requestAnimationFrame(loop);
      var dt = self.clock.getDelta();
      var t = self.clock.getElapsedTime();

      if (self.skyParticles) self.skyParticles.rotation.y = t * 0.02;

      Object.keys(self.chars).forEach(function (k) {
        var ch = self.chars[k]; if (!ch || ch.userData.dead) return;
        ch.userData.time += dt;
        var bob = Math.sin(ch.userData.time * 2) * 0.04;
        ch.position.y = bob;
        if (ch.userData.halo) ch.userData.halo.rotation.z = t * 0.5;
        var wep = ch.userData.weapon;
        if (wep && wep.userData && wep.userData.gem) {
          wep.userData.gem.rotation.y = t * 2;
        }
      });

      for (var i = self.effects.length - 1; i >= 0; i--) {
        var e = self.effects[i];
        if (e.update) e.update(dt);
        if (e.isDead && e.isDead()) { self.scene.remove(e.mesh); self.effects.splice(i, 1); }
      }

      self.renderer.render(self.scene, self.camera);
    }
    loop();
  };

  /* ==================== PUBLIC API ==================== */

  Battle3DEngine.prototype.getChar = function (side, idx) {
    return this.chars[side + '_' + idx];
  };

  Battle3DEngine.prototype.highlight = function (side, idx) {
    var self = this;
    Object.keys(this.chars).forEach(function (k) {
      var ch = self.chars[k]; if (!ch) return;
      var isTarget = (k === side + '_' + idx);
      ch.traverse(function (c) {
        if (c.material && c.material.emissive) {
          c.material.emissive.setHex(isTarget ? 0x333300 : 0);
        }
      });
    });
  };

  Battle3DEngine.prototype.clearHighlight = function () {
    var self = this;
    Object.keys(this.chars).forEach(function (k) {
      var ch = self.chars[k]; if (!ch) return;
      ch.traverse(function (c) { if (c.material && c.material.emissive) c.material.emissive.setHex(0); });
    });
  };

  Battle3DEngine.prototype.selectTarget = function (side, idx) {
    this.clearHighlight();
    this.highlight(side, idx);
  };

  /* --- Attack animation (returns promise) --- */
  Battle3DEngine.prototype.playAttack = function (aSide, aIdx, dSide, dIdx, skill) {
    var self = this;
    var speed = this.animSpeed;
    return new Promise(function (resolve) {
      var attacker = self.chars[aSide + '_' + aIdx];
      var defender = self.chars[dSide + '_' + dIdx];
      if (!attacker || !defender) { resolve(); return; }

      var ax = attacker.userData.homeX, az = attacker.userData.homeZ;
      var dx = defender.position.x, dz = defender.position.z;
      var dist = Math.sqrt((dx - ax) * (dx - ax) + (dz - az) * (dz - az));
      var mx = ax + (dx - ax) * 0.7, mz = az + (dz - az) * 0.7;

      var dur = 350 / speed;
      var startTime = performance.now();

      function step(now) {
        var p = Math.min((now - startTime) / dur, 1);
        if (p < 0.5) {
          var t = p * 2;
          t = t * t * (3 - 2 * t);
          attacker.position.x = lerp(ax, mx, t);
          attacker.position.z = lerp(az, mz, t);
          if (attacker.userData.weapon) attacker.userData.weapon.rotation.z = t * 0.8;
        } else {
          var t2 = (p - 0.5) * 2;
          t2 = t2 * t2 * (3 - 2 * t2);
          attacker.position.x = lerp(mx, ax, t2);
          attacker.position.z = lerp(mz, az, t2);
          if (attacker.userData.weapon) attacker.userData.weapon.rotation.z = 0.8 * (1 - t2);
        }
        if (p < 1) requestAnimationFrame(step);
        else resolve();
      }
      requestAnimationFrame(step);
    });
  };

  /* --- Skill effect animation --- */
  Battle3DEngine.prototype.playSkillEffect = function (element, aSide, aIdx, dSide, dIdx) {
    var self = this;
    return new Promise(function (resolve) {
      var attacker = self.chars[aSide + '_' + aIdx];
      var defender = self.chars[dSide + '_' + dIdx];
      if (!attacker || !defender) { resolve(); return; }

      var ec = elemColor(element);
      var from = attacker.position;
      var to = defender.position;
      var n = 60, positions = new Float32Array(n * 3);
      var vels = [];
      for (var i = 0; i < n; i++) {
        positions[i * 3] = from.x + (Math.random() - 0.5) * 0.5;
        positions[i * 3 + 1] = 1.5 + Math.random() * 0.5;
        positions[i * 3 + 2] = from.z + (Math.random() - 0.5) * 0.5;
        var dx = to.x - from.x, dz = to.z - from.z;
        var d = Math.sqrt(dx * dx + dz * dz) || 1;
        vels.push({ x: (dx / d) * 0.22 + (Math.random() - 0.5) * 0.06, y: (Math.random() - 0.5) * 0.04, z: (dz / d) * 0.22 + (Math.random() - 0.5) * 0.06 });
      }
      var geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      var pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: ec.pri, size: 0.16, transparent: true, opacity: 0.85 }));
      self.scene.add(pts);

      var life = 35;
      var eff = {
        mesh: pts, update: function () {
          var pa = pts.geometry.attributes.position;
          for (var j = 0; j < n; j++) {
            pa.array[j * 3] += vels[j].x;
            pa.array[j * 3 + 1] += vels[j].y;
            pa.array[j * 3 + 2] += vels[j].z;
          }
          pa.needsUpdate = true;
          life--;
          pts.material.opacity = Math.max(0, life / 35);
        },
        isDead: function () { return life <= 0; }
      };
      self.effects.push(eff);

      setTimeout(function () {
        self._explosion(to, ec);
        resolve();
      }, 320 / self.animSpeed);
    });
  };

  Battle3DEngine.prototype._explosion = function (pos, ec) {
    var n = 80, positions = new Float32Array(n * 3), vels = [];
    for (var i = 0; i < n; i++) {
      positions[i * 3] = pos.x; positions[i * 3 + 1] = 1.5; positions[i * 3 + 2] = pos.z;
      var a = Math.random() * Math.PI * 2, s = 0.08 + Math.random() * 0.18;
      vels.push({ x: Math.cos(a) * s, y: Math.random() * 0.15, z: Math.sin(a) * s });
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    var pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: ec.sec, size: 0.18, transparent: true, opacity: 1 }));
    this.scene.add(pts);
    var life = 35;
    this.effects.push({
      mesh: pts,
      update: function () {
        var pa = pts.geometry.attributes.position;
        for (var j = 0; j < n; j++) {
          pa.array[j * 3] += vels[j].x; pa.array[j * 3 + 1] += vels[j].y; vels[j].y -= 0.006;
          pa.array[j * 3 + 2] += vels[j].z;
        }
        pa.needsUpdate = true; life--; pts.material.opacity = life / 35;
      },
      isDead: function () { return life <= 0; }
    });

    var flash = new THREE.PointLight(ec.glow, 3, 8);
    flash.position.set(pos.x, 2, pos.z); this.scene.add(flash);
    var self = this, fl = 12;
    var fadeEff = {
      mesh: flash,
      update: function () { fl--; flash.intensity = (fl / 12) * 3; },
      isDead: function () { return fl <= 0; }
    };
    this.effects.push(fadeEff);
  };

  /* --- Hit animation --- */
  Battle3DEngine.prototype.playHit = function (side, idx) {
    var ch = this.chars[side + '_' + idx]; if (!ch) return;
    ch.traverse(function (c) { if (c.material && c.material.emissive) c.material.emissive.setHex(0xff2200); });
    var ox = ch.userData.homeX;
    var count = 0;
    function shake() {
      if (count >= 6) { ch.position.x = ox; ch.traverse(function (c) { if (c.material && c.material.emissive) c.material.emissive.setHex(0); }); return; }
      ch.position.x = ox + (Math.random() - 0.5) * 0.25;
      count++;
      setTimeout(shake, 40);
    }
    shake();
  };

  /* --- Death animation --- */
  Battle3DEngine.prototype.playDeath = function (side, idx) {
    var ch = this.chars[side + '_' + idx]; if (!ch) return;
    ch.userData.dead = true;
    var dur = 600, st = performance.now(), self = this;
    function step(now) {
      var p = Math.min((now - st) / dur, 1);
      ch.position.y = -p * 0.6;
      ch.rotation.x = p * 0.4;
      ch.traverse(function (c) { if (c.material) { c.material.transparent = true; c.material.opacity = 1 - p; } });
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  };

  /* --- Floating damage number --- */
  Battle3DEngine.prototype.showDamage = function (side, idx, text, isHeal, isCrit) {
    var ch = this.chars[side + '_' + idx]; if (!ch) return;
    var c = document.createElement('canvas');
    c.width = 192; c.height = 72;
    var ctx = c.getContext('2d');
    var fontSize = isCrit ? 52 : 40;
    ctx.font = 'bold ' + fontSize + 'px sans-serif';
    ctx.textAlign = 'center';
    ctx.strokeStyle = '#000'; ctx.lineWidth = 4;
    ctx.fillStyle = isHeal ? '#22c55e' : (isCrit ? '#fbbf24' : '#ff4444');
    var display = (isHeal ? '+' : '-') + text;
    ctx.strokeText(display, 96, 52);
    ctx.fillText(display, 96, 52);
    var tex = new THREE.CanvasTexture(c);
    var sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
    sp.position.set(ch.position.x + (Math.random() - 0.5) * 0.5, 3.8, ch.position.z);
    sp.scale.set(isCrit ? 2.2 : 1.8, isCrit ? 0.8 : 0.65, 1);
    this.scene.add(sp);
    var startY = sp.position.y, life = 50, self = this;
    this.effects.push({
      mesh: sp,
      update: function () { life--; sp.position.y = startY + (1 - life / 50) * 2; sp.material.opacity = life / 50; },
      isDead: function () { return life <= 0; }
    });
  };

  /* --- Heal effect --- */
  Battle3DEngine.prototype.playHeal = function (side, idx) {
    var ch = this.chars[side + '_' + idx]; if (!ch) return;
    var n = 25, pos = ch.position;
    for (var i = 0; i < n; i++) {
      var sp = new THREE.Sprite(new THREE.SpriteMaterial({ color: 0x22c55e, transparent: true, opacity: 0.7 }));
      sp.scale.set(0.12, 0.12, 0.12);
      sp.position.set(pos.x + (Math.random() - 0.5), 0.3, pos.z + (Math.random() - 0.5));
      this.scene.add(sp);
      var vy = 0.03 + Math.random() * 0.03, life = 40;
      (function (s, v) {
        var l = life;
        this.effects.push({
          mesh: s,
          update: function () { l--; s.position.y += v; s.material.opacity = l / 40 * 0.7; },
          isDead: function () { return l <= 0; }
        });
      }).call(this, sp, vy);
    }
  };

  /* --- Camera shake --- */
  Battle3DEngine.prototype.cameraShake = function (intensity) {
    var cam = this.camera; if (!cam) return;
    var ox = cam.position.x, oy = cam.position.y;
    var c = 0;
    function shake() {
      if (c >= 8) { cam.position.x = ox; cam.position.y = oy; return; }
      cam.position.x = ox + (Math.random() - 0.5) * (intensity || 0.15);
      cam.position.y = oy + (Math.random() - 0.5) * (intensity || 0.08);
      c++; setTimeout(shake, 35);
    }
    shake();
  };

  /* --- Cleanup --- */
  Battle3DEngine.prototype.destroy = function () {
    if (this._raf) cancelAnimationFrame(this._raf);
    if (this.renderer && this.container) {
      this.container.removeChild(this.renderer.domElement);
      this.renderer.dispose();
    }
    this.ready = false;
  };

  /* ==================== EXPORT ==================== */
  window.Battle3D = new Battle3DEngine();
})();
