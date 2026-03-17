'use client';

import Image from 'next/image';
import { useState } from 'react';
import { PlayerData, OwnedCharacter, RARITY_NAMES, RARITY_COLORS, RARITY_STARS, Rarity, calculateStats } from '@/types/growth';
import { BattleCharacter, ELEMENT_COLORS, ELEMENT_NAMES, ROLE_NAMES } from '@/types/game';
import { CharacterCard } from './CharacterCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { ALL_CHARACTERS } from '@/data/characters';

interface GrowthPanelProps {
  playerData: PlayerData;
  onLevelUp: (instanceId: string) => { success: boolean; newLevel?: number };
  onBreakthrough: (instanceId: string) => boolean;
  onSetTeam: (characterIds: string[]) => void;
  getBattleCharacter: (instanceId: string) => BattleCharacter | null;
}

export function GrowthPanel({
  playerData,
  onLevelUp,
  onBreakthrough,
  onSetTeam,
  getBattleCharacter,
}: GrowthPanelProps) {
  const [selectedCharacter, setSelectedCharacter] = useState<OwnedCharacter | null>(null);
  const [showDetail, setShowDetail] = useState(false);

  const handleSelectCharacter = (character: OwnedCharacter) => {
    setSelectedCharacter(character);
    setShowDetail(true);
  };

  const handleLevelUp = () => {
    if (selectedCharacter) {
      const result = onLevelUp(selectedCharacter.id);
      if (result.success && selectedCharacter) {
        // 更新选中角色
        setSelectedCharacter({
          ...selectedCharacter,
          growth: {
            ...selectedCharacter.growth,
            level: result.newLevel || selectedCharacter.growth.level,
          },
        });
      }
    }
  };

  const handleBreakthrough = () => {
    if (selectedCharacter) {
      const success = onBreakthrough(selectedCharacter.id);
      if (success && selectedCharacter) {
        setSelectedCharacter({
          ...selectedCharacter,
          growth: {
            ...selectedCharacter.growth,
            breakthrough: selectedCharacter.growth.breakthrough + 1,
            maxLevel: selectedCharacter.growth.maxLevel + 10,
          },
        });
      }
    }
  };

  // 按稀有度排序角色
  const sortedCharacters = [...playerData.characters].sort((a, b) => {
    const rarityOrder = { legendary: 0, epic: 1, rare: 2, common: 3 };
    const aRarity = getCharacterRarity(a.characterId);
    const bRarity = getCharacterRarity(b.characterId);
    return rarityOrder[aRarity] - rarityOrder[bRarity];
  });

  // 获取角色模板
  const getTemplate = (characterId: string) => {
    return ALL_CHARACTERS.find((c) => c.id === characterId);
  };

  return (
    <div className="space-y-4">
      {/* 角色列表 */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {sortedCharacters.map((owned) => {
          const template = getTemplate(owned.characterId);
          if (!template) return null;

          const rarity = getCharacterRarity(owned.characterId);
          const battleChar = getBattleCharacter(owned.id);

          return (
            <Card
              key={owned.id}
              className={cn(
                'cursor-pointer transition-all hover:scale-105 border-2 overflow-hidden',
                owned.isInTeam && 'ring-2 ring-yellow-400'
              )}
              style={{ borderColor: RARITY_COLORS[rarity] }}
              onClick={() => handleSelectCharacter(owned)}
            >
              <div className="relative">
                {/* 头像 */}
                <div className="relative h-32 w-full overflow-hidden bg-slate-700">
                  <Image
                    src={template.avatar}
                    alt={template.name}
                    fill
                    className="object-cover object-top"
                    unoptimized
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />
                </div>

                {/* 稀有度星星 */}
                <div className="absolute top-1 right-1 flex gap-0.5">
                  {Array.from({ length: RARITY_STARS[rarity] }).map((_, i) => (
                    <span key={i} className="text-yellow-400 text-xs">⭐</span>
                  ))}
                </div>

                {/* 等级 */}
                <div className="absolute bottom-1 left-1 bg-slate-800/90 px-2 py-0.5 rounded text-xs font-bold text-white">
                  Lv.{owned.growth.level}
                </div>
              </div>

              <CardContent className="p-2">
                <h4 className="font-bold text-white text-sm truncate">{template.name}</h4>
                <div className="flex items-center justify-between mt-1">
                  <Badge
                    className="text-xs"
                    style={{ backgroundColor: ELEMENT_COLORS[template.element] }}
                  >
                    {ELEMENT_NAMES[template.element]}
                  </Badge>
                  {owned.growth.breakthrough > 0 && (
                    <span className="text-xs text-purple-400">+{owned.growth.breakthrough}</span>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 角色详情弹窗 */}
      <Dialog open={showDetail} onOpenChange={setShowDetail}>
        <DialogContent className="max-w-2xl bg-slate-800 border-2 border-slate-600">
          {selectedCharacter && (() => {
            const template = getTemplate(selectedCharacter.characterId);
            if (!template) return null;

            const rarity = getCharacterRarity(selectedCharacter.characterId);
            const battleChar = getBattleCharacter(selectedCharacter.id);
            const levelUpCost = 500;
            const breakthroughCost = {
              gold: 10000 * (selectedCharacter.growth.breakthrough + 1),
              shards: 50 * (selectedCharacter.growth.breakthrough + 1),
            };

            return (
              <>
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2 text-white">
                    <span className="text-2xl">{template.name}</span>
                    <div className="flex gap-0.5">
                      {Array.from({ length: RARITY_STARS[rarity] }).map((_, i) => (
                        <span key={i} className="text-yellow-400">⭐</span>
                      ))}
                    </div>
                  </DialogTitle>
                  <DialogDescription className="text-slate-300">
                    {template.title} · {RARITY_NAMES[rarity]}
                  </DialogDescription>
                </DialogHeader>

                <div className="grid grid-cols-2 gap-4 mt-4">
                  {/* 左侧：立绘 */}
                  <div className="relative aspect-[3/4] overflow-hidden rounded-lg border-2 border-slate-600">
                    <Image
                      src={template.illustration}
                      alt={template.name}
                      fill
                      className="object-cover object-top"
                      unoptimized
                    />
                  </div>

                  {/* 右侧：属性和操作 */}
                  <div className="space-y-4">
                    {/* 等级信息 */}
                    <Card className="bg-slate-700 border-slate-600">
                      <CardContent className="p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-slate-300">等级</span>
                          <span className="text-xl font-bold text-white">
                            {selectedCharacter.growth.level} / {selectedCharacter.growth.maxLevel}
                          </span>
                        </div>
                        <Progress
                          value={(selectedCharacter.growth.level / selectedCharacter.growth.maxLevel) * 100}
                          className="h-2"
                        />
                        {selectedCharacter.growth.breakthrough > 0 && (
                          <div className="mt-1 text-sm text-purple-400">
                            突破次数: {selectedCharacter.growth.breakthrough}
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* 属性 */}
                    {battleChar && (
                      <Card className="bg-slate-700 border-slate-600">
                        <CardContent className="p-3 space-y-2">
                          <div className="flex justify-between">
                            <span className="text-slate-300">❤️ HP</span>
                            <span className="font-bold text-green-400">{battleChar.stats.hp}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-300">⚔️ 攻击</span>
                            <span className="font-bold text-orange-400">{battleChar.stats.attack}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-300">🛡️ 防御</span>
                            <span className="font-bold text-blue-400">{battleChar.stats.defense}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-300">💨 速度</span>
                            <span className="font-bold text-cyan-400">{battleChar.stats.speed}</span>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* 碎片数量 */}
                    <div className="flex items-center justify-between p-2 bg-slate-700 rounded-lg">
                      <span className="text-slate-300">💎 角色碎片</span>
                      <span className="font-bold text-purple-400">{selectedCharacter.growth.copies}</span>
                    </div>

                    {/* 操作按钮 */}
                    <div className="space-y-2">
                      <Button
                        className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
                        onClick={handleLevelUp}
                        disabled={
                          selectedCharacter.growth.level >= selectedCharacter.growth.maxLevel ||
                          playerData.resources.gold < levelUpCost
                        }
                      >
                        升级 ({levelUpCost} 💰)
                      </Button>

                      <Button
                        className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                        onClick={handleBreakthrough}
                        disabled={
                          selectedCharacter.growth.breakthrough >= 5 ||
                          playerData.resources.gold < breakthroughCost.gold ||
                          selectedCharacter.growth.copies < breakthroughCost.shards
                        }
                      >
                        突破 ({breakthroughCost.gold} 💰 + {breakthroughCost.shards} 💎)
                      </Button>
                    </div>
                  </div>
                </div>
              </>
            );
          })()}
        </DialogContent>
      </Dialog>
    </div>
  );
}

/** 获取角色稀有度 */
function getCharacterRarity(characterId: string): Rarity {
  const rarityMap: Record<string, Rarity> = {
    'zhuge-liang': 'legendary',
    'napoleon': 'legendary',
    'arthur': 'epic',
    'wu-zetian': 'epic',
    'hua-mulan': 'rare',
    'caesar': 'rare',
  };
  return rarityMap[characterId] || 'rare';
}
