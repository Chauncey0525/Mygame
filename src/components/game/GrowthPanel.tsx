'use client';

import Image from 'next/image';
import { useState } from 'react';
import { PlayerData, OwnedCharacter, RARITY_NAMES, RARITY_COLORS, RARITY_STARS, Rarity, calculateStats } from '@/types/growth';
import { BattleCharacter, ELEMENT_COLORS, ELEMENT_NAMES, ROLE_NAMES } from '@/types/game';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { ALL_CHARACTERS } from '@/data/characters';

interface GrowthPanelProps {
  playerData: PlayerData;
  onLevelUp: (instanceId: string, expAmount: number) => Promise<boolean>;
  onBreakthrough: (instanceId: string) => Promise<boolean>;
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
  const [isUpgrading, setIsUpgrading] = useState(false);

  const handleSelectCharacter = (character: OwnedCharacter) => {
    setSelectedCharacter(character);
    setShowDetail(true);
  };

  const handleLevelUp = async () => {
    if (!selectedCharacter) return;
    setIsUpgrading(true);
    try {
      const success = await onLevelUp(selectedCharacter.id, 100);
      if (success && selectedCharacter) {
        setSelectedCharacter({
          ...selectedCharacter,
          level: selectedCharacter.level + 1,
          exp: 0,
        });
      }
    } finally {
      setIsUpgrading(false);
    }
  };

  const handleBreakthrough = async () => {
    if (!selectedCharacter) return;
    setIsUpgrading(true);
    try {
      const success = await onBreakthrough(selectedCharacter.id);
      if (success && selectedCharacter) {
        setSelectedCharacter({
          ...selectedCharacter,
          breakthrough: selectedCharacter.breakthrough + 1,
        });
      }
    } finally {
      setIsUpgrading(false);
    }
  };

  const toggleTeam = (instanceId: string) => {
    const currentTeam = playerData.team;
    if (currentTeam.includes(instanceId)) {
      onSetTeam(currentTeam.filter((id) => id !== instanceId));
    } else if (currentTeam.length < 4) {
      onSetTeam([...currentTeam, instanceId]);
    }
  };

