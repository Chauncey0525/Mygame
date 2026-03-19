/**
 * 技能特效配置系统 - 完整版
 * 为每个技能设计独特的视觉效果
 * 包含11个角色专属技能 + 3个觉醒技能特效
 */

var SkillEffects = (function() {
    
    // ==================== 技能特效配置 ====================
    var SKILL_EFFECTS = {
        // ==================== 宫本武藏 - 剑圣/风属性 ====================
        'miyamoto': {
            '二天一流': {
                type: 'dual_slash',
                element: 'wind',
                animation: 'dual_blade_cross',
                particles: 'wind_slash',
                sound: 'dual_blade',
                duration: 800,
                intensity: 'strong',
                color: '#c0c0c0',
                special: 'cross_slash_wind',
                description: '双刀交叉斩击，风刃四散'
            },
            '无念无想': {
                type: 'buff',
                element: 'wind',
                animation: 'zen_meditation',
                particles: 'ki_aura_white',
                sound: 'power_up',
                duration: 1200,
                intensity: 'ultimate',
                color: '#f0f0f0',
                aura: true,
                special: 'zen_state',
                description: '进入无念境界，白色气劲环绕'
            },
            '最终之剑': {
                type: 'slash',
                element: 'wind',
                animation: 'ultimate_sword',
                particles: 'wind_devour',
                sound: 'ultimate_slash',
                duration: 1500,
                intensity: 'ultimate',
                color: '#e8e8e8',
                shake: true,
                screenFlash: true,
                special: 'sword_ultimate',
                description: '悟道后的终极一剑，风卷残云'
            }
        },

        // ==================== 维京战士拉格纳 - 火属性 ====================
        'viking-ragnar': {
            '维京冲锋': {
                type: 'charge',
                element: 'fire',
                animation: 'viking_rush',
                particles: 'fire_trail',
                sound: 'war_cry',
                duration: 700,
                intensity: 'strong',
                color: '#ff6b35',
                shake: true,
                special: 'axe_slam',
                description: '维京战士冲锋，火焰拖尾'
            },
            '狂战士之怒': {
                type: 'buff',
                element: 'fire',
                animation: 'berserker_rage',
                particles: 'fire_aura_intense',
                sound: 'berserk',
                duration: 1400,
                intensity: 'ultimate',
                color: '#ff4500',
                aura: true,
                special: 'rage_mode',
                description: '进入狂暴状态，烈焰包围全身'
            },
            '诸神黄昏': {
                type: 'magic_aoe',
                element: 'fire',
                animation: 'ragnarok',
                particles: 'meteor_rain',
                sound: 'apocalypse',
                duration: 2000,
                intensity: 'ultimate',
                color: '#ff2200',
                shake: true,
                screenFlash: true,
                aoe: true,
                special: 'ragnarok_doom',
                description: '末日降临，陨石坠落，火焰席卷战场'
            }
        },

        // ==================== 罗宾汉 - 风属性 ====================
        'robin-hood': {
            '精准射击': {
                type: 'projectile',
                element: 'wind',
                animation: 'precise_arrow',
                particles: 'wind_line',
                sound: 'arrow_perfect',
                duration: 500,
                intensity: 'strong',
                color: '#228b22',
                special: 'critical_shot',
                description: '必中一箭，绿色风痕'
            },
            '箭雨': {
                type: 'aoe_projectile',
                element: 'wind',
                animation: 'arrow_rain',
                particles: 'arrows_falling',
                sound: 'arrow_storm',
                duration: 1200,
                intensity: 'ultimate',
                color: '#32cd32',
                aoe: true,
                special: 'rain_of_arrows',
                description: '漫天箭雨从天而降'
            },
            '百步穿杨': {
                type: 'projectile',
                element: 'wind',
                animation: 'piercing_arrow',
                particles: 'piercing_wind',
                sound: 'arrow_pierce',
                duration: 600,
                intensity: 'ultimate',
                color: '#00ff00',
                beam: true,
                screenFlash: true,
                special: 'armor_pierce',
                description: '贯穿一切的绿色光束'
            }
        },

        // ==================== 关羽 - 火属性 ====================
        'guan-yu': {
            '青龙偃月斩': {
                type: 'slash',
                element: 'fire',
                animation: 'dragon_blade',
                particles: 'green_fire',
                sound: 'dragon_slash',
                duration: 900,
                intensity: 'strong',
                color: '#00ff88',
                special: 'green_dragon',
                description: '青龙偃月刀斩出青色火焰'
            },
            '过五关斩六将': {
                type: 'buff',
                element: 'fire',
                animation: 'warrior_spirit',
                particles: 'war_flame',
                sound: 'heroic',
                duration: 1000,
                intensity: 'strong',
                color: '#ff6347',
                aura: true,
                special: 'warrior_will',
                description: '战意燃烧，火焰环绕'
            },
            '忠义之魂': {
                type: 'team_buff',
                element: 'fire',
                animation: 'loyal_spirit',
                particles: 'red_flame_aura',
                sound: 'spirit_call',
                duration: 1200,
                intensity: 'strong',
                color: '#dc143c',
                teamEffect: true,
                special: 'loyalty_aura',
                description: '忠义之魂笼罩全队'
            },
            '武圣之威': {
                type: 'slash',
                element: 'fire',
                animation: 'war_god_strike',
                particles: 'golden_fire',
                sound: 'god_strike',
                duration: 1100,
                intensity: 'ultimate',
                color: '#ffd700',
                shake: true,
                special: 'war_god_slam',
                description: '武圣之力，金色火焰爆发'
            },
            '关公显圣': {
                type: 'magic_aoe',
                element: 'fire',
                animation: 'guan_gong_appear',
                particles: 'divine_fire_wave',
                sound: 'divine_appear',
                duration: 1500,
                intensity: 'ultimate',
                color: '#ff4500',
                aoe: true,
                shake: true,
                special: 'divine_sweep',
                description: '武圣显灵，神圣火焰横扫全场'
            }
        },

        // ==================== 花木兰 - 风属性 ====================
        'hua-mulan': {
            '从军斩': {
                type: 'slash',
                element: 'wind',
                animation: 'heroic_slash',
                particles: 'pink_petals',
                sound: 'swift_slash',
                duration: 600,
                intensity: 'normal',
                color: '#ff69b4',
                special: 'petal_slash',
                description: '英姿飒爽，粉色花瓣飞舞'
            },
            '替父从军': {
                type: 'buff',
                element: 'wind',
                animation: 'determination',
                particles: 'steady_wind',
                sound: 'resolve',
                duration: 900,
                intensity: 'normal',
                color: '#dda0dd',
                aura: true,
                special: 'resolve_aura',
                description: '坚定信念，紫色光环'
            },
            '花舞连斩': {
                type: 'combo',
                element: 'wind',
                animation: 'flower_dance',
                particles: 'flower_blade',
                sound: 'dance_slash',
                duration: 1000,
                intensity: 'strong',
                color: '#ff1493',
                hits: 5,
                special: 'petal_storm',
                description: '花瓣飞舞般的连斩'
            },
            '巾帼之怒': {
                type: 'magic_aoe',
                element: 'wind',
                animation: 'heroine_rage',
                particles: 'pink_wind_wave',
                sound: 'rage_release',
                duration: 1200,
                intensity: 'ultimate',
                color: '#ff69b4',
                aoe: true,
                special: 'heroine_burst',
                description: '巾帼不让须眉的爆发'
            },
            '木兰无双': {
                type: 'slash',
                element: 'wind',
                animation: 'mulan_ultimate',
                particles: 'cherry_blossom_storm',
                sound: 'ultimate_blade',
                duration: 1500,
                intensity: 'ultimate',
                color: '#ff1493',
                shake: true,
                screenFlash: true,
                special: 'sakura_ultimate',
                description: '樱花风暴般的终极一击'
            }
        },

        // ==================== 亚瑟王 - 光属性 ====================
        'arthur': {
            '誓约胜利之剑': {
                type: 'magic',
                element: 'light',
                animation: 'excalibur_slash',
                particles: 'golden_light',
                sound: 'holy_blade',
                duration: 900,
                intensity: 'strong',
                color: '#ffd700',
                special: 'excalibur_glow',
                description: '圣剑发出金色光芒'
            },
            '圆桌骑士': {
                type: 'team_buff',
                element: 'light',
                animation: 'knight_oath',
                particles: 'shield_light',
                sound: 'knight_pledge',
                duration: 1100,
                intensity: 'strong',
                color: '#f0e68c',
                teamEffect: true,
                special: 'round_table',
                description: '圆桌骑士之誓，全队护盾光环'
            },
            '圣剑光辉': {
                type: 'magic_aoe',
                element: 'light',
                animation: 'holy_burst',
                particles: 'light_explosion',
                sound: 'holy_explosion',
                duration: 1200,
                intensity: 'ultimate',
                color: '#fff8dc',
                aoe: true,
                screenFlash: true,
                special: 'light_judgment',
                description: '圣剑绽放，光芒四射'
            },
            '不列颠守护': {
                type: 'team_buff',
                element: 'light',
                animation: 'kingdom_guard',
                particles: 'golden_barrier',
                sound: 'protection',
                duration: 1300,
                intensity: 'ultimate',
                color: '#ffd700',
                teamEffect: true,
                aura: true,
                special: 'britannia_shield',
                description: '王者守护，金色屏障'
            },
            '王之军势': {
                type: 'magic_aoe',
                element: 'light',
                animation: 'army_of_kings',
                particles: 'army_phantom',
                sound: 'army_charge',
                duration: 1800,
                intensity: 'ultimate',
                color: '#ffec8b',
                aoe: true,
                shake: true,
                screenFlash: true,
                special: 'king_army',
                description: '王之军势，幻影骑士冲锋'
            }
        },

        // ==================== 曹操 - 暗属性 ====================
        'cao-cao': {
            '奸雄之刃': {
                type: 'slash',
                element: 'dark',
                animation: 'dark_blade',
                particles: 'shadow_slash',
                sound: 'sinister_blade',
                duration: 700,
                intensity: 'strong',
                color: '#4b0082',
                special: 'shadow_cut',
                description: '暗影缠绕的枭雄之刃'
            },
            '挟天子令诸侯': {
                type: 'debuff_aoe',
                element: 'dark',
                animation: 'emperor_decree',
                particles: 'dark_pressure',
                sound: 'decree',
                duration: 1000,
                intensity: 'strong',
                color: '#2f0040',
                aoe: true,
                special: 'royal_pressure',
                description: '帝王威压，暗紫色笼罩全场'
            },
            '乱世奸雄': {
                type: 'buff',
                element: 'dark',
                animation: 'warlord_awaken',
                particles: 'dark_power_surge',
                sound: 'power_up',
                duration: 1200,
                intensity: 'ultimate',
                color: '#1a0033',
                aura: true,
                special: 'warlord_power',
                description: '枭雄觉醒，暗黑力量涌动'
            },
            '魏武挥鞭': {
                type: 'slash_aoe',
                element: 'dark',
                animation: 'whip_strike',
                particles: 'dark_whip_wave',
                sound: 'whip_crack',
                duration: 1100,
                intensity: 'ultimate',
                color: '#4b0082',
                aoe: true,
                special: 'emperor_whip',
                description: '魏武帝挥鞭，暗影鞭影横扫'
            },
            '天下归心': {
                type: 'magic_aoe',
                element: 'dark',
                animation: 'world_domination',
                particles: 'dark_vortex',
                sound: 'domination',
                duration: 1600,
                intensity: 'ultimate',
                color: '#2f0040',
                aoe: true,
                shake: true,
                screenFlash: true,
                special: 'conquer_all',
                description: '天下归心，暗黑漩涡吞噬一切'
            }
        },

        // ==================== 克里奥帕特拉 - 水属性 ====================
        'cleopatra': {
            '尼罗河祝福': {
                type: 'heal',
                element: 'water',
                animation: 'nile_blessing',
                particles: 'water_droplet',
                sound: 'water_heal',
                duration: 800,
                intensity: 'normal',
                color: '#40e0d0',
                special: 'nile_water',
                description: '尼罗河水滴治愈'
            },
            '女王魅惑': {
                type: 'debuff',
                element: 'water',
                animation: 'queen_charm',
                particles: 'charm_heart',
                sound: 'charm',
                duration: 900,
                intensity: 'strong',
                color: '#da70d6',
                special: 'seduction',
                description: '女王魅惑，粉色心形粒子'
            },
            '王权之光': {
                type: 'team_buff',
                element: 'water',
                animation: 'royal_radiance',
                particles: 'golden_water',
                sound: 'royal_light',
                duration: 1100,
                intensity: 'strong',
                color: '#ffd700',
                teamEffect: true,
                special: 'queen_radiance',
                description: '王权之光，金色水波环绕全队'
            },
            '尼罗河之怒': {
                type: 'magic_aoe',
                element: 'water',
                animation: 'nile_flood',
                particles: 'water_tidal',
                sound: 'flood',
                duration: 1300,
                intensity: 'ultimate',
                color: '#00bfff',
                aoe: true,
                special: 'river_fury',
                description: '尼罗河泛滥，巨浪冲刷全场'
            },
            '永恒女王': {
                type: 'heal_aoe',
                element: 'water',
                animation: 'eternal_queen',
                particles: 'divine_water',
                sound: 'eternal',
                duration: 1500,
                intensity: 'ultimate',
                color: '#7fffd4',
                teamEffect: true,
                special: 'queen_eternal',
                description: '永恒女王，神圣之水治愈全队'
            }
        },

        // ==================== 诸葛亮 - 水属性(传说) ====================
        'zhuge-liang': {
            '八卦阵': {
                type: 'team_buff',
                element: 'water',
                animation: 'bagua_formation',
                particles: 'eight_trigram',
                sound: 'ancient_magic',
                duration: 1500,
                intensity: 'ultimate',
                color: '#1e90ff',
                teamEffect: true,
                special: 'bagua_circle',
                description: '八卦阵法，天干地支旋转'
            },
            '草船借箭': {
                type: 'magic_aoe',
                element: 'water',
                animation: 'arrow_borrow',
                particles: 'arrow_reflect',
                sound: 'tactic',
                duration: 1200,
                intensity: 'strong',
                color: '#4682b4',
                aoe: true,
                special: 'strategic_arrows',
                description: '草船借箭，箭矢反射'
            },
            '火烧赤壁': {
                type: 'magic_aoe',
                element: 'fire',
                animation: 'red_cliff_fire',
                particles: 'inferno_wave',
                sound: 'inferno',
                duration: 1800,
                intensity: 'ultimate',
                color: '#ff4500',
                aoe: true,
                shake: true,
                screenFlash: true,
                special: 'red_cliff_blaze',
                description: '赤壁之火，烈焰滔天'
            },
            '空城计': {
                type: 'buff',
                element: 'water',
                animation: 'empty_city',
                particles: 'mist_illusion',
                sound: 'mystical',
                duration: 1000,
                intensity: 'strong',
                color: '#87ceeb',
                aura: true,
                special: 'phantom_city',
                description: '空城计，幻雾弥漫'
            },
            '七星灯': {
                type: 'heal_aoe',
                element: 'water',
                animation: 'seven_stars',
                particles: 'star_lantern',
                sound: 'divine_light',
                duration: 1400,
                intensity: 'ultimate',
                color: '#e6e6fa',
                teamEffect: true,
                special: 'seven_star_lamp',
                description: '七星续命，星灯闪烁'
            }
        },

        // ==================== 圣女贞德 - 光属性(传说) ====================
        'joan-of-arc': {
            '圣女祈祷': {
                type: 'heal_aoe',
                element: 'light',
                animation: 'saint_prayer',
                particles: 'holy_dove',
                sound: 'prayer',
                duration: 1000,
                intensity: 'strong',
                color: '#fff8dc',
                teamEffect: true,
                special: 'divine_prayer',
                description: '圣女祈祷，白鸽飞舞'
            },
            '神启': {
                type: 'team_buff',
                element: 'light',
                animation: 'divine_revelation',
                particles: 'heaven_light',
                sound: 'revelation',
                duration: 1100,
                intensity: 'strong',
                color: '#ffd700',
                teamEffect: true,
                special: 'god_whisper',
                description: '神启，天光降临'
            },
            '圣旗飘扬': {
                type: 'team_buff',
                element: 'light',
                animation: 'holy_flag',
                particles: 'banner_light',
                sound: 'flag_wave',
                duration: 1300,
                intensity: 'ultimate',
                color: '#fffacd',
                teamEffect: true,
                special: 'sacred_banner',
                description: '圣旗飘扬，光芒四射'
            },
            '殉道之光': {
                type: 'heal',
                element: 'light',
                animation: 'martyr_light',
                particles: 'sacrifice_glow',
                sound: 'martyr',
                duration: 1000,
                intensity: 'ultimate',
                color: '#fffacd',
                special: 'martyrdom',
                description: '殉道之光，牺牲治愈'
            },
            '圣女降临': {
                type: 'magic_aoe',
                element: 'light',
                animation: 'saint_descent',
                particles: 'angel_feather',
                sound: 'angel',
                duration: 1600,
                intensity: 'ultimate',
                color: '#ffffff',
                aoe: true,
                shake: true,
                screenFlash: true,
                special: 'saint_appear',
                description: '圣女降临，天使羽毛飘落'
            }
        },

        // ==================== 成吉思汗 - 火属性(传说) ====================
        'genghis-khan': {
            '铁骑冲锋': {
                type: 'charge_aoe',
                element: 'fire',
                animation: 'cavalry_charge',
                particles: 'horse_hoof',
                sound: 'cavalry',
                duration: 1000,
                intensity: 'strong',
                color: '#8b0000',
                aoe: true,
                shake: true,
                special: 'iron_cavalry',
                description: '蒙古铁骑冲锋，地动山摇'
            },
            '草原之王': {
                type: 'buff',
                element: 'fire',
                animation: 'steppe_king',
                particles: 'steppe_wind',
                sound: 'king_power',
                duration: 1100,
                intensity: 'strong',
                color: '#cd5c5c',
                aura: true,
                special: 'grassland_lord',
                description: '草原之王，狂风环绕'
            },
            '万箭齐发': {
                type: 'aoe_projectile',
                element: 'fire',
                animation: 'arrow_volley',
                particles: 'fire_arrows',
                sound: 'arrow_storm',
                duration: 1200,
                intensity: 'ultimate',
                color: '#ff4500',
                aoe: true,
                special: 'ten_thousand_arrows',
                description: '万箭齐发，火箭如雨'
            },
            '征服者之威': {
                type: 'team_buff',
                element: 'fire',
                animation: 'conqueror_glory',
                particles: 'victory_flame',
                sound: 'conqueror',
                duration: 1300,
                intensity: 'ultimate',
                color: '#dc143c',
                teamEffect: true,
                special: 'conqueror_aura',
                description: '征服者之威，胜利之焰'
            },
            '蒙古铁骑': {
                type: 'charge_aoe',
                element: 'fire',
                animation: 'mongol_army',
                particles: 'war_horse_wave',
                sound: 'army_charge',
                duration: 1800,
                intensity: 'ultimate',
                color: '#8b0000',
                aoe: true,
                shake: true,
                screenFlash: true,
                special: 'mongol_onslaught',
                description: '蒙古铁骑万马奔腾'
            }
        }
    };

    // ==================== 觉醒技能特效配置 ====================
    var AWAKENING_EFFECTS = {
        // 诸葛亮 - 卧龙出山
        'zgl_awakening': {
            name: '卧龙出山',
            type: 'awakening',
            element: 'water',
            animation: 'dragon_emerge',
            particles: 'water_dragon',
            sound: 'dragon_roar',
            duration: 3000,
            intensity: 'awakening',
            color: '#1e90ff',
            aoe: true,
            shake: true,
            screenFlash: true,
            special: 'sleeping_dragon',
            phases: [
                { phase: 1, duration: 500, animation: 'sky_darken', description: '天空变暗' },
                { phase: 2, duration: 800, animation: 'water_dragon_rise', description: '水龙腾空' },
                { phase: 3, duration: 1000, animation: 'dragon_breath', description: '龙息冲击' },
                { phase: 4, duration: 700, animation: 'team_buff_glow', description: '全队增益' }
            ],
            description: '卧龙出山天地变色！水龙腾空，毁灭一切'
        },

        // 圣女贞德 - 奇迹之火
        'joan_awakening': {
            name: '奇迹之火',
            type: 'awakening',
            element: 'light',
            animation: 'miracle_fire',
            particles: 'holy_flame',
            sound: 'miracle',
            duration: 3500,
            intensity: 'awakening',
            color: '#ffffff',
            aoe: true,
            shake: true,
            screenFlash: true,
            special: 'miracle_blaze',
            phases: [
                { phase: 1, duration: 600, animation: 'heaven_open', description: '天堂之门打开' },
                { phase: 2, duration: 1000, animation: 'holy_fire_rain', description: '圣火降临' },
                { phase: 3, duration: 800, animation: 'full_heal', description: '完全治愈' },
                { phase: 4, duration: 1100, animation: 'divine_shield', description: '神圣护盾' }
            ],
            description: '圣火燃烧一切不义！奇迹降临，全队重生'
        },

        // 成吉思汗 - 天之骄子
        'khan_awakening': {
            name: '天之骄子',
            type: 'awakening',
            element: 'fire',
            animation: 'sky_favorite',
            particles: 'eternal_blue_sky',
            sound: 'heaven',
            duration: 2800,
            intensity: 'awakening',
            color: '#ff4500',
            aoe: true,
            shake: true,
            screenFlash: true,
            special: 'tengri_blessing',
            phases: [
                { phase: 1, duration: 400, animation: 'lightning_strike', description: '闪电劈下' },
                { phase: 2, duration: 700, animation: 'fire_explosion', description: '火焰爆发' },
                { phase: 3, duration: 1000, animation: 'army_empower', description: '军队强化' },
                { phase: 4, duration: 700, animation: 'conqueror_glory', description: '征服者荣耀' }
            ],
            description: '长生天之子降世！闪电与火焰，征服一切'
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
     * 获取觉醒技能特效配置
     */
    function getAwakeningEffect(skillId) {
        return AWAKENING_EFFECTS[skillId] || null;
    }

    /**
     * 根据元素生成粒子效果
     */
    function generateElementParticles(element, intensity) {
        var count = intensity === 'awakening' ? 50 : 
                    (intensity === 'ultimate' ? 30 : 
                    (intensity === 'strong' ? 20 : 10));
        var particles = [];
        
        var elementColors = {
            fire: ['#ff4500', '#ff6347', '#ff7f50', '#ffa500', '#ffcc00'],
            water: ['#00bfff', '#1e90ff', '#4169e1', '#87ceeb', '#40e0d0'],
            wind: ['#90ee90', '#98fb98', '#00fa9a', '#00ced1', '#48d1cc'],
            earth: ['#cd853f', '#d2691e', '#8b4513', '#a0522d', '#d4a574'],
            light: ['#ffd700', '#ffec8b', '#fffacd', '#fff8dc', '#ffffff'],
            dark: ['#4b0082', '#8b008b', '#2f0040', '#1a0033', '#6a0dad'],
            neutral: ['#94a3b8', '#cbd5e1', '#e2e8f0', '#f1f5f9', '#ffffff']
        };
        
        var colors = elementColors[element] || elementColors.neutral;
        
        for (var i = 0; i < count; i++) {
            particles.push({
                color: colors[Math.floor(Math.random() * colors.length)],
                size: Math.random() * 10 + 3,
                x: Math.random() * 100 - 50,
                y: Math.random() * 100 - 50,
                vx: (Math.random() - 0.5) * 15,
                vy: (Math.random() - 0.5) * 15,
                life: Math.random() * 0.5 + 0.5,
                rotation: Math.random() * 360,
                rotationSpeed: (Math.random() - 0.5) * 20
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
        if (effect.aoe) {
            classes.push('is-aoe');
        }
        if (effect.teamEffect) {
            classes.push('team-effect');
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

    /**
     * 创建特效DOM元素
     */
    function createEffectElement(effect, x, y) {
        var container = document.createElement('div');
        container.className = getEffectCSSClass(effect);
        container.style.setProperty('--effect-color', effect.color);
        container.style.left = x + 'px';
        container.style.top = y + 'px';
        
        // 添加特效名称显示
        if (effect.name) {
            var nameDisplay = document.createElement('div');
            nameDisplay.className = 'skill-name-display';
            if (effect.intensity === 'ultimate' || effect.intensity === 'awakening') {
                nameDisplay.classList.add('intensity-ultimate');
            }
            nameDisplay.textContent = effect.name;
            nameDisplay.style.setProperty('--effect-color', effect.color);
            container.appendChild(nameDisplay);
        }
        
        // 根据特效类型创建不同的视觉元素
        switch (effect.type) {
            case 'slash':
            case 'dual_slash':
                container.innerHTML += createSlashEffect(effect);
                break;
            case 'magic':
            case 'magic_aoe':
                container.innerHTML += createMagicEffect(effect);
                break;
            case 'projectile':
            case 'aoe_projectile':
                container.innerHTML += createProjectileEffect(effect);
                break;
            case 'heal':
            case 'heal_aoe':
                container.innerHTML += createHealEffect(effect);
                break;
            case 'buff':
            case 'team_buff':
                container.innerHTML += createBuffEffect(effect);
                break;
            case 'debuff':
            case 'debuff_aoe':
                container.innerHTML += createDebuffEffect(effect);
                break;
            case 'charge':
            case 'charge_aoe':
                container.innerHTML += createChargeEffect(effect);
                break;
            case 'combo':
                container.innerHTML += createComboEffect(effect);
                break;
            case 'awakening':
                container.innerHTML += createAwakeningEffect(effect);
                break;
        }
        
        return container;
    }

    /**
     * 创建斩击特效
     */
    function createSlashEffect(effect) {
        var html = '<div class="slash-container">';
        html += '<div class="slash-line"></div>';
        if (effect.type === 'dual_slash') {
            html += '<div class="slash-line second"></div>';
        }
        if (effect.intensity === 'ultimate') {
            html += '<div class="slash-glow"></div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * 创建魔法特效
     */
    function createMagicEffect(effect) {
        var html = '<div class="magic-container">';
        html += '<div class="magic-circle"></div>';
        if (effect.aoe) {
            html += '<div class="magic-circle outer"></div>';
            html += '<div class="magic-circle outer-2"></div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * 创建投射物特效
     */
    function createProjectileEffect(effect) {
        var html = '<div class="projectile-container">';
        html += '<div class="arrow"></div>';
        if (effect.trail || effect.intensity === 'ultimate') {
            html += '<div class="arrow-trail"></div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * 创建治疗特效
     */
    function createHealEffect(effect) {
        var html = '<div class="heal-container">';
        html += '<div class="heal-ring"></div>';
        html += '<div class="heal-cross">+</div>';
        if (effect.intensity === 'ultimate') {
            html += '<div class="heal-ring outer"></div>';
            html += '<div class="heal-particles"></div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * 创建增益特效
     */
    function createBuffEffect(effect) {
        var html = '<div class="buff-container">';
        html += '<div class="buff-aura"></div>';
        if (effect.teamEffect) {
            html += '<div class="buff-wave"></div>';
        }
        if (effect.intensity === 'ultimate') {
            html += '<div class="buff-sparkle"></div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * 创建减益特效
     */
    function createDebuffEffect(effect) {
        var html = '<div class="debuff-container">';
        html += '<div class="debuff-chains"></div>';
        if (effect.aoe) {
            html += '<div class="debuff-wave"></div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * 创建冲锋特效
     */
    function createChargeEffect(effect) {
        var html = '<div class="charge-container">';
        html += '<div class="charge-trail"></div>';
        html += '<div class="charge-impact"></div>';
        html += '</div>';
        return html;
    }

    /**
     * 创建连击特效
     */
    function createComboEffect(effect) {
        var html = '<div class="combo-container">';
        var hits = effect.hits || 3;
        for (var i = 0; i < hits; i++) {
            html += '<div class="combo-hit" style="animation-delay: ' + (i * 0.15) + 's"></div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * 创建觉醒特效
     */
    function createAwakeningEffect(effect) {
        var html = '<div class="awakening-container">';
        html += '<div class="awakening-bg"></div>';
        html += '<div class="awakening-circle"></div>';
        if (effect.phases) {
            effect.phases.forEach(function(phase) {
                html += '<div class="awakening-phase phase-' + phase.phase + '"></div>';
            });
        }
        html += '</div>';
        return html;
    }

    // ==================== 公开API ====================
    return {
        getSkillEffect: getSkillEffect,
        getAwakeningEffect: getAwakeningEffect,
        generateElementParticles: generateElementParticles,
        getEffectCSSClass: getEffectCSSClass,
        getEffectDuration: getEffectDuration,
        createEffectElement: createEffectElement,
        SKILL_EFFECTS: SKILL_EFFECTS,
        AWAKENING_EFFECTS: AWAKENING_EFFECTS,
        DEFAULT_EFFECT: DEFAULT_EFFECT
    };
})();

// 导出全局
window.SkillEffects = SkillEffects;
