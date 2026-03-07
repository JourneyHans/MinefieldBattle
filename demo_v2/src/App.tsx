import { useState } from 'react';
import { GameScreen } from './components/Game/GameScreen';
import { useGameStore } from './store/gameStore';
import { Difficulty } from './types';
import './App.css';

// 主菜单组件
const MainMenu: React.FC<{ onStartGame: (difficulty: Difficulty) => void }> = ({ onStartGame }) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8" style={{ backgroundColor: '#1a1a2e', color: '#f1f1f1' }}>
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-5xl font-bold mb-4" style={{ color: '#e94560' }}>
          魔法军团：地雷战场
        </h1>
        <h2 className="text-2xl mb-8" style={{ color: '#a2a8d3' }}>
          Demo_v2 网页版
        </h2>

        <div className="rounded-lg p-8 mb-6" style={{ backgroundColor: '#16213e' }}>
          <h3 className="text-xl font-semibold mb-6">选择难度</h3>
          <div className="flex flex-col gap-4">
            <button
              onClick={() => onStartGame(Difficulty.BEGINNER)}
              className="px-6 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105"
              style={{ backgroundColor: '#4ecdc4', color: '#f1f1f1' }}
            >
              初级 (9x9, 10个怪物)
            </button>
            <button
              onClick={() => onStartGame(Difficulty.INTERMEDIATE)}
              className="px-6 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105"
              style={{ backgroundColor: '#f38181', color: '#f1f1f1' }}
            >
              中级 (16x16, 40个怪物)
            </button>
            <button
              onClick={() => onStartGame(Difficulty.EXPERT)}
              className="px-6 py-4 rounded-lg font-semibold text-lg transition-all hover:scale-105"
              style={{ backgroundColor: '#aa96da', color: '#f1f1f1' }}
            >
              高级 (16x30, 99个怪物)
            </button>
          </div>
        </div>

        <div className="rounded-lg p-6" style={{ backgroundColor: '#16213e' }}>
          <h3 className="text-lg font-semibold mb-4">游戏说明</h3>
          <div className="text-sm space-y-2" style={{ color: '#a2a8d3', textAlign: 'left' }}>
            <p>🎮 <strong>核心玩法：</strong>扫雷 + 卡牌对战</p>
            <p>🃏 <strong>卡牌系统：</strong>每回合发5张卡牌，部署兵种到数字格子</p>
            <p>⚔️ <strong>战斗系统：</strong>兵种战力 vs 怪物战力</p>
            <p>🎯 <strong>胜利条件：</strong>完成任务并确认</p>
            <p>💀 <strong>失败条件：</strong>生命值归零</p>
          </div>
        </div>

        <div className="mt-6 text-sm" style={{ color: '#a2a8d3' }}>
          <p>技术栈: React 18 + TypeScript + PixiJS + Zustand</p>
          <p>状态: 核心逻辑完成 ✅ | PixiJS渲染已集成 ✅</p>
        </div>
      </div>
    </div>
  );
};

function App() {
  const [gameStarted, setGameStarted] = useState(false);
  const initGame = useGameStore((state) => state.initGame);

  const handleStartGame = (difficulty: Difficulty) => {
    initGame(difficulty);
    setGameStarted(true);
  };

  const handleBackToMenu = () => {
    setGameStarted(false);
  };

  return (
    <>
      {!gameStarted ? (
        <MainMenu onStartGame={handleStartGame} />
      ) : (
        <div>
          <button
            onClick={handleBackToMenu}
            className="fixed top-4 left-4 px-4 py-2 rounded font-semibold z-10"
            style={{ backgroundColor: '#0f3460', color: '#f1f1f1' }}
          >
            ← 返回主菜单
          </button>
          <GameScreen />
        </div>
      )}
    </>
  );
}

export default App;