  // 按稀有度排序角色
  const sortedCharacters = [...playerData.characters].sort((a, b) => {
    const rarityOrder = { legendary: 0, epic: 1, rare: 2, common: 3 };
    return rarityOrder[a.rarity] - rarityOrder[b.rarity];
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

          const battleChar = getBattleCharacter(owned.id);
          const isInTeam = playerData.team.includes(owned.id);

          return (
            <Card
              key={owned.id}
              className={cn(
                'cursor-pointer transition-all hover:scale-105 border-2 overflow-hidden',
                isInTeam ? 'border-yellow-400 ring-2 ring-yellow-400/30' : 'border-slate-600'
              )}
              onClick={() => handleSelectCharacter(owned)}
            >
              <div className="relative aspect-square">
                <Image
                  src={template.avatar}
                  alt={template.name}
                  fill
                  className="object-cover object-top"
                  unoptimized
                />
                <div className="absolute top-2 left-2">
                  <Badge
                    className="text-xs font-bold text-white"
                    style={{ backgroundColor: RARITY_COLORS[owned.rarity] }}
                  >
                    {RARITY_NAMES[owned.rarity]}
                  </Badge>
                </div>
                <div className="absolute top-2 right-2">
                  <Badge className="bg-slate-800 text-white text-xs">
                    Lv.{owned.level}
                  </Badge>
                </div>
                {isInTeam && (
                  <div className="absolute bottom-2 right-2">
                    <Badge className="bg-yellow-500 text-black text-xs font-bold">
                      出战
                    </Badge>
                  </div>
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900 to-transparent p-2">
                  <div className="text-sm font-bold text-white truncate">{template.name}</div>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: owned.stars }).map((_, i) => (
                      <span key={i} className="text-yellow-400 text-xs">★</span>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* 角色详情弹窗 */}
      <Dialog open={showDetail} onOpenChange={setShowDetail}>
        <DialogContent className="max-w-lg bg-slate-800 border-2 border-slate-600">
          {selectedCharacter && (() => {
            const template = getTemplate(selectedCharacter.characterId);
            if (!template) return null;
            const battleChar = getBattleCharacter(selectedCharacter.id);
            const isInTeam = playerData.team.includes(selectedCharacter.id);
            const breakthroughCost = (selectedCharacter.breakthrough + 1) * 1000;

            return (
              <>
                <DialogHeader>
                  <DialogTitle className="text-white text-xl flex items-center gap-2">
                    {template.name}
                    <Badge style={{ backgroundColor: RARITY_COLORS[selectedCharacter.rarity] }}>
                      {RARITY_NAMES[selectedCharacter.rarity]}
                    </Badge>
                  </DialogTitle>
                  <DialogDescription className="text-slate-400">
                    {template.title}
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 mt-4">
                  {/* 角色信息 */}
                  <div className="flex gap-4">
                    <div className="w-24 h-24 rounded-lg overflow-hidden border-2"
                      style={{ borderColor: ELEMENT_COLORS[template.element] }}>
                      <Image
                        src={template.avatar}
                        alt={template.name}
                        width={96}
                        height={96}
                        className="object-cover object-top"
                        unoptimized
                      />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-slate-400">等级:</span>
                        <span className="text-white font-bold">{selectedCharacter.level}</span>
                        <span className="text-slate-400 ml-2">突破:</span>
                        <span className="text-white font-bold">{selectedCharacter.breakthrough}</span>
                      </div>
                      <div className="flex items-center gap-1 mb-2">
                        <span className="text-slate-400">星级:</span>
                        {Array.from({ length: selectedCharacter.stars }).map((_, i) => (
                          <span key={i} className="text-yellow-400">★</span>
                        ))}
                      </div>
                      <div className="flex gap-2">
                        <Badge style={{ backgroundColor: ELEMENT_COLORS[template.element] }}>
                          {ELEMENT_NAMES[template.element]}
                        </Badge>
                        <Badge className="bg-slate-600">
                          {ROLE_NAMES[template.roleType]}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* 属性 */}
                  {battleChar && (
                    <Card className="bg-slate-700 border-slate-600">
                      <CardContent className="p-3">
                        <h4 className="font-bold text-white mb-2">属性</h4>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-400">生命</span>
                            <span className="text-green-400 font-bold">{battleChar.stats.maxHp}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">攻击</span>
                            <span className="text-red-400 font-bold">{battleChar.stats.attack}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">防御</span>
                            <span className="text-blue-400 font-bold">{battleChar.stats.defense}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">速度</span>
                            <span className="text-yellow-400 font-bold">{battleChar.stats.speed}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* 技能 */}
                  <Card className="bg-slate-700 border-slate-600">
                    <CardContent className="p-3">
                      <h4 className="font-bold text-white mb-2">技能</h4>
                      <div className="space-y-2">
                        {template.skills.map((skill) => (
                          <div key={skill.id} className="text-sm">
                            <div className="flex items-center gap-2">
                              <span className="text-yellow-400 font-bold">{skill.name}</span>
                              <Badge className="bg-slate-600 text-xs">Lv.1</Badge>
                            </div>
                            <p className="text-slate-400 text-xs mt-1">{skill.description}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* 操作按钮 */}
                  <div className="flex gap-2">
                    <Button
                      onClick={handleLevelUp}
                      disabled={isUpgrading || playerData.resources.exp < 100}
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                    >
                      升级 (消耗 100 经验书)
                    </Button>
                    <Button
                      onClick={handleBreakthrough}
                      disabled={isUpgrading || playerData.resources.gold < breakthroughCost || selectedCharacter.breakthrough >= 5}
                      className="flex-1 bg-purple-600 hover:bg-purple-700"
                    >
                      突破 ({breakthroughCost} 金币)
                    </Button>
                  </div>
                  
                  <Button
                    onClick={() => toggleTeam(selectedCharacter.id)}
                    className={cn(
                      'w-full',
                      isInTeam ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
                    )}
                  >
                    {isInTeam ? '移出队伍' : '加入队伍'}
                  </Button>
                </div>
              </>
            );
          })()}
        </DialogContent>
      </Dialog>
    </div>
  );
}
