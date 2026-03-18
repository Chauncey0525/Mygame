/**
 * 技能特效系统
 * 实现六种元素的技能特效
 */

class SkillEffectFactory {
    constructor(battle3D) {
        this.battle3D = battle3D;
        
        // 元素配置
        this.elementConfig = {
            fire: {
                color: 0xff6b35,
                secondaryColor: 0xff8c42,
                particleCount: 80,
                speed: 0.15,
                spread: 0.3
            },
            water: {
                color: 0x4fc3f7,
                secondaryColor: 0x81d4fa,
                particleCount: 60,
                speed: 0.12,
                spread: 0.4
            },
            wind: {
                color: 0x81c784,
                secondaryColor: 0xa5d6a7,
                particleCount: 100,
                speed: 0.2,
                spread: 0.5
            },
            earth: {
                color: 0xa1887f,
                secondaryColor: 0xbcaaa4,
                particleCount: 50,
                speed: 0.08,
                spread: 0.2
            },
            light: {
                color: 0xfff59d,
                secondaryColor: 0xffee58,
                particleCount: 70,
                speed: 0.18,
                spread: 0.35
            },
            dark: {
                color: 0x7e57c2,
                secondaryColor: 0x9575cd,
                particleCount: 90,
                speed: 0.14,
                spread: 0.45
            }
        };
    }
    
    /**
     * 创建技能特效
     * @param {string} element - 元素类型
     * @param {Object} startPos - 起始位置 {x, y, z}
     * @param {Object} endPos - 结束位置 {x, y, z}
     * @param {Function} onComplete - 完成回调
     */
    create(element, startPos, endPos, onComplete) {
        const config = this.elementConfig[element] || this.elementConfig.fire;
        
        switch (element) {
            case 'fire':
                this.createFireEffect(startPos, endPos, config, onComplete);
                break;
            case 'water':
                this.createWaterEffect(startPos, endPos, config, onComplete);
                break;
            case 'wind':
                this.createWindEffect(startPos, endPos, config, onComplete);
                break;
            case 'earth':
                this.createEarthEffect(startPos, endPos, config, onComplete);
                break;
            case 'light':
                this.createLightEffect(startPos, endPos, config, onComplete);
                break;
            case 'dark':
                this.createDarkEffect(startPos, endPos, config, onComplete);
                break;
            default:
                this.createFireEffect(startPos, endPos, config, onComplete);
        }
    }
    
    /**
     * 火元素特效 - 火焰喷射
     */
    createFireEffect(startPos, endPos, config, onComplete) {
        const scene = this.battle3D.scene;
        const particles = [];
        const group = new THREE.Group();
        
        // 创建火焰粒子
        for (let i = 0; i < config.particleCount; i++) {
            const size = 0.1 + Math.random() * 0.15;
            const geometry = new THREE.SphereGeometry(size, 8, 8);
            const material = new THREE.MeshBasicMaterial({
                color: Math.random() > 0.5 ? config.color : config.secondaryColor,
                transparent: true,
                opacity: 0.9
            });
            
            const particle = new THREE.Mesh(geometry, material);
            particle.position.set(
                startPos.x + (Math.random() - 0.5) * 0.5,
                1.5 + Math.random() * 0.5,
                startPos.z + (Math.random() - 0.5) * 0.5
            );
            
            // 目标方向速度
            const dx = endPos.x - startPos.x;
            const dz = endPos.z - startPos.z;
            const dist = Math.sqrt(dx * dx + dz * dz);
            
            particle.userData = {
                velocity: {
                    x: (dx / dist) * config.speed + (Math.random() - 0.5) * config.spread,
                    y: 0.02 + Math.random() * 0.05,
                    z: (dz / dist) * config.speed + (Math.random() - 0.5) * config.spread
                },
                life: 30 + Math.random() * 20,
                maxLife: 50
            };
            
            particles.push(particle);
            group.add(particle);
        }
        
        scene.add(group);
        
        // 动画
        const effect = {
            mesh: group,
            particles: particles,
            life: 50,
            update: function() {
                this.particles.forEach(p => {
                    p.position.x += p.userData.velocity.x;
                    p.position.y += p.userData.velocity.y;
                    p.position.z += p.userData.velocity.z;
                    p.userData.velocity.y -= 0.002; // 轻微下坠
                    
                    p.userData.life--;
                    p.material.opacity = p.userData.life / p.userData.maxLife;
                    
                    // 火焰颜色渐变
                    if (p.userData.life < p.userData.maxLife * 0.5) {
                        p.material.color.setHex(0xff4500);
                    }
                });
                this.life--;
            },
            isDead: function() {
                return this.life <= 0;
            }
        };
        
        this.battle3D.effects.push(effect);
        
        // 命中后创建爆炸
        setTimeout(() => {
            this.createFireExplosion(endPos, config);
            if (onComplete) onComplete();
        }, 350);
    }
    
