import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseClient } from '@/storage/database/supabase-client';

/** 创建默认每日任务 */
function createDefaultDailyTasks(playerId: string, taskDate: string) {
  return [
    {
      player_id: playerId,
      task_id: 'daily-login',
      name: '每日签到',
      description: '登录游戏',
      target: 1,
      progress: 1,
      reward_gold: 500,
      reward_gems: 50,
      completed: true,
      claimed: false,
      task_date: taskDate,
    },
    {
      player_id: playerId,
      task_id: 'daily-battle',
      name: '每日战斗',
      description: '完成3次战斗',
      target: 3,
      progress: 0,
      reward_gold: 300,
      reward_exp: 100,
      completed: false,
      claimed: false,
      task_date: taskDate,
    },
    {
      player_id: playerId,
      task_id: 'daily-summon',
      name: '每日召唤',
      description: '进行1次召唤',
      target: 1,
      progress: 0,
      reward_gold: 200,
      reward_gems: 20,
      completed: false,
      claimed: false,
      task_date: taskDate,
    },
    {
      player_id: playerId,
      task_id: 'daily-levelup',
      name: '强化角色',
      description: '强化任意角色1次',
      target: 1,
      progress: 0,
      reward_gold: 400,
      reward_exp: 50,
      completed: false,
      claimed: false,
      task_date: taskDate,
    },
  ];
}

/** GET /api/player - 获取或创建玩家数据 */
export async function GET(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const playerId = request.headers.get('x-player-id');

    if (!playerId) {
      // 创建新玩家
      const today = new Date().toISOString().split('T')[0];
      
      const { data: newPlayer, error: playerError } = await client
        .from('players')
        .insert({
          name: '勇者',
        })
        .select()
        .single();

      if (playerError || !newPlayer) {
        return NextResponse.json({ error: 'Failed to create player' }, { status: 500 });
      }

      // 创建每日任务
      const tasks = createDefaultDailyTasks(newPlayer.id, today);
      await client.from('player_daily_tasks').insert(tasks);

      // 获取完整数据
      return NextResponse.json({
        player: newPlayer,
        characters: [],
        team: [],
        completedStages: [],
        dailyTasks: tasks,
      });
    }

    // 获取现有玩家数据
    const { data: player, error: playerError } = await client
      .from('players')
      .select('*')
      .eq('id', playerId)
      .single();

    if (playerError || !player) {
      return NextResponse.json({ error: 'Player not found' }, { status: 404 });
    }

    // 检查并更新体力
    const now = new Date();
    const lastUpdate = new Date(player.last_energy_update);
    const hoursPassed = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60);
    const energyToRecover = Math.min(
      Math.floor(hoursPassed * 10),
      player.max_energy - player.energy
    );

    if (energyToRecover > 0) {
      const newEnergy = Math.min(player.max_energy, player.energy + energyToRecover);
      await client
        .from('players')
        .update({ energy: newEnergy, last_energy_update: now.toISOString() })
        .eq('id', playerId);
      player.energy = newEnergy;
      player.last_energy_update = now.toISOString();
    }

    // 检查每日任务重置
    const today = new Date().toISOString().split('T')[0];
    let dailyTasks;

    if (player.last_login_date !== today) {
      // 重置每日任务
      await client
        .from('player_daily_tasks')
        .delete()
        .eq('player_id', playerId);

      const tasks = createDefaultDailyTasks(playerId, today);
      await client.from('player_daily_tasks').insert(tasks);
      dailyTasks = tasks;

      // 更新登录信息
      await client
        .from('players')
        .update({
          last_login_date: today,
          total_play_days: player.total_play_days + 1,
        })
        .eq('id', playerId);
      player.last_login_date = today;
      player.total_play_days += 1;
    } else {
      // 获取今日任务
      const { data: tasks } = await client
        .from('player_daily_tasks')
        .select('*')
        .eq('player_id', playerId)
        .eq('task_date', today);
      dailyTasks = tasks || [];
    }

    // 获取角色
    const { data: characters } = await client
      .from('player_characters')
      .select('*')
      .eq('player_id', playerId);

    // 获取队伍
    const { data: teamData } = await client
      .from('player_team')
      .select('*')
      .eq('player_id', playerId)
      .order('slot');

    const team = (teamData || []).map(t => t.character_instance_id.toString());

    // 获取已通关关卡
    const { data: completedStagesData } = await client
      .from('player_completed_stages')
      .select('stage_id')
      .eq('player_id', playerId);

    const completedStages = (completedStagesData || []).map(s => s.stage_id);

    return NextResponse.json({
      player,
      characters: characters || [],
      team,
      completedStages,
      dailyTasks,
    });
  } catch (error) {
    console.error('GET /api/player error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/** PUT /api/player - 更新玩家数据 */
export async function PUT(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const body = await request.json();
    const { playerId, updates } = body;

    if (!playerId) {
      return NextResponse.json({ error: 'Player ID required' }, { status: 400 });
    }

    const { data, error } = await client
      .from('players')
      .update({
        ...updates,
        updated_at: new Date().toISOString(),
      })
      .eq('id', playerId)
      .select()
      .single();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ success: true, player: data });
  } catch (error) {
    console.error('PUT /api/player error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
