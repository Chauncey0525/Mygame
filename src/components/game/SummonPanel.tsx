'use client';

import Image from 'next/image';
import { useState, useEffect } from 'react';
import { SummonResult, RARITY_NAMES, RARITY_COLORS, RARITY_STARS } from '@/types/growth';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { ALL_CHARACTERS } from '@/data/characters';

interface SummonPanelProps {
  gems: number;
  summonTickets: number;
  pity: number;
  legendaryPity: number;
  isSummoning: boolean;
  onSummonOnce: () => Promise<any>;
  onSummonTen: () => Promise<any[]>;
  onSummonWithTicket: () => Promise<any>;
}

export function SummonPanel({
  gems,
  summonTickets,
  pity,
  legendaryPity,
  isSummoning,
  onSummonOnce,
  onSummonTen,
  onSummonWithTicket,
}: SummonPanelProps) {
  const [results, setResults] = useState<SummonResult[]>([]);
  const [showResult, setShowResult] = useState(false);
  const [animatingIndex, setAnimatingIndex] = useState(0);

  const handleSummonOnce = async () => {
    const result = await onSummonOnce();
    if (result) {
      setResults([result]);
      setShowResult(true);
      setAnimatingIndex(0);
    }
  };

  const handleSummonTen = async () => {
    const results = await onSummonTen();
    if (results && results.length > 0) {
      setResults(results);
      setShowResult(true);
      setAnimatingIndex(0);
    }
  };

  const handleSummonWithTicket = async () => {
    const result = await onSummonWithTicket();
    if (result) {
      setResults([result]);
      setShowResult(true);
      setAnimatingIndex(0);
    }
  };

  // 抽卡动画
  useEffect(() => {
    if (showResult && results.length > 1) {
      const timer = setInterval(() => {
        setAnimatingIndex((prev) => {
          if (prev >= results.length - 1) {
            clearInterval(timer);
            return prev;
          }
          return prev + 1;
        });
      }, 200);
      return () => clearInterval(timer);
    }
  }, [showResult, results.length]);

  const closeResult = () => {
    setShowResult(false);
    setResults([]);
  };

  return (
    <div className="space-y-6">
      {/* 抽卡横幅 */}
      <div className="relative h-48 rounded-xl overflow-hidden border-2 border-yellow-500/50">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900 via-blue-900 to-cyan-900" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-3xl font-black text-white drop-shadow-lg">英雄召唤</h2>
            <p className="text-yellow-400 mt-2">召唤历史英雄，组建你的战队！</p>
          </div>
        </div>
        {/* 装饰星星 */}
        <div className="absolute top-4 left-4 text-yellow-400 text-2xl animate-pulse">⭐</div>
        <div className="absolute top-8 right-8 text-yellow-400 text-xl animate-pulse delay-100">✨</div>
        <div className="absolute bottom-4 left-8 text-yellow-400 text-lg animate-pulse delay-200">💫</div>
      </div>

      {/* 保底信息 */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="bg-slate-800 border-purple-500/50">
          <CardContent className="p-4 text-center">
            <div className="text-slate-300 text-sm">史诗保底</div>
            <div className="text-2xl font-bold text-purple-400 mt-1">
              {pity} / 50
            </div>
            <Progress value={(pity / 50) * 100} className="h-2 mt-2" />
          </CardContent>
        </Card>
        <Card className="bg-slate-800 border-yellow-500/50">
          <CardContent className="p-4 text-center">
            <div className="text-slate-300 text-sm">传说保底</div>
            <div className="text-2xl font-bold text-yellow-400 mt-1">
              {legendaryPity} / 100
            </div>
            <Progress value={(legendaryPity / 100) * 100} className="h-2 mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* 抽卡按钮 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 单抽 */}
        <Button
          onClick={handleSummonOnce}
          disabled={isSummoning || gems < 150}
          className="h-20 flex-col gap-1 bg-gradient-to-b from-blue-600 to-blue-800 hover:from-blue-500 hover:to-blue-700 disabled:opacity-50"
        >
          <span className="text-lg font-bold">单抽</span>
          <span className="text-sm">💎 150</span>
        </Button>

        {/* 十连 */}
        <Button
          onClick={handleSummonTen}
          disabled={isSummoning || gems < 1350}
          className="h-20 flex-col gap-1 bg-gradient-to-b from-purple-600 to-purple-800 hover:from-purple-500 hover:to-purple-700 disabled:opacity-50"
        >
          <span className="text-lg font-bold">十连抽</span>
          <span className="text-sm">💎 1350 (9折)</span>
        </Button>

        {/* 召唤券 */}
        <Button
          onClick={handleSummonWithTicket}
          disabled={isSummoning || summonTickets < 1}
          className="h-20 flex-col gap-1 bg-gradient-to-b from-yellow-600 to-yellow-800 hover:from-yellow-500 hover:to-yellow-700 disabled:opacity-50"
        >
          <span className="text-lg font-bold">使用召唤券</span>
          <span className="text-sm">🎫 {summonTickets}</span>
        </Button>
      </div>

      {/* 当前资源 */}
      <Card className="bg-slate-800 border-slate-600">
        <CardContent className="p-4 flex justify-around">
          <div className="text-center">
            <div className="text-2xl">💎</div>
            <div className="font-bold text-cyan-400">{gems}</div>
            <div className="text-xs text-slate-400">钻石</div>
          </div>
          <div className="text-center">
            <div className="text-2xl">🎫</div>
            <div className="font-bold text-yellow-400">{summonTickets}</div>
            <div className="text-xs text-slate-400">召唤券</div>
          </div>
        </CardContent>
      </Card>

      {/* 抽卡概率 */}
      <Card className="bg-slate-800 border-slate-600">
        <CardContent className="p-4">
          <h4 className="font-bold text-white mb-2">📊 召唤概率</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span style={{ color: RARITY_COLORS.legendary }}>传说</span>
              <span className="text-white">10%</span>
            </div>
            <div className="flex justify-between">
              <span style={{ color: RARITY_COLORS.epic }}>史诗</span>
              <span className="text-white">30%</span>
            </div>
            <div className="flex justify-between">
              <span style={{ color: RARITY_COLORS.rare }}>稀有</span>
              <span className="text-white">60%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 抽卡结果弹窗 */}
      <Dialog open={showResult} onOpenChange={setShowResult}>
        <DialogContent className="max-w-4xl bg-slate-900 border-2 border-slate-600">
          <div className="p-4">
            <h3 className="text-xl font-bold text-center text-white mb-4">
              {results.length > 1 ? '🎉 召唤结果' : '✨ 获得角色'}
            </h3>

            <div className={cn(
              'grid gap-3',
              results.length === 1 ? 'grid-cols-1 max-w-xs mx-auto' :
              results.length <= 4 ? 'grid-cols-2' : 'grid-cols-5'
            )}>
              {results.slice(0, animatingIndex + 1).map((result, index) => {
                const template = ALL_CHARACTERS.find((c) => c.id === result.characterId);
                if (!template) return null;

                return (
                  <Card
                    key={index}
                    className={cn(
                      'overflow-hidden border-2 animate-pop-in',
                      result.isNew && 'ring-2 ring-yellow-400'
                    )}
                    style={{ borderColor: RARITY_COLORS[result.rarity] }}
                  >
                    <div className="relative aspect-square">
                      <Image
                        src={template.avatar}
                        alt={template.name}
                        fill
                        className="object-cover object-top"
                        unoptimized
                      />
                      {/* 稀有度星星 */}
                      <div className="absolute top-1 left-1 flex gap-0.5">
                        {Array.from({ length: RARITY_STARS[result.rarity] }).map((_, i) => (
                          <span key={i} className="text-yellow-400 text-xs drop-shadow-lg">⭐</span>
                        ))}
                      </div>
                      {/* 新获得标记 */}
                      {result.isNew && (
                        <div className="absolute top-1 right-1 bg-yellow-500 px-2 py-0.5 rounded text-xs font-bold text-black">
                          NEW!
                        </div>
                      )}
                    </div>
                    <CardContent className="p-2 text-center bg-slate-800">
                      <h4 className="font-bold text-white text-sm truncate">{template.name}</h4>
                      <div className="text-xs mt-1" style={{ color: RARITY_COLORS[result.rarity] }}>
                        {RARITY_NAMES[result.rarity]}
                      </div>
                      {!result.isNew && result.shards > 0 && (
                        <div className="text-xs text-purple-400 mt-1">+{result.shards} 碎片</div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="mt-6 text-center">
              <Button
                onClick={closeResult}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8"
              >
                确认
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <style jsx>{`
        @keyframes pop-in {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          50% {
            transform: scale(1.1);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
        .animate-pop-in {
          animation: pop-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
