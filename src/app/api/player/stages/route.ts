import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseClient } from '@/storage/database/supabase-client';

/** POST /api/player/stages - 记录通关 */
export async function POST(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const body = await request.json();
    const { playerId, stageId, rewards } = body;

    if (!playerId || !stageId) {
      return NextResponse.json({ error: 'Player ID and Stage ID required' }, { status: 400 });
    }

    // 检查是否已通关
    const { data: existing } = await client
      .from('player_completed_stages')
      .select('id')
      .eq('player_id', playerId)
      .eq('stage_id', stageId)
      .single();

    if (!existing) {
      // 记录通关
      await client
        .from('player_completed_stages')
        .insert({
          player_id: playerId,
          stage_id: stageId,
        });
    }

    // 发放奖励
    if (rewards) {
      const updates: Record<string, number> = {};
      if (rewards.gold) updates.gold = rewards.gold;
      if (rewards.gems) updates.gems = rewards.gems;
      if (rewards.exp) updates.exp = rewards.exp;

      if (Object.keys(updates).length > 0) {
        // 获取当前玩家数据
        const { data: player } = await client
          .from('players')
          .select('gold, gems, exp')
          .eq('id', playerId)
          .single();

        if (player) {
          const newValues: Record<string, number> = {};
          if (updates.gold) newValues.gold = player.gold + updates.gold;
          if (updates.gems) newValues.gems = player.gems + updates.gems;
          if (updates.exp) {
            newValues.exp = player.exp + updates.exp;
            // TODO: 处理升级逻辑
          }

          await client
            .from('players')
            .update(newValues)
            .eq('id', playerId);
        }
      }
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('POST /api/player/stages error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
