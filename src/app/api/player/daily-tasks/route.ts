import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseClient } from '@/storage/database/supabase-client';

/** PUT /api/player/daily-tasks - 更新任务进度 */
export async function PUT(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const body = await request.json();
    const { playerId, taskId, progress } = body;

    if (!playerId || !taskId) {
      return NextResponse.json({ error: 'Player ID and Task ID required' }, { status: 400 });
    }

    // 获取当前任务
    const { data: task, error: taskError } = await client
      .from('player_daily_tasks')
      .select('*')
      .eq('player_id', playerId)
      .eq('task_id', taskId)
      .single();

    if (taskError || !task) {
      return NextResponse.json({ error: 'Task not found' }, { status: 404 });
    }

    // 更新进度
    const newProgress = task.progress + (progress || 1);
    const completed = newProgress >= task.target;

    const { data, error } = await client
      .from('player_daily_tasks')
      .update({
        progress: Math.min(newProgress, task.target),
        completed,
        updated_at: new Date().toISOString(),
      })
      .eq('id', task.id)
      .select()
      .single();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ success: true, task: data });
  } catch (error) {
    console.error('PUT /api/player/daily-tasks error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/** POST /api/player/daily-tasks/claim - 领取任务奖励 */
export async function POST(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const body = await request.json();
    const { playerId, taskId } = body;

    if (!playerId || !taskId) {
      return NextResponse.json({ error: 'Player ID and Task ID required' }, { status: 400 });
    }

    // 获取任务
    const { data: task, error: taskError } = await client
      .from('player_daily_tasks')
      .select('*')
      .eq('player_id', playerId)
      .eq('task_id', taskId)
      .single();

    if (taskError || !task) {
      return NextResponse.json({ error: 'Task not found' }, { status: 404 });
    }

    if (!task.completed) {
      return NextResponse.json({ error: 'Task not completed' }, { status: 400 });
    }

    if (task.claimed) {
      return NextResponse.json({ error: 'Task already claimed' }, { status: 400 });
    }

    // 获取玩家数据
    const { data: player } = await client
      .from('players')
      .select('gold, gems, exp')
      .eq('id', playerId)
      .single();

    if (!player) {
      return NextResponse.json({ error: 'Player not found' }, { status: 404 });
    }

    // 发放奖励
    const updates: Record<string, number> = {};
    if (task.reward_gold) updates.gold = player.gold + task.reward_gold;
    if (task.reward_gems) updates.gems = player.gems + task.reward_gems;
    if (task.reward_exp) updates.exp = player.exp + task.reward_exp;

    // 更新玩家资源
    await client
      .from('players')
      .update(updates)
      .eq('id', playerId);

    // 标记已领取
    await client
      .from('player_daily_tasks')
      .update({ claimed: true, updated_at: new Date().toISOString() })
      .eq('id', task.id);

    return NextResponse.json({ 
      success: true, 
      rewards: {
        gold: task.reward_gold || 0,
        gems: task.reward_gems || 0,
        exp: task.reward_exp || 0,
      },
    });
  } catch (error) {
    console.error('POST /api/player/daily-tasks/claim error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