    /**
     * 火焰爆炸
     */
    createFireExplosion(position, config) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 爆炸核心光球
        const coreGeometry = new THREE.SphereGeometry(0.5, 16, 16);
        const coreMaterial = new THREE.MeshBasicMaterial({
            color: config.color,
            transparent: true,
            opacity: 0.9
        });
        const core = new THREE.Mesh(coreGeometry, coreMaterial);
        core.position.set(position.x, 1.5, position.z);
        group.add(core);
        
        // 爆炸粒子
        const particleCount = 60;
        for (let i = 0; i < particleCount; i++) {
            const size = 0.05 + Math.random() * 0.1;
            const geometry = new THREE.SphereGeometry(size, 8, 8);
            const material = new THREE.MeshBasicMaterial({
                color: Math.random() > 0.3 ? config.color : 0xff4500,
                transparent: true,
                opacity: 0.8
            });
            
            const particle = new THREE.Mesh(geometry, material);
            particle.position.set(position.x, 1.5, position.z);
            
            const angle = Math.random() * Math.PI * 2;
            const speed = 0.1 + Math.random() * 0.15;
            
            particle.userData = {
                velocity: {
                    x: Math.cos(angle) * speed,
                    y: 0.1 + Math.random() * 0.15,
                    z: Math.sin(angle) * speed
                },
                life: 30 + Math.random() * 20
            };
            
            group.add(particle);
        }
        
        scene.add(group);
        
