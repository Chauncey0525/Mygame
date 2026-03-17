import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseClient } from '@/storage/database/supabase-client';

/** 角色稀有度映射 */
const CHARACTER_RARITY: Record<string, string> = {
  'zhuge-liang': 'legendary',
  'napoleon': 'legendary',
  'arthur': 'epic',
  'wu-zetian': 'epic',
  'hua-mulan': 'rare',
  'caesar': 'rare',
};

/** GET /api/player/characters - 获取玩家角色列表 */
export async function GET(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const playerId = request.headers.get('x-player-id');

    if (!playerId) {
      return NextResponse.json({ error: 'Player ID required' }, { status: 400 });
    }

    const { data, error } = await client
      .from('player_characters')
      .select('*')
      .eq('player_id', playerId);

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ characters: data || [] });
  } catch (error) {
    console.error('GET /api/player/characters error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/** POST /api/player/characters - 添加新角色 */
export async function POST(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const body = await request.json();
    const { playerId, characterId } = body;

    if (!playerId || !characterId) {
      return NextResponse.json({ error: 'Player ID and Character ID required' }, { status: 400 });
    }

    // 检查是否已拥有该角色
    const { data: existing } = await client
      .from('player_characters')
      .select('id')
      .eq('player_id', playerId)
      .eq('character_id', characterId)
      .single();

    if (existing) {
      // 已有角色，增加星级
      const { data: existingChar } = await client
        .from('player_characters')
        .select('stars')
        .eq('id', existing.id)
        .single();

      const currentStars = existingChar?.stars || 1;
      const newStars = currentStars < 6 ? currentStars + 1 : 6;

      const { data, error } = await client
        .from('player_characters')
        .update({
          stars: newStars,
          updated_at: new Date().toISOString(),
        })
        .eq('id', existing.id)
        .select()
        .single();

      if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
      }

      return NextResponse.json({ character: data, isNew: false });
    }

    // 创建新角色
    const rarity = CHARACTER_RARITY[characterId] || 'common';
    const stars = rarity === 'legendary' ? 2 : rarity === 'epic' ? 1 : 1;

    const { data, error } = await client
      .from('player_characters')
      .insert({
        player_id: playerId,
        character_id: characterId,
        stars,
      })
      .select()
      .single();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ character: data, isNew: true });
  } catch (error) {
    console.error('POST /api/player/characters error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/** PUT /api/player/characters - 更新角色数据 */
export async function PUT(request: NextRequest) {
  try {
    const client = getSupabaseClient();
    const body = await request.json();
    const { characterInstanceId, updates } = body;

    if (!characterInstanceId) {
      return NextResponse.json({ error: 'Character instance ID required' }, { status: 400 });
    }

    const { data, error } = await client
      .from('player_characters')
      .update({
        ...updates,
        updated_at: new Date().toISOString(),
      })
      .eq('id', characterInstanceId)
      .select()
      .single();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ success: true, character: data });
  } catch (error) {
    console.error('PUT /api/player/characters error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
