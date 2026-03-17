'use client';

import Image from 'next/image';
import { BattleCharacter, ELEMENT_COLORS, ELEMENT_NAMES, ROLE_NAMES } from '@/types/game';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface CharacterSelectProps {
  characters: BattleCharacter[];
  selectedCharacter: BattleCharacter | null;
  onSelect: (character: BattleCharacter) => void;
  onStartBattle: () => void;
  onRandomSelect: () => void;
}

export function CharacterSelect({
  characters,
  selectedCharacter,
  onSelect,
  onStartBattle,
  onRandomSelect,
}: CharacterSelectProps) {
  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4">
      {/* 标题 */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-black bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
          选择你的英雄
        </h1>
        <p className="text-slate-400">选择一位历史人物，开启你的战斗之旅</p>
      </div>

      {/* 角色网格 */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {characters.map((character) => (
          <Card
            key={character.id}
            className={cn(
              'relative cursor-pointer overflow-hidden transition-all hover:scale-[1.02] hover:shadow-2xl',
              selectedCharacter?.id === character.id
                ? 'ring-2 ring-yellow-400 shadow-xl shadow-yellow-400/20'
                : 'border-slate-700 bg-slate-800/50 hover:border-slate-500'
            )}
            onClick={() => onSelect(character)}
          >
            {/* 立绘背景 */}
            <div className="absolute inset-0 -z-10">
              <Image
                src={character.illustration}
                alt={character.name}
                fill
                className="object-cover object-top"
                style={{ opacity: 0.2 }}
                unoptimized
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/80 to-slate-800/60" />
            </div>

            <CardHeader className="pb-2 relative">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-xl font-black">{character.name}</CardTitle>
                  <CardDescription className="text-slate-300">{character.title}</CardDescription>
                </div>
                {/* 元素标记 */}
                <Badge
                  className="text-xs font-bold shadow-lg"
                  style={{ backgroundColor: ELEMENT_COLORS[character.element] }}
                >
                  {ELEMENT_NAMES[character.element]}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {/* 头像 */}
              <div className="mb-4 flex justify-center">
                <div
                  className="relative h-32 w-32 overflow-hidden rounded-full border-4 shadow-2xl"
                  style={{ borderColor: ELEMENT_COLORS[character.element] }}
                >
                  <Image
                    src={character.avatar}
                    alt={character.name}
                    fill
                    className="object-cover object-top"
                    unoptimized
                  />
                </div>
              </div>

              {/* 基本信息 */}
              <div className="mb-4 flex flex-wrap justify-center gap-2">
                <Badge variant="outline" className="text-xs border-slate-600">
                  📅 {character.era}
                </Badge>
                <Badge variant="outline" className="text-xs border-slate-600">
                  🌍 {character.origin}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  ⚔️ {ROLE_NAMES[character.roleType]}
                </Badge>
              </div>

              {/* 属性条 */}
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-10 font-medium text-slate-400">❤️ HP</span>
                  <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-gradient-to-r from-green-600 to-green-400 transition-all"
                      style={{ width: `${(character.stats.hp / 4000) * 100}%` }}
                    />
                  </div>
                  <span className="w-14 text-right font-bold text-green-400">{character.stats.hp}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-10 font-medium text-slate-400">⚔️ ATK</span>
                  <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-gradient-to-r from-orange-600 to-orange-400 transition-all"
                      style={{ width: `${(character.stats.attack / 1000) * 100}%` }}
                    />
                  </div>
                  <span className="w-14 text-right font-bold text-orange-400">{character.stats.attack}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-10 font-medium text-slate-400">🛡️ DEF</span>
                  <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-gradient-to-r from-blue-600 to-blue-400 transition-all"
                      style={{ width: `${(character.stats.defense / 1000) * 100}%` }}
                    />
                  </div>
                  <span className="w-14 text-right font-bold text-blue-400">{character.stats.defense}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-10 font-medium text-slate-400">💨 SPD</span>
                  <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 transition-all"
                      style={{ width: `${(character.stats.speed / 1000) * 100}%` }}
                    />
                  </div>
                  <span className="w-14 text-right font-bold text-cyan-400">{character.stats.speed}</span>
                </div>
              </div>

              {/* 技能预览 */}
              <div className="mt-4 space-y-2">
                <div className="text-xs font-bold text-slate-400">✨ 技能:</div>
                <div className="grid grid-cols-2 gap-1">
                  {character.skills.map((skill) => (
                    <Badge
                      key={skill.id}
                      variant="outline"
                      className="text-xs justify-center py-1"
                      style={{ 
                        borderColor: ELEMENT_COLORS[skill.element] + '50',
                        color: ELEMENT_COLORS[skill.element]
                      }}
                    >
                      {skill.type === 'special' && '⭐'}
                      {skill.type === 'heal' && '💚'}
                      {skill.type === 'buff' && '⬆️'}
                      {skill.name}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 操作按钮 */}
      <div className="flex justify-center gap-4">
        <Button
          variant="outline"
          onClick={onRandomSelect}
          className="gap-2 border-slate-600 hover:border-yellow-400 hover:text-yellow-400"
        >
          🎲 随机选择
        </Button>
        <Button
          onClick={onStartBattle}
          disabled={!selectedCharacter}
          className="gap-2 bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 hover:from-yellow-600 hover:via-orange-600 hover:to-red-600 disabled:opacity-50 px-8 py-6 text-lg font-bold shadow-lg shadow-orange-500/30"
        >
          ⚔️ 开始战斗！
        </Button>
      </div>

      {/* 已选角色展示 */}
      {selectedCharacter && (
        <Card className="border-yellow-500 bg-gradient-to-r from-yellow-900/20 via-orange-900/20 to-red-900/20 overflow-hidden">
          <div className="absolute inset-0 -z-10">
            <Image
              src={selectedCharacter.illustration}
              alt={selectedCharacter.name}
              fill
              className="object-cover object-top"
              style={{ opacity: 0.15 }}
              unoptimized
            />
          </div>
          <CardContent className="flex items-center justify-center gap-6 py-6">
            <div className="relative h-20 w-20 overflow-hidden rounded-full border-3 shadow-xl"
              style={{ borderColor: ELEMENT_COLORS[selectedCharacter.element] }}>
              <Image
                src={selectedCharacter.avatar}
                alt={selectedCharacter.name}
                fill
                className="object-cover object-top"
                unoptimized
              />
            </div>
            <div className="text-center">
              <div className="text-2xl font-black text-yellow-400">{selectedCharacter.name}</div>
              <div className="text-sm text-slate-300">{selectedCharacter.title}</div>
            </div>
            <Badge 
              className="text-sm px-4 py-2"
              style={{ backgroundColor: ELEMENT_COLORS[selectedCharacter.element] }}
            >
              {ELEMENT_NAMES[selectedCharacter.element]}属性
            </Badge>
            <Badge variant="secondary" className="text-sm px-4 py-2">
              Lv.{selectedCharacter.level}
            </Badge>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
