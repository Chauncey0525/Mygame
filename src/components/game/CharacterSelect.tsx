'use client';

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
    <div className="mx-auto max-w-5xl space-y-6 p-4">
      {/* 标题 */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white">选择你的英雄</h1>
        <p className="mt-2 text-slate-400">选择一位历史人物，开启你的战斗之旅</p>
      </div>

      {/* 角色网格 */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {characters.map((character) => (
          <Card
            key={character.id}
            className={cn(
              'cursor-pointer transition-all hover:scale-105 hover:shadow-lg',
              selectedCharacter?.id === character.id
                ? 'ring-2 ring-yellow-400 shadow-lg shadow-yellow-400/20'
                : 'border-slate-700 bg-slate-800/50 hover:border-slate-500'
            )}
            onClick={() => onSelect(character)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{character.name}</CardTitle>
                  <CardDescription>{character.title}</CardDescription>
                </div>
                {/* 元素标记 */}
                <Badge
                  className="text-xs"
                  style={{ backgroundColor: ELEMENT_COLORS[character.element] }}
                >
                  {ELEMENT_NAMES[character.element]}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {/* 头像占位 */}
              <div className="mb-3 flex items-center justify-center">
                <div
                  className="flex h-16 w-16 items-center justify-center rounded-full text-3xl"
                  style={{ backgroundColor: ELEMENT_COLORS[character.element] + '30' }}
                >
                  {character.id === 'zhuge-liang' && '🪭'}
                  {character.id === 'napoleon' && '⚔️'}
                  {character.id === 'arthur' && '🗡️'}
                  {character.id === 'wu-zetian' && '👑'}
                  {character.id === 'hua-mulan' && '🌸'}
                  {character.id === 'caesar' && '🦅'}
                </div>
              </div>

              {/* 基本信息 */}
              <div className="mb-3 flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  {character.era}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {character.origin}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  {ROLE_NAMES[character.roleType]}
                </Badge>
              </div>

              {/* 属性条 */}
              <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-8 text-slate-400">HP</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-green-500"
                      style={{ width: `${(character.stats.hp / 4000) * 100}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-slate-300">{character.stats.hp}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-8 text-slate-400">ATK</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-orange-500"
                      style={{ width: `${(character.stats.attack / 1000) * 100}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-slate-300">{character.stats.attack}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-8 text-slate-400">DEF</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-blue-500"
                      style={{ width: `${(character.stats.defense / 1000) * 100}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-slate-300">{character.stats.defense}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-8 text-slate-400">SPD</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-700">
                    <div
                      className="h-full bg-green-500"
                      style={{ width: `${(character.stats.speed / 1000) * 100}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-slate-300">{character.stats.speed}</span>
                </div>
              </div>

              {/* 技能预览 */}
              <div className="mt-3 space-y-1">
                <div className="text-xs font-bold text-slate-400">技能:</div>
                <div className="flex flex-wrap gap-1">
                  {character.skills.map((skill) => (
                    <Badge key={skill.id} variant="outline" className="text-xs">
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
        <Button variant="outline" onClick={onRandomSelect} className="gap-2">
          🎲 随机选择
        </Button>
        <Button
          onClick={onStartBattle}
          disabled={!selectedCharacter}
          className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          ⚔️ 开始战斗
        </Button>
      </div>

      {/* 已选角色展示 */}
      {selectedCharacter && (
        <Card className="border-yellow-500 bg-yellow-900/20">
          <CardContent className="flex items-center justify-center gap-4 py-4">
            <div className="text-4xl">
              {selectedCharacter.id === 'zhuge-liang' && '🪭'}
              {selectedCharacter.id === 'napoleon' && '⚔️'}
              {selectedCharacter.id === 'arthur' && '🗡️'}
              {selectedCharacter.id === 'wu-zetian' && '👑'}
              {selectedCharacter.id === 'hua-mulan' && '🌸'}
              {selectedCharacter.id === 'caesar' && '🦅'}
            </div>
            <div>
              <div className="font-bold text-yellow-400">{selectedCharacter.name}</div>
              <div className="text-sm text-slate-400">{selectedCharacter.title}</div>
            </div>
            <Badge style={{ backgroundColor: ELEMENT_COLORS[selectedCharacter.element] }}>
              {ELEMENT_NAMES[selectedCharacter.element]}属性
            </Badge>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
