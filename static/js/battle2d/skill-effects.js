/**
 * 技能特效配置系统
 * 为每个技能设计独特的视觉效果
 */

var SkillEffects = (function() {
    
    // ==================== 技能特效配置 ====================
    var SKILL_EFFECTS = {
        // ========== 普通角色技能 ==========
        'soldier': {
            '冲锋斩击': {
                type: 'slash',
                element: 'earth',
                animation: 'earth_slash',
                particles: 'rock_debris',
                sound: 'slash_heavy',
                duration: 600,
                intensity: 'normal',
                color: '#d4a574'
            },
            '坚守阵地': {
                type: 'buff',
                element: 'earth',
                animation: 'shield_earth',
                particles: 'dust_swirl',
                sound: 'shield_up',
                duration: 800,
                intensity: 'normal',
                color: '#8b7355'
            }
        },
        'archer': {
            '穿云箭': {
                type: 'projectile',
                element: 'flying',
                animation: 'arrow_wind',
                particles: 'wind_trail',
                sound: 'arrow_piercing',
                duration: 500,
                intensity: 'normal',
                color: '#90ee90',
                trail: true
            },
            '快速射击': {
                type: 'projectile',
                element: 'flying',
                animation: 'arrow_quick',
                particles: null,
                sound: 'arrow_quick',
                duration: 300,
                intensity: 'weak',
                color: '#98fb98'
            }
        },
        'mage-apprentice': {
            '水弹术': {
                type: 'magic',
                element: 'water',
                animation: 'water_ball',
                particles: 'water_splash',
                sound: 'water_splash',
                duration: 500,
                intensity: 'normal',
                color: '#00bfff'
            },
            '冰霜护盾': {
                type: 'buff',
                element: 'water',
                animation: 'ice_shield',
                particles: 'frost_crystals',
                sound: 'ice_form',
                duration: 800,
                intensity: 'normal',
                color: '#87ceeb'
            }
        },
        'cavalry': {
            '骑兵冲锋': {
                type: 'charge',
                element: 'fire',
                animation: 'cavalry_charge',
                particles: 'fire_trail',
                sound: 'horse_charge',
                duration: 700,
                intensity: 'strong',
                color: '#ff6b35',
                shake: true
            }
        },
        'pikeman': {
            '长矛突刺': {
                type: 'thrust',
                element: 'earth',
                animation: 'spear_thrust',
                particles: 'impact_dust',
                sound: 'spear_hit',
                duration: 400,
                intensity: 'normal',
                color: '#cd853f'
            },
            '盾墙': {
                type: 'buff',
                element: 'earth',
                animation: 'shield_wall',
                particles: 'dust_wave',
                sound: 'shield_wall',
                duration: 900,
                intensity: 'strong',
                color: '#8b4513'
            }
        },
        'healer-apprentice': {
            '治愈之光': {
                type: 'heal',
                element: 'light',
                animation: 'healing_light',
                particles: 'holy_particles',
                sound: 'heal_cast',
                duration: 800,
                intensity: 'normal',
                color: '#ffd700'
            }
        },
        
        // ========== 史诗角色技能 ==========
        'guan-yu': {
            '青龙偃月': {
                type: 'slash',
                element: 'fire',
                animation: 'dragon_blade',
                particles: 'fire_dragon',
                sound: 'dragon_slash',
                duration: 1000,
                intensity: 'ultimate',
                color: '#ff4500',
                shake: true,
                screenFlash: true,
                // 特殊效果：青龙刀光
                special: 'dragon_crescent'
            },
            '过五关斩六将': {
                type: 'combo',
                element: 'fire',
                animation: 'multi_slash',
                particles: 'fire_sparks',
                sound: 'combo_slash',
                duration: 800,
                intensity: 'strong',
                color: '#ff6347',
                hits: 3
            },
            '武圣之威': {
                type: 'buff',
                element: 'fire',
                animation: 'warrior_aura',
                particles: 'flame_aura',
                sound: 'power_up',
                duration: 1200,
                intensity: 'ultimate',
                color: '#dc143c',
                aura: true
            }
        },
        'hua-mulan': {
            '破阵斩将': {
                type: 'slash',
                element: 'flying',
                animation: 'wind_slash',
                particles: 'wind_blade',
                sound: 'wind_slash',
                duration: 700,
                intensity: 'strong',
                color: '#00ced1',
                special: 'wind_wave'
            },
            '木兰从军': {
                type: 'combo',
                element: 'flying',
                animation: 'quick_slash',
                particles: 'wind_trail',
                sound: 'quick_strike',
                duration: 600,
                intensity: 'normal',
                color: '#48d1cc',
                hits: 2
            },
            '代父从军': {
                type: 'buff',
                element: 'flying',
                animation: 'heroic_aura',
                particles: 'wind_swirl',
                sound: 'determination',
                duration: 1000,
                intensity: 'strong',
                color: '#20b2aa'
            }
        },
        'arthur': {
            '圣剑斩击': {
                type: 'slash',
                element: 'light',
                animation: 'holy_slash',
                particles: 'light_particles',
                sound: 'holy_blade',
                duration: 800,
                intensity: 'ultimate',
                color: '#ffd700',
                screenFlash: true,
                special: 'cross_slash'
            },
            '王者之剑': {
                type: 'magic',
                element: 'light',
                animation: 'excalibur_beam',
                particles: 'golden_light',
                sound: 'excalibur',
                duration: 1200,
                intensity: 'ultimate',
                color: '#ffec8b',
                beam: true,
                screenFlash: true
            },
            '骑士荣耀': {
                type: 'buff',
                element: 'light',
                animation: 'knight_blessing',
                particles: 'holy_light',
                sound: 'blessing',
                duration: 1500,
                intensity: 'ultimate',
                color: '#fffacd',
                aura: true,
                teamEffect: true
            }
        },
        'cao-cao': {
            '霸业之剑': {
                type: 'slash',
                element: 'dark',
                animation: 'dark_slash',
                particles: 'dark_energy',
                sound: 'dark_blade',
                duration: 700,
                intensity: 'strong',
                color: '#4b0082',
                special: 'dark_wave'
            },
            '奸雄之计': {
                type: 'debuff',
                element: 'dark',
                animation: 'shadow_trap',
                particles: 'dark_tendrils',
                sound: 'sinister',
                duration: 900,
                intensity: 'strong',
                color: '#2f0040'
            },
            '唯才是举': {
                type: 'buff',
                element: 'dark',
                animation: 'emperor_aura',
                particles: 'dark_aura',
                sound: 'power_surge',
                duration: 1200,
                intensity: 'ultimate',
                color: '#1a0033',
                aura: true
            }
        },
        
        // ========== 传说角色技能 ==========
        'zhuge-liang': {
            '八阵图': {
                type: 'magic',
                element: 'water',
                animation: 'bagua_formation',
                particles: 'water_vortex',
                sound: 'ancient_magic',
                duration: 1500,
                intensity: 'ultimate',
                color: '#1e90ff',
                special: 'bagua_circle',
                screenFlash: true,
                // 八卦阵特效
                summon: 'bagua_array'
            },
            '火烧连营': {
                type: 'magic_aoe',
                element: 'fire',
                animation: 'fire_storm',
                particles: 'fire_rain',
                sound: 'inferno',
                duration: 1800,
                intensity: 'ultimate',
                color: '#ff4500',
                aoe: true,
                shake: true,
                screenFlash: true,
                special: 'fire_ocean'
            },
            '空城计': {
                type: 'buff',
                element: 'flying',
                animation: 'strategist_calm',
                particles: 'mist_swirl',
                sound: 'mystical',
                duration: 1000,
                intensity: 'strong',
                color: '#4682b4',
                aura: true
            }
        },
        
        // ========== 稀有角色技能 ==========
        'miyamoto': {
            '二天一流': {
                type: 'dual_slash',
                element: 'flying',
                animation: 'dual_blade_strike',
                particles: 'wind_cross',
                sound: 'dual_blade',
                duration: 900,
                intensity: 'ultimate',
                color: '#c0c0c0',
                special: 'cross_slash',
                shake: true
            },
            '燕返': {
                type: 'combo',
                element: 'flying',
                animation: 'swallow_return',
                particles: 'wind_slash_triple',
                sound: 'swift_slash',
                duration: 600,
                intensity: 'strong',
                color: '#e0e0e0',
                hits: 3
            },
            '剑道极意': {
                type: 'buff',
                element: 'flying',
                animation: 'sword_master',
                particles: 'ki_aura',
                sound: 'focus',
                duration: 1200,
                intensity: 'ultimate',
                color: '#f0f0f0',
                aura: true
            }
        },
        
        // ========== 其他英雄技能 ==========
        'joan-of-arc': {
            '神圣审判': {
                type: 'magic',
                element: 'light',
                animation: 'divine_judgment',
                particles: 'holy_spear',
                sound: 'divine_strike',
                duration: 1000,
                intensity: 'ultimate',
                color: '#fff8dc',
                screenFlash: true
            }
        },
        'cleopatra': {
            '尼罗之泪': {
                type: 'magic',
                element: 'water',
                animation: 'nile_blessing',
                particles: 'water_heal',
                sound: 'water_magic',
                duration: 1000,
                intensity: 'strong',
                color: '#40e0d0'
            }
        },
        'robin-hood': {
            '精准射击': {
                type: 'projectile',
                element: 'flying',
                animation: 'precise_arrow',
                particles: 'wind_trail',
                sound: 'arrow_strike',
                duration: 500,
                intensity: 'strong',
                color: '#228b22'
            }
        },
        'genghis-khan': {
            '蒙古铁骑': {
                type: 'charge',
                element: 'fire',
                animation: 'mongol_charge',
                particles: 'dust_storm',
                sound: 'cavalry_charge',
                duration: 800,
                intensity: 'ultimate',
                color: '#8b0000',
                shake: true
            }
        },
        'viking-ragnar': {
            '维京狂暴': {
                type: 'buff',
                element: 'fire',
                animation: 'berserker_rage',
                particles: 'fire_aura',
                sound: 'berserk',
                duration: 1200,
                intensity: 'ultimate',
                color: '#ff4500',
                aura: true
            }
        }
    };
    
    // ==================== 默认特效配置 ====================
    var DEFAULT_EFFECT = {
        type: 'slash',
        element: 'neutral',
        animation: 'basic_attack',
        particles: null,
        sound: 'hit',
        duration: 400,
        intensity: 'normal',
        color: '#94a3b8'
    };
    
    // ==================== 特效生成器 ====================
    
    /**
     * 获取技能特效配置
     */
    function getSkillEffect(characterId, skillName) {
        if (SKILL_EFFECTS[characterId] && SKILL_EFFECTS[characterId][skillName]) {
            return SKILL_EFFECTS[characterId][skillName];
        }
        return DEFAULT_EFFECT;
    }
    
    /**
     * 根据元素生成粒子效果
     */
    function generateElementParticles(element, intensity) {
        var count = intensity === 'ultimate' ? 30 : (intensity === 'strong' ? 20 : 10);
        var particles = [];
        
        var elementColors = {
            fire: ['#ff4500', '#ff6347', '#ff7f50', '#ffa500'],
            water: ['#00bfff', '#1e90ff', '#4169e1', '#87ceeb'],
            wind: ['#90ee90', '#98fb98', '#00fa9a', '#00ced1'],
            earth: ['#cd853f', '#d2691e', '#8b4513', '#a0522d'],
            light: ['#ffd700', '#ffec8b', '#fffacd', '#fff8dc'],
            dark: ['#4b0082', '#8b008b', '#2f0040', '#1a0033'],
            neutral: ['#94a3b8', '#cbd5e1', '#e2e8f0', '#f1f5f9']
        };
        
        var colors = elementColors[element] || elementColors.neutral;
        
        for (var i = 0; i < count; i++) {
            particles.push({
                color: colors[Math.floor(Math.random() * colors.length)],
                size: Math.random() * 8 + 2,
                x: Math.random() * 100 - 50,
                y: Math.random() * 100 - 50,
                vx: (Math.random() - 0.5) * 10,
                vy: (Math.random() - 0.5) * 10,
                life: Math.random() * 0.5 + 0.5
            });
        }
        
        return particles;
    }
    
    /**
     * 生成特效CSS类名
     */
    function getEffectCSSClass(effect) {
        var classes = ['skill-effect'];
        classes.push('effect-' + effect.type);
        classes.push('element-' + effect.element);
        classes.push('intensity-' + effect.intensity);
        
        if (effect.special) {
            classes.push('special-' + effect.special);
        }
        if (effect.aura) {
            classes.push('has-aura');
        }
        if (effect.beam) {
            classes.push('has-beam');
        }
        if (effect.shake) {
            classes.push('has-shake');
        }
        if (effect.screenFlash) {
            classes.push('has-flash');
        }
        
        return classes.join(' ');
    }
    
    /**
     * 获取特效持续时间（考虑动画速度）
     */
    function getEffectDuration(effect, speedMultiplier) {
        speedMultiplier = speedMultiplier || 1;
        return Math.floor(effect.duration / speedMultiplier);
    }
    
    // ==================== 公开API ====================
    return {
        getSkillEffect: getSkillEffect,
        generateElementParticles: generateElementParticles,
        getEffectCSSClass: getEffectCSSClass,
        getEffectDuration: getEffectDuration,
        SKILL_EFFECTS: SKILL_EFFECTS,
        DEFAULT_EFFECT: DEFAULT_EFFECT
    };
})();

// 导出全局
window.SkillEffects = SkillEffects;