        // 动画
        let frame = 0;
        const animate = () => {
            frame++;
            
            // 核心扩散并淡出
            core.scale.multiplyScalar(1.05);
            core.material.opacity = Math.max(0, 0.9 - frame * 0.03);
            
            // 粒子扩散
            group.children.forEach((child, i) => {
                if (i === 0) return; // 跳过核心
                if (child.userData.velocity) {
                    child.position.x += child.userData.velocity.x;
                    child.position.y += child.userData.velocity.y;
                    child.position.z += child.userData.velocity.z;
                    child.userData.velocity.y -= 0.005;
                    child.material.opacity *= 0.95;
                }
            });
            
            if (frame < 40) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
            }
        };
        
        animate();
    }
    
    /**
     * 水元素特效 - 水流冲击
     */
    createWaterEffect(startPos, endPos, config, onComplete) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 创建水流粒子
        for (let i = 0; i < config.particleCount; i++) {
            const size = 0.08 + Math.random() * 0.1;
            const geometry = new THREE.SphereGeometry(size, 8, 8);
            const material = new THREE.MeshBasicMaterial({
                color: config.color,
                transparent: true,
                opacity: 0.7
            });
            
            const particle = new THREE.Mesh(geometry, material);
            particle.position.set(
                startPos.x + (Math.random() - 0.5) * 0.8,
                1.2 + Math.random() * 0.6,
                startPos.z + (Math.random() - 0.5) * 0.8
            );
            
            const dx = endPos.x - startPos.x;
            const dz = endPos.z - startPos.z;
            const dist = Math.sqrt(dx * dx + dz * dz);
            
            particle.userData = {
                velocity: {
                    x: (dx / dist) * config.speed,
                    y: 0,
                    z: (dz / dist) * config.speed
                },
                life: 35
            };
            
            group.add(particle);
        }
        
        scene.add(group);
        
        const effect = {
            mesh: group,
            life: 40,
            update: function() {
                group.children.forEach(p => {
                    if (p.userData.velocity) {
                        p.position.x += p.userData.velocity.x;
                        p.position.z += p.userData.velocity.z;
                        p.userData.life--;
                        p.material.opacity = Math.min(0.7, p.userData.life / 35);
                    }
                });
                this.life--;
            },
            isDead: function() {
                return this.life <= 0;
            }
        };
        
        this.battle3D.effects.push(effect);
        
        setTimeout(() => {
            this.createWaterSplash(endPos, config);
            if (onComplete) onComplete();
        }, 350);
    }
    
    /**
     * 水花溅射
     */
    createWaterSplash(position, config) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 水波纹
        const ring = new THREE.Mesh(
            new THREE.RingGeometry(0.1, 0.2, 32),
            new THREE.MeshBasicMaterial({
                color: config.color,
                transparent: true,
                opacity: 0.8,
                side: THREE.DoubleSide
            })
        );
        ring.rotation.x = -Math.PI / 2;
        ring.position.set(position.x, 0.1, position.z);
        group.add(ring);
        
        // 溅射粒子
        for (let i = 0; i < 30; i++) {
            const drop = new THREE.Mesh(
                new THREE.SphereGeometry(0.05, 8, 8),
                new THREE.MeshBasicMaterial({
                    color: config.color,
                    transparent: true,
                    opacity: 0.8
                })
            );
            
            drop.position.set(position.x, 1.5, position.z);
            const angle = Math.random() * Math.PI * 2;
            const speed = 0.05 + Math.random() * 0.1;
            
            drop.userData = {
                vx: Math.cos(angle) * speed,
                vy: 0.15 + Math.random() * 0.1,
                vz: Math.sin(angle) * speed
            };
            
            group.add(drop);
        }
        
        scene.add(group);
        
        let frame = 0;
        const animate = () => {
            frame++;
            
            // 波纹扩散
            ring.scale.multiplyScalar(1.08);
            ring.material.opacity *= 0.95;
            
            // 水滴下落
            group.children.forEach((child, i) => {
                if (i === 0) return;
                if (child.userData) {
                    child.position.x += child.userData.vx;
                    child.position.y += child.userData.vy;
                    child.position.z += child.userData.vz;
                    child.userData.vy -= 0.01;
                    child.material.opacity *= 0.97;
                }
            });
            
            if (frame < 35) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
            }
        };
        
        animate();
    }
    
    /**
     * 风元素特效 - 龙卷风刃
     */
    createWindEffect(startPos, endPos, config, onComplete) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 创建风刃
        const bladeCount = 5;
        for (let i = 0; i < bladeCount; i++) {
            const blade = new THREE.Mesh(
                new THREE.PlaneGeometry(0.3, 0.8),
                new THREE.MeshBasicMaterial({
                    color: config.color,
                    transparent: true,
                    opacity: 0.6,
                    side: THREE.DoubleSide
                })
            );
            
            blade.position.set(startPos.x, 1.5 + i * 0.2, startPos.z);
            blade.userData = {
                angle: (i / bladeCount) * Math.PI * 2,
                speed: config.speed + i * 0.02,
                offset: i * 0.3
            };
            
            group.add(blade);
        }
        
        // 风粒子
        for (let i = 0; i < config.particleCount; i++) {
            const particle = new THREE.Mesh(
                new THREE.SphereGeometry(0.03 + Math.random() * 0.05, 8, 8),
                new THREE.MeshBasicMaterial({
                    color: config.secondaryColor,
                    transparent: true,
                    opacity: 0.5
                })
            );
            
            particle.position.set(
                startPos.x + (Math.random() - 0.5) * 2,
                1 + Math.random() * 2,
                startPos.z + (Math.random() - 0.5) * 2
            );
            
            particle.userData = {
                angle: Math.random() * Math.PI * 2,
                radius: 0.5 + Math.random() * 1,
                speed: 0.1 + Math.random() * 0.1,
                life: 40
            };
            
            group.add(particle);
        }
        
        scene.add(group);
        
        // 动画
        const dx = endPos.x - startPos.x;
        const dz = endPos.z - startPos.z;
        const dist = Math.sqrt(dx * dx + dz * dz);
        
        let progress = 0;
        const animate = () => {
            progress += 0.03;
            
            // 移动整体
            const currentX = startPos.x + (dx / dist) * dist * progress;
            const currentZ = startPos.z + (dz / dist) * dist * progress;
            
            group.children.forEach((child, i) => {
                if (i < bladeCount) {
                    // 风刃旋转
                    child.position.x = currentX + Math.cos(child.userData.angle + progress * 10) * 0.5;
                    child.position.z = currentZ + Math.sin(child.userData.angle + progress * 10) * 0.5;
                    child.rotation.z = progress * 10 + child.userData.angle;
                    child.material.opacity = 0.6 * (1 - progress);
                } else if (child.userData.life !== undefined) {
                    // 粒子螺旋
                    child.userData.angle += child.userData.speed;
                    child.position.x = currentX + Math.cos(child.userData.angle) * child.userData.radius;
                    child.position.z = currentZ + Math.sin(child.userData.angle) * child.userData.radius;
                    child.userData.life--;
                    child.material.opacity = child.userData.life / 40 * 0.5;
                }
            });
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
                this.createWindBurst(endPos, config);
                if (onComplete) onComplete();
            }
        };
        
        animate();
    }
    
    /**
     * 风暴爆发
     */
    createWindBurst(position, config) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 扩散的圆环
        for (let i = 0; i < 3; i++) {
            const ring = new THREE.Mesh(
                new THREE.RingGeometry(0.3, 0.4, 32),
                new THREE.MeshBasicMaterial({
                    color: config.color,
                    transparent: true,
                    opacity: 0.8,
                    side: THREE.DoubleSide
                })
            );
            ring.rotation.x = -Math.PI / 2;
            ring.position.set(position.x, 0.5 + i * 0.3, position.z);
            ring.userData = { delay: i * 5 };
            group.add(ring);
        }
        
        scene.add(group);
        
        let frame = 0;
        const animate = () => {
            frame++;
            
            group.children.forEach(ring => {
                if (frame > ring.userData.delay) {
                    ring.scale.multiplyScalar(1.1);
                    ring.material.opacity *= 0.95;
                }
            });
            
            if (frame < 25) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
            }
        };
        
        animate();
    }
    
    /**
     * 土元素特效 - 岩石崩裂
     */
    createEarthEffect(startPos, endPos, config, onComplete) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 创建岩石块
        const rockCount = 15;
        for (let i = 0; i < rockCount; i++) {
            const size = 0.15 + Math.random() * 0.2;
            const geometry = new THREE.DodecahedronGeometry(size, 0);
            const material = new THREE.MeshStandardMaterial({
                color: config.color,
                roughness: 0.9,
                flatShading: true
            });
            
            const rock = new THREE.Mesh(geometry, material);
            rock.position.set(
                endPos.x + (Math.random() - 0.5) * 1.5,
                -0.5 - Math.random() * 0.5,
                endPos.z + (Math.random() - 0.5) * 1.5
            );
            
            rock.userData = {
                targetY: 0.5 + Math.random() * 1.5,
                delay: Math.random() * 10,
                risen: false
            };
            
            group.add(rock);
        }
        
        scene.add(group);
        
        let frame = 0;
        const animate = () => {
            frame++;
            
            group.children.forEach(rock => {
                if (frame > rock.userData.delay && !rock.userData.risen) {
                    // 岩石升起
                    rock.position.y += 0.15;
                    rock.rotation.x += 0.1;
                    rock.rotation.z += 0.1;
                    
                    if (rock.position.y >= rock.userData.targetY) {
                        rock.userData.risen = true;
                    }
                }
                
                if (rock.userData.risen) {
                    // 下落
                    rock.position.y -= 0.02;
                    rock.rotation.x += 0.02;
                    rock.material.opacity = 1 - (frame - 30) / 20;
                }
            });
            
            if (frame < 50) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
                this.createEarthquake(endPos, config);
                if (onComplete) onComplete();
            }
        };
        
        animate();
    }
    
    /**
     * 地震效果
     */
    createEarthquake(position, config) {
        // 震动相机
        const camera = this.battle3D.camera;
        const originalPos = camera.position.clone();
        
        let frame = 0;
        const shake = () => {
            frame++;
            
            camera.position.x = originalPos.x + (Math.random() - 0.5) * 0.1;
            camera.position.y = originalPos.y + (Math.random() - 0.5) * 0.05;
            
            if (frame < 10) {
                requestAnimationFrame(shake);
            } else {
                camera.position.copy(originalPos);
            }
        };
        
        shake();
    }
    
    /**
     * 光元素特效 - 圣光射线
     */
    createLightEffect(startPos, endPos, config, onComplete) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 光束
        const beamGeometry = new THREE.CylinderGeometry(0.05, 0.3, 8, 8);
        const beamMaterial = new THREE.MeshBasicMaterial({
            color: config.color,
            transparent: true,
            opacity: 0.8
        });
        const beam = new THREE.Mesh(beamGeometry, beamMaterial);
        beam.position.set(endPos.x, 6, endPos.z);
        beam.rotation.x = Math.PI;
        group.add(beam);
        
        // 光环
        for (let i = 0; i < 5; i++) {
            const ring = new THREE.Mesh(
                new THREE.TorusGeometry(0.3 + i * 0.2, 0.05, 8, 32),
                new THREE.MeshBasicMaterial({
                    color: config.secondaryColor,
                    transparent: true,
                    opacity: 0.6
                })
            );
            ring.position.set(endPos.x, 0.5 + i * 1.5, endPos.z);
            ring.userData = { speed: 0.05 + i * 0.02 };
            group.add(ring);
        }
        
        // 光粒子
        for (let i = 0; i < config.particleCount; i++) {
            const particle = new THREE.Mesh(
                new THREE.SphereGeometry(0.05, 8, 8),
                new THREE.MeshBasicMaterial({
                    color: config.color,
                    transparent: true,
                    opacity: 0.9
                })
            );
            
            const angle = Math.random() * Math.PI * 2;
            const radius = 0.5 + Math.random() * 1;
            
            particle.position.set(
                endPos.x + Math.cos(angle) * radius,
                1 + Math.random() * 5,
                endPos.z + Math.sin(angle) * radius
            );
            
            particle.userData = {
                vy: -0.05 - Math.random() * 0.05,
                life: 30 + Math.random() * 20
            };
            
            group.add(particle);
        }
        
        scene.add(group);
        
        let frame = 0;
        const animate = () => {
            frame++;
            
            // 光束脉冲
            beam.scale.x = 1 + Math.sin(frame * 0.3) * 0.2;
            beam.scale.z = 1 + Math.sin(frame * 0.3) * 0.2;
            beam.material.opacity = 0.8 - frame * 0.01;
            
            // 光环旋转
            group.children.forEach((child, i) => {
                if (i > 0 && i < 6) {
                    child.rotation.z += child.userData.speed;
                    child.material.opacity *= 0.98;
                } else if (child.userData && child.userData.vy !== undefined) {
                    child.position.y += child.userData.vy;
                    child.userData.life--;
                    child.material.opacity = child.userData.life / 50;
                }
            });
            
            if (frame < 50) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
                if (onComplete) onComplete();
            }
        };
        
        animate();
    }
    
    /**
     * 暗元素特效 - 暗影吞噬
     */
    createDarkEffect(startPos, endPos, config, onComplete) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 暗影球
        const sphere = new THREE.Mesh(
            new THREE.SphereGeometry(0.5, 16, 16),
            new THREE.MeshBasicMaterial({
                color: config.color,
                transparent: true,
                opacity: 0.9
            })
        );
        sphere.position.set(startPos.x, 1.5, startPos.z);
        group.add(sphere);
        
        // 暗影触手
        const tentacleCount = 8;
        for (let i = 0; i < tentacleCount; i++) {
            const angle = (i / tentacleCount) * Math.PI * 2;
            const tentacle = new THREE.Mesh(
                new THREE.ConeGeometry(0.1, 1, 8),
                new THREE.MeshBasicMaterial({
                    color: config.secondaryColor,
                    transparent: true,
                    opacity: 0.7
                })
            );
            
            tentacle.position.set(
                startPos.x + Math.cos(angle) * 0.3,
                1.5,
                startPos.z + Math.sin(angle) * 0.3
            );
            tentacle.rotation.z = -Math.PI / 2;
            tentacle.rotation.y = angle;
            tentacle.userData = { angle: angle };
            
            group.add(tentacle);
        }
        
        scene.add(group);
        
        // 动画 - 移动到目标
        const dx = endPos.x - startPos.x;
        const dz = endPos.z - startPos.z;
        
        let progress = 0;
        const animate = () => {
            progress += 0.02;
            
            // 球体移动
            sphere.position.x = startPos.x + dx * progress;
            sphere.position.z = startPos.z + dz * progress;
            
            // 触手旋转
            group.children.forEach((child, i) => {
                if (i > 0) {
                    child.position.x = sphere.position.x + Math.cos(child.userData.angle + progress * 5) * 0.3;
                    child.position.z = sphere.position.z + Math.sin(child.userData.angle + progress * 5) * 0.3;
                }
            });
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.createDarkExplosion(endPos, config);
                scene.remove(group);
                if (onComplete) onComplete();
            }
        };
        
        animate();
    }
    
    /**
     * 暗影爆炸
     */
    createDarkExplosion(position, config) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 黑洞效果
        const hole = new THREE.Mesh(
            new THREE.SphereGeometry(1, 16, 16),
            new THREE.MeshBasicMaterial({
                color: 0x000000,
                transparent: true,
                opacity: 0.9
            })
        );
        hole.position.set(position.x, 1.5, position.z);
        group.add(hole);
        
        // 吸入粒子
        for (let i = 0; i < 50; i++) {
            const particle = new THREE.Mesh(
                new THREE.SphereGeometry(0.05, 8, 8),
                new THREE.MeshBasicMaterial({
                    color: config.secondaryColor,
                    transparent: true,
                    opacity: 0.8
                })
            );
            
            const angle = Math.random() * Math.PI * 2;
            const radius = 2 + Math.random() * 1;
            
            particle.position.set(
                position.x + Math.cos(angle) * radius,
                1 + Math.random() * 2,
                position.z + Math.sin(angle) * radius
            );
            
            particle.userData = {
                angle: angle,
                radius: radius,
                targetRadius: 0
            };
            
            group.add(particle);
        }
        
        scene.add(group);
        
        let frame = 0;
        const animate = () => {
            frame++;
            
            // 黑洞收缩
            if (frame < 20) {
                hole.scale.multiplyScalar(1.05);
            } else {
                hole.scale.multiplyScalar(0.95);
                hole.material.opacity *= 0.9;
            }
            
            // 粒子吸入
            group.children.forEach((child, i) => {
                if (i > 0 && child.userData) {
                    child.userData.radius *= 0.95;
                    child.position.x = position.x + Math.cos(child.userData.angle + frame * 0.1) * child.userData.radius;
                    child.position.z = position.z + Math.sin(child.userData.angle + frame * 0.1) * child.userData.radius;
                    child.material.opacity = child.userData.radius / 3;
                }
            });
            
            if (frame < 40) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
            }
        };
        
        animate();
    }
    
    /**
     * 治疗特效
     */
    createHealEffect(position, amount) {
        const scene = this.battle3D.scene;
        const group = new THREE.Group();
        
        // 上升的绿色光点
        for (let i = 0; i < 30; i++) {
            const particle = new THREE.Mesh(
                new THREE.SphereGeometry(0.05, 8, 8),
                new THREE.MeshBasicMaterial({
                    color: 0x22c55e,
                    transparent: true,
                    opacity: 0.8
                })
            );
            
            particle.position.set(
                position.x + (Math.random() - 0.5) * 1,
                0.5 + Math.random() * 0.5,
                position.z + (Math.random() - 0.5) * 1
            );
            
            particle.userData = {
                vy: 0.03 + Math.random() * 0.03,
                life: 40 + Math.random() * 20
            };
            
            group.add(particle);
        }
        
        // 十字光环
        const cross = new THREE.Group();
        
        const vBar = new THREE.Mesh(
            new THREE.PlaneGeometry(0.1, 0.8),
            new THREE.MeshBasicMaterial({
                color: 0x22c55e,
                transparent: true,
                opacity: 0.9,
                side: THREE.DoubleSide
            })
        );
        cross.add(vBar);
        
        const hBar = new THREE.Mesh(
            new THREE.PlaneGeometry(0.8, 0.1),
            new THREE.MeshBasicMaterial({
                color: 0x22c55e,
                transparent: true,
                opacity: 0.9,
                side: THREE.DoubleSide
            })
        );
        cross.add(hBar);
        
        cross.position.set(position.x, 2.5, position.z);
        cross.lookAt(this.battle3D.camera.position);
        group.add(cross);
        
        scene.add(group);
        
        let frame = 0;
        const animate = () => {
            frame++;
            
            group.children.forEach((child, i) => {
                if (i < group.children.length - 1) {
                    // 粒子上升
                    child.position.y += child.userData.vy;
                    child.userData.life--;
                    child.material.opacity = child.userData.life / 60;
                } else {
                    // 十字旋转并淡出
                    child.rotation.z += 0.05;
                    child.children.forEach(c => {
                        c.material.opacity *= 0.97;
                    });
                }
            });
            
            if (frame < 60) {
                requestAnimationFrame(animate);
            } else {
                scene.remove(group);
            }
        };
        
        animate();
        
        // 显示治疗数字
        this.battle3D.showDamageNumber('ally', 0, amount, true);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkillEffectFactory;
}
