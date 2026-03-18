/**
 * 3D战斗系统主入口
 * 使用Three.js实现角色模型和技能特效
 */

class Battle3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Battle3D: Container not found');
            return;
        }
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.characters = new Map();
        this.effects = [];
        this.isInitialized = false;
        this.animationId = null;
        
        // 战斗配置
        this.config = {
            groundSize: 20,
            allyPositions: [
                { x: -4, z: 3 },
                { x: 0, z: 3 },
                { x: 4, z: 3 }
            ],
            enemyPositions: [
                { x: -4, z: -3 },
                { x: 0, z: -3 },
                { x: 4, z: -3 }
            ]
        };
        
        // 元素颜色映射
        this.elementColors = {
            fire: 0xff6b35,
            water: 0x4fc3f7,
            wind: 0x81c784,
            earth: 0xa1887f,
            light: 0xfff59d,
            dark: 0x7e57c2
        };
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadThreeJS();
            this.setupScene();
            this.setupLighting();
            this.setupGround();
            this.setupCamera();
            this.startAnimation();
            this.isInitialized = true;
            console.log('Battle3D: 初始化完成');
        } catch (error) {
            console.error('Battle3D: 初始化失败', error);
        }
    }
    
    async loadThreeJS() {
        // 检查Three.js是否已加载
        if (typeof THREE !== 'undefined') {
            return;
        }
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    setupScene() {
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);
        
        // 添加雾效果
        this.scene.fog = new THREE.Fog(0x1a1a2e, 15, 35);
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        this.container.appendChild(this.renderer.domElement);
        
        // 窗口大小调整
        window.addEventListener('resize', () => this.onResize());
    }
    
    setupLighting() {
        // 环境光
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        
        // 主光源（从上方）
        const mainLight = new THREE.DirectionalLight(0xffffff, 1);
        mainLight.position.set(0, 10, 5);
        mainLight.castShadow = true;
        mainLight.shadow.mapSize.width = 1024;
        mainLight.shadow.mapSize.height = 1024;
        mainLight.shadow.camera.near = 0.5;
        mainLight.shadow.camera.far = 50;
        this.scene.add(mainLight);
        
        // 补光（从侧面）
        const fillLight = new THREE.DirectionalLight(0x6699ff, 0.3);
        fillLight.position.set(-5, 5, 0);
        this.scene.add(fillLight);
        
        // 背光
        const backLight = new THREE.DirectionalLight(0xff9966, 0.2);
        backLight.position.set(0, 5, -10);
        this.scene.add(backLight);
    }
    
    setupGround() {
        // 地面
        const groundGeometry = new THREE.CircleGeometry(this.config.groundSize, 64);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x2a2a4a,
            roughness: 0.8,
            metalness: 0.2
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
        
        // 战斗区域标记
        this.addBattleZoneMarkers();
        
        // 环境粒子
        this.addAmbientParticles();
    }
    
    addBattleZoneMarkers() {
        // 我方区域标记（绿色）
        const allyZone = this.createZoneMarker(0x22c55e, 0, 3);
        this.scene.add(allyZone);
        
        // 敌方区域标记（红色）
        const enemyZone = this.createZoneMarker(0xef4444, 0, -3);
        this.scene.add(enemyZone);
    }
    
    createZoneMarker(color, x, z) {
        const group = new THREE.Group();
        
        // 圆形标记
        const ringGeometry = new THREE.RingGeometry(3.5, 4, 64);
        const ringMaterial = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });
        const ring = new THREE.Mesh(ringGeometry, ringMaterial);
        ring.rotation.x = -Math.PI / 2;
        ring.position.set(x, 0.01, z);
        group.add(ring);
        
        return group;
    }
    
    addAmbientParticles() {
        const particleCount = 100;
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 30;
            positions[i * 3 + 1] = Math.random() * 10;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
            
            colors[i * 3] = 0.8 + Math.random() * 0.2;
            colors[i * 3 + 1] = 0.8 + Math.random() * 0.2;
            colors[i * 3 + 2] = 1;
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const material = new THREE.PointsMaterial({
            size: 0.1,
            vertexColors: true,
            transparent: true,
            opacity: 0.6
        });
        
        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }
    
    setupCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
        this.camera.position.set(0, 12, 12);
        this.camera.lookAt(0, 0, 0);
    }
    
    onResize() {
        if (!this.container || !this.camera || !this.renderer) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    startAnimation() {
        const animate = () => {
            this.animationId = requestAnimationFrame(animate);
            
            // 更新粒子
            if (this.particles) {
                this.particles.rotation.y += 0.0005;
            }
            
            // 更新角色动画
            this.characters.forEach(char => {
                if (char.update) char.update();
            });
            
            // 更新特效
            this.updateEffects();
            
            this.renderer.render(this.scene, this.camera);
        };
        
        animate();
    }
    
    updateEffects() {
        for (let i = this.effects.length - 1; i >= 0; i--) {
            const effect = this.effects[i];
            if (effect.update) {
                effect.update();
            }
            
            if (effect.isDead && effect.isDead()) {
                this.scene.remove(effect.mesh);
                this.effects.splice(i, 1);
            }
        }
    }
    
    /**
     * 创建角色模型
     * @param {Object} data - 角色数据
     * @param {string} type - 'ally' 或 'enemy'
     * @param {number} index - 位置索引
     */
    createCharacter(data, type, index) {
        const positions = type === 'ally' ? this.config.allyPositions : this.config.enemyPositions;
        const position = positions[index] || { x: 0, z: 0 };
        
        // 根据角色职业创建模型
        const character = this.createCharacterModel(data);
        character.position.set(position.x, 0, position.z);
        
        // 敌方角色朝向相反
        if (type === 'enemy') {
            character.rotation.y = Math.PI;
        }
        
        this.scene.add(character);
        this.characters.set(`${type}_${index}`, character);
        
        return character;
    }
    
    /**
     * 根据角色数据创建低多边形模型
     */
    createCharacterModel(data) {
        const group = new THREE.Group();
        group.userData = { data: data };
        
        // 确定职业类型
        const profession = this.getProfessionType(data);
        const elementColor = this.elementColors[data.element] || 0xffffff;
        
        // 根据职业创建不同的模型
        switch (profession) {
            case 'warrior':
                this.createWarriorModel(group, data, elementColor);
                break;
            case 'mage':
                this.createMageModel(group, data, elementColor);
                break;
            case 'archer':
                this.createArcherModel(group, data, elementColor);
                break;
            case 'assassin':
                this.createAssassinModel(group, data, elementColor);
                break;
            case 'healer':
                this.createHealerModel(group, data, elementColor);
                break;
            default:
                this.createWarriorModel(group, data, elementColor);
        }
        
        // 添加元素光环
        this.addElementAura(group, elementColor);
        
        // 添加阴影
        this.addShadow(group);
        
        return group;
    }
    
    getProfessionType(data) {
        // 根据角色名称或属性判断职业
        const name = (data.name || '').toLowerCase();
        const skills = data.skills || [];
        
        if (name.includes('法师') || name.includes('mage') || name.includes('诸葛亮')) {
            return 'mage';
        }
        if (name.includes('弓') || name.includes('archer')) {
            return 'archer';
        }
        if (name.includes('刺客') || name.includes('assassin')) {
            return 'assassin';
        }
        if (name.includes('治疗') || name.includes('healer')) {
            return 'healer';
        }
        
        // 默认战士
        return 'warrior';
    }
    
    createWarriorModel(group, data, elementColor) {
        // 身体 - 立方体组合
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: elementColor,
            roughness: 0.6,
            metalness: 0.3
        });
        
        // 躯干
        const torso = new THREE.Mesh(
            new THREE.BoxGeometry(0.8, 1, 0.5),
            bodyMaterial
        );
        torso.position.y = 1.5;
        torso.castShadow = true;
        group.add(torso);
        
        // 头部
        const headMaterial = new THREE.MeshStandardMaterial({
            color: 0xffdbac,
            roughness: 0.8
        });
        const head = new THREE.Mesh(
            new THREE.SphereGeometry(0.35, 16, 16),
            headMaterial
        );
        head.position.y = 2.4;
        head.castShadow = true;
        group.add(head);
        
        // 头盔
        const helmet = new THREE.Mesh(
            new THREE.ConeGeometry(0.4, 0.4, 8),
            new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 })
        );
        helmet.position.y = 2.75;
        group.add(helmet);
        
        // 腿部
        const legMaterial = new THREE.MeshStandardMaterial({ color: 0x444444 });
        const leftLeg = new THREE.Mesh(
            new THREE.CylinderGeometry(0.15, 0.12, 0.8, 8),
            legMaterial
        );
        leftLeg.position.set(-0.2, 0.4, 0);
        leftLeg.castShadow = true;
        group.add(leftLeg);
        
        const rightLeg = leftLeg.clone();
        rightLeg.position.set(0.2, 0.4, 0);
        group.add(rightLeg);
        
        // 武器 - 剑
        const sword = this.createSword();
        sword.position.set(0.6, 1.5, 0);
        group.add(sword);
        group.userData.weapon = sword;
        
        // 盾牌
        const shield = this.createShield(elementColor);
        shield.position.set(-0.6, 1.5, 0.2);
        group.add(shield);
    }
    
    createMageModel(group, data, elementColor) {
        // 法师 - 长袍造型
        const robeMaterial = new THREE.MeshStandardMaterial({
            color: elementColor,
            roughness: 0.7
        });
        
        // 袍子（锥形）
        const robe = new THREE.Mesh(
            new THREE.ConeGeometry(0.6, 1.8, 8),
            robeMaterial
        );
        robe.position.y = 0.9;
        robe.castShadow = true;
        group.add(robe);
        
        // 上身
        const torso = new THREE.Mesh(
            new THREE.CylinderGeometry(0.3, 0.4, 0.8, 8),
            robeMaterial
        );
        torso.position.y = 1.9;
        torso.castShadow = true;
        group.add(torso);
        
        // 头部
        const head = new THREE.Mesh(
            new THREE.SphereGeometry(0.35, 16, 16),
            new THREE.MeshStandardMaterial({ color: 0xffdbac, roughness: 0.8 })
        );
        head.position.y = 2.55;
        head.castShadow = true;
        group.add(head);
        
        // 法师帽
        const hat = new THREE.Mesh(
            new THREE.ConeGeometry(0.5, 0.8, 8),
            new THREE.MeshStandardMaterial({ color: 0x2a2a4a, roughness: 0.6 })
        );
        hat.position.y = 3.1;
        group.add(hat);
        
        // 法杖
        const staff = this.createStaff(elementColor);
        staff.position.set(0.6, 1.5, 0);
        group.add(staff);
        group.userData.weapon = staff;
    }
    
    createArcherModel(group, data, elementColor) {
        // 弓箭手 - 轻甲造型
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x2d5a27,
            roughness: 0.6
        });
        
        // 躯干
        const torso = new THREE.Mesh(
            new THREE.BoxGeometry(0.7, 0.9, 0.4),
            bodyMaterial
        );
        torso.position.y = 1.5;
        torso.castShadow = true;
        group.add(torso);
        
        // 头部
        const head = new THREE.Mesh(
            new THREE.SphereGeometry(0.32, 16, 16),
            new THREE.MeshStandardMaterial({ color: 0xffdbac, roughness: 0.8 })
        );
        head.position.y = 2.3;
        head.castShadow = true;
        group.add(head);
        
        // 斗篷
        const cloak = new THREE.Mesh(
            new THREE.PlaneGeometry(0.8, 1.2),
            new THREE.MeshStandardMaterial({
                color: elementColor,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.8
            })
        );
        cloak.position.set(0, 1.4, -0.3);
        group.add(cloak);
        
        // 腿部
        const legMaterial = new THREE.MeshStandardMaterial({ color: 0x3d3d3d });
        const leftLeg = new THREE.Mesh(
            new THREE.CylinderGeometry(0.12, 0.1, 0.7, 8),
            legMaterial
        );
        leftLeg.position.set(-0.18, 0.35, 0);
        leftLeg.castShadow = true;
        group.add(leftLeg);
        
        const rightLeg = leftLeg.clone();
        rightLeg.position.set(0.18, 0.35, 0);
        group.add(rightLeg);
        
        // 弓
        const bow = this.createBow(elementColor);
        bow.position.set(0.5, 1.5, 0);
        group.add(bow);
        group.userData.weapon = bow;
    }
    
    createAssassinModel(group, data, elementColor) {
        // 刺客 - 紧身造型
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x1a1a1a,
            roughness: 0.4,
            metalness: 0.3
        });
        
        // 躯干
        const torso = new THREE.Mesh(
            new THREE.BoxGeometry(0.6, 0.9, 0.35),
            bodyMaterial
        );
        torso.position.y = 1.5;
        torso.castShadow = true;
        group.add(torso);
        
        // 头部 + 面罩
        const head = new THREE.Mesh(
            new THREE.SphereGeometry(0.3, 16, 16),
            new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 })
        );
        head.position.y = 2.25;
        head.castShadow = true;
        group.add(head);
        
        // 眼睛发光效果
        const eyeMaterial = new THREE.MeshBasicMaterial({ color: elementColor });
        const leftEye = new THREE.Mesh(
            new THREE.SphereGeometry(0.05, 8, 8),
            eyeMaterial
        );
        leftEye.position.set(-0.1, 2.28, 0.25);
        group.add(leftEye);
        
        const rightEye = leftEye.clone();
        rightEye.position.set(0.1, 2.28, 0.25);
        group.add(rightEye);
        
        // 腿部
        const legMaterial = new THREE.MeshStandardMaterial({ color: 0x1a1a1a });
        const leftLeg = new THREE.Mesh(
            new THREE.CylinderGeometry(0.1, 0.08, 0.7, 8),
            legMaterial
        );
        leftLeg.position.set(-0.15, 0.35, 0);
        leftLeg.castShadow = true;
        group.add(leftLeg);
        
        const rightLeg = leftLeg.clone();
        rightLeg.position.set(0.15, 0.35, 0);
        group.add(rightLeg);
        
        // 双刀
        const leftDagger = this.createDagger(elementColor);
        leftDagger.position.set(-0.5, 1.2, 0);
        leftDagger.rotation.z = -0.3;
        group.add(leftDagger);
        
        const rightDagger = this.createDagger(elementColor);
        rightDagger.position.set(0.5, 1.2, 0);
        rightDagger.rotation.z = 0.3;
        group.add(rightDagger);
        
        group.userData.weapon = [leftDagger, rightDagger];
    }
    
    createHealerModel(group, data, elementColor) {
        // 治疗者 - 圣洁造型
        const robeMaterial = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            roughness: 0.7
        });
        
        // 袍子
        const robe = new THREE.Mesh(
            new THREE.ConeGeometry(0.5, 1.6, 8),
            robeMaterial
        );
        robe.position.y = 0.8;
        robe.castShadow = true;
        group.add(robe);
        
        // 上身
        const torso = new THREE.Mesh(
            new THREE.CylinderGeometry(0.25, 0.35, 0.7, 8),
            robeMaterial
        );
        torso.position.y = 1.8;
        torso.castShadow = true;
        group.add(torso);
        
        // 头部
        const head = new THREE.Mesh(
            new THREE.SphereGeometry(0.3, 16, 16),
            new THREE.MeshStandardMaterial({ color: 0xffdbac, roughness: 0.8 })
        );
        head.position.y = 2.4;
        head.castShadow = true;
        group.add(head);
        
        // 光环
        const halo = new THREE.Mesh(
            new THREE.TorusGeometry(0.35, 0.03, 8, 32),
            new THREE.MeshBasicMaterial({ color: 0xffdd00 })
        );
        halo.position.y = 2.85;
        halo.rotation.x = Math.PI / 2;
        group.add(halo);
        group.userData.halo = halo;
        
        // 法球
        const orb = this.createOrb(elementColor);
        orb.position.set(0.5, 1.5, 0);
        group.add(orb);
        group.userData.weapon = orb;
    }
    
    // 武器创建方法
    createSword() {
        const group = new THREE.Group();
        
        // 剑身
        const blade = new THREE.Mesh(
            new THREE.BoxGeometry(0.08, 1.2, 0.02),
            new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.9, roughness: 0.2 })
        );
        blade.position.y = 0.6;
        group.add(blade);
        
        // 护手
        const guard = new THREE.Mesh(
            new THREE.BoxGeometry(0.3, 0.06, 0.06),
            new THREE.MeshStandardMaterial({ color: 0xffd700, metalness: 0.8 })
        );
        group.add(guard);
        
        // 剑柄
        const handle = new THREE.Mesh(
            new THREE.CylinderGeometry(0.04, 0.04, 0.25, 8),
            new THREE.MeshStandardMaterial({ color: 0x8b4513 })
        );
        handle.position.y = -0.15;
        group.add(handle);
        
        return group;
    }
    
    createShield(color) {
        const group = new THREE.Group();
        
        // 盾牌主体
        const shieldBody = new THREE.Mesh(
            new THREE.CircleGeometry(0.4, 32),
            new THREE.MeshStandardMaterial({ color: color, metalness: 0.5, roughness: 0.4 })
        );
        group.add(shieldBody);
        
        // 盾牌边框
        const rim = new THREE.Mesh(
            new THREE.TorusGeometry(0.4, 0.03, 8, 32),
            new THREE.MeshStandardMaterial({ color: 0xffd700, metalness: 0.8 })
        );
        group.add(rim);
        
        return group;
    }
    
    createStaff(color) {
        const group = new THREE.Group();
        
        // 法杖杆
        const rod = new THREE.Mesh(
            new THREE.CylinderGeometry(0.04, 0.05, 2, 8),
            new THREE.MeshStandardMaterial({ color: 0x8b4513, roughness: 0.6 })
        );
        group.add(rod);
        
        // 法杖顶部宝石
        const gem = new THREE.Mesh(
            new THREE.OctahedronGeometry(0.15, 0),
            new THREE.MeshBasicMaterial({ color: color })
        );
        gem.position.y = 1.1;
        group.add(gem);
        group.userData.gem = gem;
        
        return group;
    }
    
    createBow(color) {
        const group = new THREE.Group();
        
        // 弓身（弧形）
        const curve = new THREE.QuadraticBezierCurve3(
            new THREE.Vector3(-0.4, -0.8, 0),
            new THREE.Vector3(0, 0, 0.3),
            new THREE.Vector3(0.4, -0.8, 0)
        );
        const geometry = new THREE.TubeGeometry(curve, 20, 0.03, 8, false);
        const bowBody = new THREE.Mesh(
            geometry,
            new THREE.MeshStandardMaterial({ color: 0x8b4513, roughness: 0.5 })
        );
        group.add(bowBody);
        
        // 弓弦
        const stringGeom = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(-0.4, -0.8, 0),
            new THREE.Vector3(0, 0, -0.1),
            new THREE.Vector3(0.4, -0.8, 0)
        ]);
        const stringMat = new THREE.LineBasicMaterial({ color: 0xffffff });
        const bowString = new THREE.Line(stringGeom, stringMat);
        group.add(bowString);
        
        return group;
    }
    
    createDagger(color) {
        const group = new THREE.Group();
        
        // 刀身
        const blade = new THREE.Mesh(
            new THREE.ConeGeometry(0.05, 0.5, 4),
            new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.9, roughness: 0.2 })
        );
        blade.position.y = 0.25;
        group.add(blade);
        
        // 刀柄
        const handle = new THREE.Mesh(
            new THREE.CylinderGeometry(0.03, 0.03, 0.15, 8),
            new THREE.MeshStandardMaterial({ color: 0x1a1a1a })
        );
        handle.position.y = -0.05;
        group.add(handle);
        
        return group;
    }
    
    createOrb(color) {
        const group = new THREE.Group();
        
        // 法球
        const orb = new THREE.Mesh(
            new THREE.SphereGeometry(0.15, 16, 16),
            new THREE.MeshBasicMaterial({
                color: color,
                transparent: true,
                opacity: 0.8
            })
        );
        group.add(orb);
        
        // 光环
        const ring = new THREE.Mesh(
            new THREE.TorusGeometry(0.2, 0.02, 8, 32),
            new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.6 })
        );
        ring.rotation.x = Math.PI / 2;
        group.add(ring);
        
        group.userData.orb = orb;
        group.userData.ring = ring;
        
        return group;
    }
    
    addElementAura(group, color) {
        // 元素光环粒子
        const particleCount = 20;
        const positions = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            const angle = (i / particleCount) * Math.PI * 2;
            const radius = 0.5 + Math.random() * 0.3;
            positions[i * 3] = Math.cos(angle) * radius;
            positions[i * 3 + 1] = 1 + Math.random() * 1.5;
            positions[i * 3 + 2] = Math.sin(angle) * radius;
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: color,
            size: 0.08,
            transparent: true,
            opacity: 0.6
        });
        
        const aura = new THREE.Points(geometry, material);
        group.add(aura);
        group.userData.aura = aura;
    }
    
    addShadow(group) {
        const shadow = new THREE.Mesh(
            new THREE.CircleGeometry(0.5, 32),
            new THREE.MeshBasicMaterial({
                color: 0x000000,
                transparent: true,
                opacity: 0.3
            })
        );
        shadow.rotation.x = -Math.PI / 2;
        shadow.position.y = 0.01;
        group.add(shadow);
    }
    
    /**
     * 角色攻击动画
     */
    attackCharacter(type, index, targetIndex, isEnemy) {
        const character = this.characters.get(`${type}_${index}`);
        if (!character) return;
        
        // 攻击动画
        const startPos = character.position.clone();
        const targetPos = isEnemy 
            ? this.config.enemyPositions[targetIndex]
            : this.config.allyPositions[targetIndex];
        
        // 冲向目标
        const jumpForward = new TWEEN.Tween(character.position)
            .to({ x: targetPos.x * 0.5, z: targetPos.z * 0.7 }, 200)
            .easing(TWEEN.Easing.Quadratic.Out);
        
        // 返回原位
        const jumpBack = new TWEEN.Tween(character.position)
            .to({ x: startPos.x, z: startPos.z }, 200)
            .easing(TWEEN.Easing.Quadratic.In);
        
        // 武器挥动
        if (character.userData.weapon) {
            const weapon = character.userData.weapon;
            weapon.rotation.z = 0;
            const weaponSwing = new TWEEN.Tween(weapon.rotation)
                .to({ z: Math.PI * 0.5 }, 150)
                .easing(TWEEN.Easing.Quadratic.Out);
            const weaponReset = new TWEEN.Tween(weapon.rotation)
                .to({ z: 0 }, 150)
                .easing(TWEEN.Easing.Quadratic.In);
            weaponSwing.chain(weaponReset);
            weaponSwing.start();
        }
        
        jumpForward.chain(jumpBack);
        jumpForward.start();
        
        // 简单动画（不依赖TWEEN）
        this.simpleAttackAnimation(character, startPos, targetPos);
    }
    
    simpleAttackAnimation(character, startPos, targetPos) {
        // 简单的攻击动画，不依赖外部库
        const duration = 400;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            if (progress < 0.5) {
                // 前半段：冲向目标
                const p = progress * 2;
                character.position.x = startPos.x + (targetPos.x * 0.5 - startPos.x) * p;
                character.position.z = startPos.z + (targetPos.z * 0.7 - startPos.z) * p;
                
                // 武器挥动
                if (character.userData.weapon) {
                    character.userData.weapon.rotation.z = Math.PI * 0.5 * p;
                }
            } else {
                // 后半段：返回
                const p = (progress - 0.5) * 2;
                character.position.x = targetPos.x * 0.5 + (startPos.x - targetPos.x * 0.5) * p;
                character.position.z = targetPos.z * 0.7 + (startPos.z - targetPos.z * 0.7) * p;
                
                // 武器归位
                if (character.userData.weapon) {
                    character.userData.weapon.rotation.z = Math.PI * 0.5 * (1 - p);
                }
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
    
    /**
     * 创建技能特效
     */
    createSkillEffect(element, fromPos, toPos, onComplete) {
        const color = this.elementColors[element] || 0xffffff;
        
        // 创建粒子弹道
        const particleCount = 50;
        const positions = new Float32Array(particleCount * 3);
        const velocities = [];
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = fromPos.x;
            positions[i * 3 + 1] = fromPos.y + 1.5;
            positions[i * 3 + 2] = fromPos.z;
            
            velocities.push({
                x: (toPos.x - fromPos.x) / 30,
                y: (1.5 + (toPos.y || 0)) / 30 + (Math.random() - 0.5) * 0.1,
                z: (toPos.z - fromPos.z) / 30
            });
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: color,
            size: 0.15,
            transparent: true,
            opacity: 0.8
        });
        
        const particles = new THREE.Points(geometry, material);
        this.scene.add(particles);
        
        // 动画
        const effect = {
            mesh: particles,
            velocities: velocities,
            life: 30,
            update: function() {
                const posAttr = this.mesh.geometry.attributes.position;
                for (let i = 0; i < particleCount; i++) {
                    posAttr.array[i * 3] += this.velocities[i].x;
                    posAttr.array[i * 3 + 1] += this.velocities[i].y;
                    posAttr.array[i * 3 + 2] += this.velocities[i].z;
                }
                posAttr.needsUpdate = true;
                this.life--;
            },
            isDead: function() {
                return this.life <= 0;
            }
        };
        
        this.effects.push(effect);
        
        // 延迟后创建爆炸效果
        setTimeout(() => {
            this.createExplosionEffect(toPos, color);
            if (onComplete) onComplete();
        }, 300);
    }
    
    /**
     * 创建爆炸特效
     */
    createExplosionEffect(position, color) {
        const particleCount = 100;
        const positions = new Float32Array(particleCount * 3);
        const velocities = [];
        
        const center = position || { x: 0, y: 0, z: 0 };
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = center.x;
            positions[i * 3 + 1] = 1.5;
            positions[i * 3 + 2] = center.z;
            
            // 随机方向爆炸
            const angle = Math.random() * Math.PI * 2;
            const speed = 0.1 + Math.random() * 0.2;
            velocities.push({
                x: Math.cos(angle) * speed,
                y: Math.random() * 0.2,
                z: Math.sin(angle) * speed
            });
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: color,
            size: 0.2,
            transparent: true,
            opacity: 1
        });
        
        const particles = new THREE.Points(geometry, material);
        this.scene.add(particles);
        
        const effect = {
            mesh: particles,
            velocities: velocities,
            life: 40,
            update: function() {
                const posAttr = this.mesh.geometry.attributes.position;
                for (let i = 0; i < particleCount; i++) {
                    posAttr.array[i * 3] += this.velocities[i].x;
                    posAttr.array[i * 3 + 1] += this.velocities[i].y;
                    this.velocities[i].y -= 0.01; // 重力
                    posAttr.array[i * 3 + 2] += this.velocities[i].z;
                }
                posAttr.needsUpdate = true;
                this.life--;
                this.mesh.material.opacity = this.life / 40;
            },
            isDead: function() {
                return this.life <= 0;
            }
        };
        
        this.effects.push(effect);
    }
    
    /**
     * 角色受击动画
     */
    hitCharacter(type, index) {
        const character = this.characters.get(`${type}_${index}`);
        if (!character) return;
        
        // 闪烁效果
        character.traverse((child) => {
            if (child.material && child.material.emissive) {
                const originalEmissive = child.material.emissive.getHex();
                child.material.emissive.setHex(0xff0000);
                setTimeout(() => {
                    child.material.emissive.setHex(originalEmissive);
                }, 100);
            }
        });
        
        // 震动效果
        const originalX = character.position.x;
        const shake = (count) => {
            if (count <= 0) return;
            character.position.x = originalX + (Math.random() - 0.5) * 0.2;
            setTimeout(() => {
                character.position.x = originalX;
                shake(count - 1);
            }, 50);
        };
        shake(4);
    }
    
    /**
     * 角色死亡动画
     */
    deathCharacter(type, index) {
        const character = this.characters.get(`${type}_${index}`);
        if (!character) return;
        
        // 淡出并下落
        const duration = 500;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 下落
            character.position.y = -progress * 0.5;
            
            // 淡出
            character.traverse((child) => {
                if (child.material) {
                    child.material.transparent = true;
                    child.material.opacity = 1 - progress;
                }
            });
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.scene.remove(character);
                this.characters.delete(`${type}_${index}`);
            }
        };
        
        animate();
    }
    
    /**
     * 显示伤害数字
     */
    showDamageNumber(type, index, damage, isHeal = false) {
        const character = this.characters.get(`${type}_${index}`);
        if (!character) return;
        
        const position = character.position.clone();
        position.y += 3;
        
        // 创建精灵文字
        const canvas = document.createElement('canvas');
        canvas.width = 128;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');
        
        ctx.fillStyle = isHeal ? '#22c55e' : '#ef4444';
        ctx.font = 'bold 48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText((isHeal ? '+' : '-') + damage, 64, 48);
        
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ 
            map: texture, 
            transparent: true 
        });
        const sprite = new THREE.Sprite(material);
        sprite.position.copy(position);
        sprite.scale.set(1, 0.5, 1);
        
        this.scene.add(sprite);
        
        // 上浮动画
        const startY = position.y;
        const duration = 800;
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            sprite.position.y = startY + progress * 1.5;
            sprite.material.opacity = 1 - progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.scene.remove(sprite);
            }
        };
        
        animate();
    }
    
    /**
     * 清理资源
     */
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        // 清理场景
        this.characters.forEach(char => {
            this.scene.remove(char);
        });
        this.characters.clear();
        
        this.effects.forEach(effect => {
            this.scene.remove(effect.mesh);
        });
        this.effects = [];
        
        // 移除渲染器
        if (this.renderer) {
            this.container.removeChild(this.renderer.domElement);
            this.renderer.dispose();
        }
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Battle3D;
}
