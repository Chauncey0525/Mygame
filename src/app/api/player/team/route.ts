import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseClient } from '@/storage/database/supabase-client';

/** GET /api/player/team - 获取玩家队伍 */
export async function GET(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const playerId = request.headers.get('x-player-id');

    if (!playerId) {
      return NextResponse.json({ error: 'Player ID required' }, { status: 400 });
    }

    const { data, error } = await client
      .from('player_team')
      .select('*')
      .eq('player_id', playerId)
      .order('slot');

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const team = (data || []).map(t => ({
      slot: t.slot,
      characterInstanceId: t.character_instance_id,
    }));

    return NextResponse.json({ team });
  } catch (error) {
    console.error('GET /api/player/team error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/** POST /api/player/team - 设置队伍 */
export async function POST(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const body = await request.json();
    const { playerId, team } = body; // team: [characterInstanceId, ...]

    if (!playerId || !Array.isArray(team)) {
      return NextResponse.json({ error: 'Player ID and team array required' }, { status: 400 });
    }

    // 删除旧队伍配置
    await client
      .from('player_team')
      .delete()
      .eq('player_id', playerId);

    // 创建新队伍配置
    if (team.length > 0) {
      const teamData = team.map((characterInstanceId, slot) => ({
        player_id: playerId,
        slot,
        character_instance_id: characterInstanceId,
      }));

      const { error } = await client
        .from('player_team')
        .insert(teamData);

      if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
      }
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('POST /api/player/team error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
