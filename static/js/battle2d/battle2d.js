/**
 * 宝可梦风格2D战斗场景引擎
 * 实现角色立绘展示、技能特效、伤害飘字
 */

var Battle2D = (function() {
    var arena = null;
    var allies = [];
    var enemies = [];
    var battleMode = '3v3';
    var stageElement = 'neutral';
    var ready = false;
    var animSpeed = 1;
    
    // 元素颜色映射
    var ELEMENT_COLORS = {
        fire: '#ef4444',
        water: '#3b82f6',
        wind: '#22c55e',
        earth: '#f59e0b',
        light: '#fbbf24',
        dark: '#a855f7',
        neutral: '#94a3b8'
    };
    
    // 战斗背景映射
    var STAGE_BACKGROUNDS = {
        fire: 'radial-gradient(ellipse at center, #4a1515 0%, #2d1010 50%, #1a0808 100%)',
        water: 'radial-gradient(ellipse at center, #0c3d5e 0%, #082840 50%, #041520 100%)',
        wind: 'radial-gradient(ellipse at center, #1a4a2e 0%, #0f3520 50%, #081a10 100%)',
        earth: 'radial-gradient(ellipse at center, #4a3a15 0%, #352810 50%, #1a1408 100%)',
        light: 'radial-gradient(ellipse at center, #4a4020 0%, #353015 50%, #1a1808 100%)',
        dark: 'radial-gradient(ellipse at center, #2a154a 0%, #1a0f35 50%, #0a081a 100%)',
        neutral: 'radial-gradient(ellipse at center, #2a2a3e 0%, #1a1a2e 50%, #0a0a1a 100%)'
    };
    
    /**
     * 初始化战斗场景
     */
    function init(arenaId, allyData, enemyData, mode, element) {
        arena = document.getElementById(arenaId);
        if (!arena) {
            console.error('Battle arena not found:', arenaId);
            return;
        }
        
        allies = allyData;
        enemies = enemyData;
        battleMode = mode || '3v3';
        stageElement = element || 'neutral';
        ready = true;
        
        // 设置背景
        var bgEl = document.getElementById('battle-bg');
        if (bgEl) {
            bgEl.style.background = STAGE_BACKGROUNDS[stageElement] || STAGE_BACKGROUNDS.neutral;
        }
        
        console.log('Battle2D initialized:', { mode: battleMode, element: stageElement });
    }
    
    /**
     * 渲染所有角色
     */
    function renderAll() {
        renderEnemies();
        renderAllies();
    }
    
    /**
     * 渲染敌方角色
     */
    function renderEnemies() {
        var enemyArea = document.getElementById('enemy-area');
        if (!enemyArea) return;
        
        enemyArea.innerHTML = '';
        
        var row = document.createElement('div');
        row.className = 'enemy-row';
        
        enemies.forEach(function(enemy, index) {
            var unit = createEnemyUnit(enemy, index);
            row.appendChild(unit);
        });
        
        enemyArea.appendChild(row);
    }
    
    /**
     * 创建敌方角色单元
     */
    function createEnemyUnit(enemy, index) {
        var unit = document.createElement('div');
        unit.className = 'enemy-unit' + (enemy.currentHp <= 0 ? ' dead' : '');
        unit.id = 'enemy-unit-' + index;
        unit.onclick = function() { selectTarget('enemy', index); };
        
        var hpPercent = Math.max(0, (enemy.currentHp / enemy.maxHp) * 100);
        var hpClass = hpPercent > 50 ? 'high' : (hpPercent > 25 ? 'mid' : 'low');
        
        // 使用动态立绘（如果存在）
        var illustration = enemy.illustration || enemy.avatar;
        var isDynamic = illustration && illustration.includes('/dynamic/');
        
        // 根据HP状态设置动画类
        var animClass = 'breathe-idle';
        if (enemy.currentHp <= 0) {
            animClass = 'breathe-dead';
        } else if (hpPercent <= 20) {
            animClass = 'breathe-near-death';
        } else {
            // 根据元素添加光环
            animClass = 'breathe-idle element-' + (enemy.element || 'neutral');
        }
        
        unit.innerHTML = 
            '<div class="enemy-sprite ' + animClass + '" id="enemy-sprite-' + index + '">' +
                '<img src="' + illustration + '" alt="' + enemy.name + '" id="enemy-img-' + index + '" class="character-illustration' + (isDynamic ? ' dynamic-illustration' : '') + '">' +
            '</div>' +
            '<div class="enemy-info">' +
                '<div class="enemy-name">' + enemy.name + '</div>' +
                '<div class="enemy-hp-bar">' +
                    '<div class="enemy-hp-fill ' + hpClass + '" id="enemy-hp-fill-' + index + '" style="width:' + hpPercent + '%"></div>' +
                '</div>' +
                '<div class="enemy-hp-text" id="enemy-hp-text-' + index + '">' + 
                    Math.floor(enemy.currentHp) + '/' + enemy.maxHp + 
                '</div>' +
            '</div>';
        
        return unit;
    }
    
    /**
     * 渲染己方角色
     */
    function renderAllies() {
        var allyArea = document.getElementById('ally-area');
        if (!allyArea) return;
        
        allyArea.innerHTML = '';
        
        allies.forEach(function(ally, index) {
            var unit = createAllyUnit(ally, index);
            allyArea.appendChild(unit);
        });
    }
    
    /**
     * 创建己方角色单元
     */
    function createAllyUnit(ally, index) {
        var unit = document.createElement('div');
        unit.className = 'ally-unit' + (ally.currentHp <= 0 ? ' dead' : '');
        unit.id = 'ally-unit-' + index;
        
        var hpPercent = Math.max(0, (ally.currentHp / ally.maxHp) * 100);
        
        // 使用动态立绘（如果存在）
        var illustration = ally.illustration || ally.avatar;
        var isDynamic = illustration && illustration.includes('/dynamic/');
        
        // 根据HP状态设置动画类
        var animClass = 'breathe-idle';
        if (ally.currentHp <= 0) {
            animClass = 'breathe-dead';
        } else if (hpPercent <= 20) {
            animClass = 'breathe-near-death';
        } else {
            // 根据元素添加光环
            animClass = 'breathe-idle element-' + (ally.element || 'neutral');
        }
        
        unit.innerHTML = 
            '<div class="ally-sprite ' + animClass + '" id="ally-sprite-' + index + '">' +
                '<img src="' + illustration + '" alt="' + ally.name + '" id="ally-img-' + index + '" class="character-illustration' + (isDynamic ? ' dynamic-illustration' : '') + '">' +
            '</div>' +
            '<div class="ally-info">' +
                '<div class="ally-name">' + ally.name + '</div>' +
                '<div class="ally-hp-bar">' +
                    '<div class="ally-hp-fill" id="ally-hp-fill-' + index + '" style="width:' + hpPercent + '%"></div>' +
                '</div>' +
                '<div class="ally-hp-text" id="ally-hp-text-' + index + '">' + 
                    Math.floor(ally.currentHp) + '/' + ally.maxHp + 
                '</div>' +
            '</div>';
        
        return unit;
    }
    
    /**
     * 选择目标
     */
    function selectTarget(side, index) {
        if (side === 'enemy') {
            // 移除之前的选中状态
            document.querySelectorAll('.enemy-unit.selected').forEach(function(el) {
                el.classList.remove('selected');
            });
            
            // 添加新的选中状态
            var unit = document.getElementById('enemy-unit-' + index);
            if (unit) {
                unit.classList.add('selected');
            }
        }
    }
    
    /**
     * 高亮角色
     */
    function highlight(side, index) {
        if (side === 'ally') {
            document.querySelectorAll('.ally-unit.active').forEach(function(el) {
                el.classList.remove('active');
            });
            
            var unit = document.getElementById('ally-unit-' + index);
            if (unit) {
                unit.classList.add('active');
            }
        }
    }
    
    /**
     * 更新血条
     */
    function updateHp(side, index, percent) {
        var fillEl, textEl, entity;
        
        if (side === 'enemy') {
            fillEl = document.getElementById('enemy-hp-fill-' + index);
            textEl = document.getElementById('enemy-hp-text-' + index);
            entity = enemies[index];
            
            if (fillEl) {
                var hpClass = percent > 50 ? 'high' : (percent > 25 ? 'mid' : 'low');
                fillEl.className = 'enemy-hp-fill ' + hpClass;
                fillEl.style.width = (percent * 100) + '%';
            }
        } else {
            fillEl = document.getElementById('ally-hp-fill-' + index);
            textEl = document.getElementById('ally-hp-text-' + index);
            entity = allies[index];
            
            if (fillEl) {
                fillEl.style.width = (percent * 100) + '%';
            }
        }
        
        if (textEl && entity) {
            textEl.textContent = Math.floor(entity.currentHp) + '/' + entity.maxHp;
        }
        
        // 更新死亡状态
        if (percent <= 0) {
            var unit = document.getElementById(side + '-unit-' + index);
            if (unit) {
                unit.classList.add('dead');
            }
        }
    }
    
    /**
     * 播放攻击动画
     */
    function playAttack(attackerSide, attackerIndex, targetSide, targetIndex) {
        return new Promise(function(resolve) {
            var attackerUnit = document.getElementById(attackerSide + '-unit-' + attackerIndex);
            if (attackerUnit) {
                attackerUnit.classList.add('attacking');
                setTimeout(function() {
                    attackerUnit.classList.remove('attacking');
                    resolve();
                }, getDelay(400));
            } else {
                resolve();
            }
        });
    }
    
    /**
     * 播放受击动画
     */
    function playHit(side, index) {
        var unit = document.getElementById(side + '-unit-' + index);
        if (unit) {
            unit.classList.add('hit');
            setTimeout(function() {
                unit.classList.remove('hit');
            }, getDelay(300));
        }
    }
    
    /**
     * 显示伤害数字
     */
    function showDamage(side, index, damage, isHeal, isCrit) {
        var sprite = document.getElementById(side + '-sprite-' + index);
        if (!sprite) return;
        
        var rect = sprite.getBoundingClientRect();
        var arenaRect = arena.getBoundingClientRect();
        
        var floater = document.createElement('div');
        floater.className = 'damage-float' + (isCrit ? ' critical' : '');
        if (isHeal) {
            floater.classList.add('heal');
            floater.textContent = '+' + damage;
        } else {
            floater.classList.add('physical');
            floater.textContent = damage;
            if (isCrit) {
                floater.textContent = damage + '!';
            }
        }
        
        floater.style.left = (rect.left - arenaRect.left + rect.width / 2) + 'px';
        floater.style.top = (rect.top - arenaRect.top) + 'px';
        floater.style.fontSize = isCrit ? '1.5rem' : '1.2rem';
        
        arena.appendChild(floater);
        
        setTimeout(function() {
            floater.remove();
        }, getDelay(1000));
    }
    
    /**
     * 播放治疗动画
     */
    function playHeal(side, index) {
        // 治疗特效 - 绿色光芒
        showElementEffect('light', side, index);
    }
    
    /**
     * 播放死亡动画
     */
    function playDeath(side, index) {
        var unit = document.getElementById(side + '-unit-' + index);
        if (unit) {
            unit.style.transition = 'opacity 0.5s, transform 0.5s';
            unit.style.opacity = '0.3';
            unit.style.transform = 'scale(0.8)';
        }
    }
    
    /**
     * 播放技能特效
     */
    function playSkillEffect(element, attackerSide, attackerIndex, targetSide, targetIndex) {
        return new Promise(function(resolve) {
            var targetSprite = document.getElementById(targetSide + '-sprite-' + targetIndex);
            if (!targetSprite) {
                resolve();
                return;
            }
            
            var rect = targetSprite.getBoundingClientRect();
            var arenaRect = arena.getBoundingClientRect();
            
            // 创建元素特效
            var effect = document.createElement('div');
            effect.className = 'element-effect ' + (element || 'neutral');
            effect.style.left = (rect.left - arenaRect.left + rect.width / 2 - 100) + 'px';
            effect.style.top = (rect.top - arenaRect.top + rect.height / 2 - 100) + 'px';
            
            arena.appendChild(effect);
            
            // 闪光效果
            var flash = document.getElementById('effect-flash');
            if (flash) {
                flash.classList.add('active');
                setTimeout(function() {
                    flash.classList.remove('active');
                }, getDelay(150));
            }
            
            setTimeout(function() {
                effect.remove();
                resolve();
            }, getDelay(600));
        });
    }
    
    /**
     * 播放高级技能特效（根据角色ID和技能名称）
     * @param {string} characterId - 角色ID（如 'guan-yu', 'zhuge-liang'）
     * @param {string} skillName - 技能名称（如 '青龙偃月斩', '八卦阵'）
     * @param {string} attackerSide - 攻击方阵营 ('ally' 或 'enemy')
     * @param {number} attackerIndex - 攻击方索引
     * @param {string} targetSide - 目标方阵营
     * @param {number} targetIndex - 目标索引
     */
    function playAdvancedSkillEffect(characterId, skillName, attackerSide, attackerIndex, targetSide, targetIndex) {
        return new Promise(function(resolve) {
            if (!window.SkillEffects) {
                // 如果SkillEffects未加载，回退到基础特效
                var elem = getElementFromCharacterId(characterId);
                playSkillEffect(elem, attackerSide, attackerIndex, targetSide, targetIndex).then(resolve);
                return;
            }
            
            var effectConfig = SkillEffects.getSkillEffect(characterId, skillName);
            var targetSprite = document.getElementById(targetSide + '-sprite-' + targetIndex);
            
            if (!targetSprite) {
                resolve();
                return;
            }
            
            var rect = targetSprite.getBoundingClientRect();
            var arenaRect = arena.getBoundingClientRect();
            var centerX = rect.left - arenaRect.left + rect.width / 2;
            var centerY = rect.top - arenaRect.top + rect.height / 2;
            
            // 检查是否是觉醒技能
            var awakeningConfig = SkillEffects.getAwakeningEffect(skillName);
            if (awakeningConfig && awakeningConfig.id) {
                playAwakeningEffect(awakeningConfig, centerX, centerY, effectConfig).then(resolve);
                return;
            }
            
            // 创建特效容器
            var effectContainer = document.createElement('div');
            effectContainer.className = SkillEffects.getEffectCSSClass(effectConfig);
            effectContainer.style.setProperty('--effect-color', effectConfig.color);
            effectContainer.style.left = (centerX - 150) + 'px';
            effectContainer.style.top = (centerY - 150) + 'px';
            effectContainer.style.width = '300px';
            effectContainer.style.height = '300px';
            
            // 添加技能名称显示
            if (skillName && (effectConfig.intensity === 'ultimate' || effectConfig.intensity === 'awakening')) {
                var nameDisplay = document.createElement('div');
                nameDisplay.className = 'skill-name-display' + (effectConfig.intensity === 'ultimate' ? ' intensity-ultimate' : '');
                nameDisplay.textContent = skillName;
                nameDisplay.style.setProperty('--effect-color', effectConfig.color);
                nameDisplay.style.left = '50%';
                nameDisplay.style.top = '-60px';
                nameDisplay.style.transform = 'translateX(-50%)';
                effectContainer.appendChild(nameDisplay);
            }
            
            // 根据特效类型创建内容
            var effectContent = createEffectContent(effectConfig);
            if (effectContent) {
                effectContainer.innerHTML += effectContent;
            }
            
            // 添加粒子效果
            var particles = SkillEffects.generateElementParticles(effectConfig.element, effectConfig.intensity);
            particles.forEach(function(p) {
                var particle = document.createElement('div');
                particle.className = 'particle ' + effectConfig.element;
                particle.style.left = (centerX + p.x) + 'px';
                particle.style.top = (centerY + p.y) + 'px';
                particle.style.width = p.size + 'px';
                particle.style.height = p.size + 'px';
                particle.style.setProperty('--particle-vx', p.vx + 'px');
                particle.style.setProperty('--particle-vy', p.vy + 'px');
                particle.style.setProperty('--particle-life', p.life + 's');
                particle.style.background = p.color;
                arena.appendChild(particle);
                
                setTimeout(function() {
                    particle.remove();
                }, getDelay(p.life * 1000));
            });
            
            arena.appendChild(effectContainer);
            
            // 屏幕闪光效果
            if (effectConfig.screenFlash) {
                var flash = document.getElementById('effect-flash');
                if (flash) {
                    flash.classList.add('active');
                    setTimeout(function() {
                        flash.classList.remove('active');
                    }, getDelay(300));
                }
            }
            
            // 屏幕震动效果
            if (effectConfig.shake) {
                cameraShake(effectConfig.intensity === 'ultimate' ? 0.2 : 0.1);
            }
            
            // 清理特效
            var duration = SkillEffects.getEffectDuration(effectConfig, animSpeed);
            setTimeout(function() {
                effectContainer.remove();
                resolve();
            }, getDelay(duration));
        });
    }
    
    /**
     * 播放觉醒技能特效
     */
    function playAwakeningEffect(awakeningConfig, centerX, centerY, baseConfig) {
        return new Promise(function(resolve) {
            // 创建全屏遮罩
            var overlay = document.createElement('div');
            overlay.className = 'screen-effect-overlay darken';
            document.body.appendChild(overlay);
            
            // 创建觉醒特效容器
            var effectContainer = document.createElement('div');
            effectContainer.className = 'skill-effect effect-awakening';
            effectContainer.style.setProperty('--effect-color', awakeningConfig.color);
            
            // 创建觉醒特效内容
            var content = '<div class="awakening-container">';
            content += '<div class="awakening-bg"></div>';
            content += '<div class="awakening-circle"></div>';
            content += '</div>';
            effectContainer.innerHTML = content;
            
            // 添加特殊效果
            if (awakeningConfig.special) {
                effectContainer.classList.add('special-' + awakeningConfig.special);
            }
            
            document.body.appendChild(effectContainer);
            
            // 屏幕震动
            cameraShake(0.25);
            
            // 清理
            var duration = awakeningConfig.duration || 3000;
            setTimeout(function() {
                overlay.remove();
                effectContainer.remove();
                resolve();
            }, getDelay(duration));
        });
    }
    
    /**
     * 创建特效内容HTML
     */
    function createEffectContent(config) {
        var html = '';
        
        switch(config.type) {
            case 'slash':
            case 'dual_slash':
                html = '<div class="slash-container">';
                html += '<div class="slash-line"></div>';
                if (config.type === 'dual_slash') {
                    html += '<div class="slash-line second"></div>';
                }
                html += '</div>';
                break;
                
            case 'magic':
            case 'magic_aoe':
                html = '<div class="magic-container">';
                html += '<div class="magic-circle"></div>';
                if (config.aoe) {
                    html += '<div class="magic-circle outer"></div>';
                }
                html += '</div>';
                break;
                
            case 'projectile':
            case 'aoe_projectile':
                html = '<div class="projectile-container">';
                html += '<div class="arrow"></div>';
                if (config.intensity === 'ultimate') {
                    html += '<div class="arrow-trail"></div>';
                }
                html += '</div>';
                break;
                
            case 'heal':
            case 'heal_aoe':
                html = '<div class="heal-container">';
                html += '<div class="heal-ring"></div>';
                html += '<div class="heal-cross">+</div>';
                if (config.intensity === 'ultimate') {
                    html += '<div class="heal-ring outer"></div>';
                }
                html += '</div>';
                break;
                
            case 'buff':
            case 'team_buff':
                html = '<div class="buff-container">';
                html += '<div class="buff-aura"></div>';
                if (config.teamEffect) {
                    html += '<div class="buff-wave"></div>';
                }
                html += '</div>';
                break;
                
            case 'debuff':
            case 'debuff_aoe':
                html = '<div class="debuff-container">';
                html += '<div class="debuff-chains"></div>';
                if (config.aoe) {
                    html += '<div class="debuff-wave"></div>';
                }
                html += '</div>';
                break;
                
            case 'charge':
            case 'charge_aoe':
                html = '<div class="charge-container">';
                html += '<div class="charge-trail"></div>';
                html += '<div class="charge-impact"></div>';
                html += '</div>';
                break;
                
            case 'combo':
                var hits = config.hits || 3;
                html = '<div class="combo-container">';
                for (var i = 0; i < hits; i++) {
                    html += '<div class="combo-hit" style="animation-delay: ' + (i * 0.15) + 's"></div>';
                }
                html += '</div>';
                break;
                
            default:
                html = '<div class="magic-container"><div class="magic-circle"></div></div>';
        }
        
        return html;
    }
    
    /**
     * 根据角色ID获取默认元素
     */
    function getElementFromCharacterId(characterId) {
        var elementMap = {
            'miyamoto': 'wind',
            'viking-ragnar': 'fire',
            'robin-hood': 'wind',
            'guan-yu': 'fire',
            'hua-mulan': 'wind',
            'arthur': 'light',
            'cao-cao': 'dark',
            'cleopatra': 'water',
            'zhuge-liang': 'water',
            'joan-of-arc': 'light',
            'genghis-khan': 'fire'
        };
        return elementMap[characterId] || 'neutral';
    }
    
    /**
     * 显示元素特效
     */
    function showElementEffect(element, side, index) {
        var sprite = document.getElementById(side + '-sprite-' + index);
        if (!sprite) return;
        
        var rect = sprite.getBoundingClientRect();
        var arenaRect = arena.getBoundingClientRect();
        
        var effect = document.createElement('div');
        effect.className = 'element-effect ' + element;
        effect.style.left = (rect.left - arenaRect.left + rect.width / 2 - 100) + 'px';
        effect.style.top = (rect.top - arenaRect.top + rect.height / 2 - 100) + 'px';
        
        arena.appendChild(effect);
        
        setTimeout(function() {
            effect.remove();
        }, getDelay(600));
    }
    
    /**
     * 屏幕震动
     */
    function cameraShake(intensity) {
        if (!arena) return;
        
        var originalTransform = arena.style.transform || '';
        var shakeAmount = (intensity || 0.1) * 20;
        
        arena.style.transition = 'transform 0.05s';
        arena.style.transform = 'translateX(' + shakeAmount + 'px)';
        
        setTimeout(function() {
            arena.style.transform = 'translateX(' + (-shakeAmount) + 'px)';
        }, getDelay(50));
        
        setTimeout(function() {
            arena.style.transform = 'translateX(' + (shakeAmount / 2) + 'px)';
        }, getDelay(100));
        
        setTimeout(function() {
            arena.style.transform = originalTransform;
        }, getDelay(150));
    }
    
    /**
     * 获取动画延迟（根据速度倍率）
     */
    function getDelay(baseMs) {
        return Math.floor(baseMs / animSpeed);
    }
    
    // 公开API
    return {
        init: init,
        renderAll: renderAll,
        renderEnemies: renderEnemies,
        renderAllies: renderAllies,
        selectTarget: selectTarget,
        highlight: highlight,
        updateHp: updateHp,
        playAttack: playAttack,
        playHit: playHit,
        showDamage: showDamage,
        playHeal: playHeal,
        playDeath: playDeath,
        playSkillEffect: playSkillEffect,
        playAdvancedSkillEffect: playAdvancedSkillEffect,
        cameraShake: cameraShake,
        get ready() { return ready; },
        get animSpeed() { return animSpeed; },
        set animSpeed(v) { animSpeed = v; }
    };
})();

// 导出全局
window.Battle2D = Battle2D;
