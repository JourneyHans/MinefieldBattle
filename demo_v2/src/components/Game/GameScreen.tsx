import { useState, useEffect } from 'react';
import { PixiStage } from '../../rendering/Stage';
import { useGameStore } from '../../store/gameStore';
import { Difficulty } from '../../types';

/**
 * 游戏界面组件
 */
export const GameScreen: React.FC = () => {
  const [selectedCard, setSelectedCard] = useState<number | null>(null);
  const [selectedCell, setSelectedCell] = useState<{row: number, col: number} | null>(null);
  const [gameMessages, setGameMessages] = useState<string[]>([]);

  const gameState = useGameStore((state) => state.gameState);
  const initGame = useGameStore((state) => state.initGame);
  const revealCell = useGameStore((state) => state.revealCell);
  const deployCard = useGameStore((state) => state.deployCard);
  const battleMonster = useGameStore((state) => state.battleMonster);
  const endTurn = useGameStore((state) => state.endTurn);
  const confirmTask = useGameStore((state) => state.confirmTask);

  // 初始化游戏
  useEffect(() => {
    initGame(Difficulty.BEGINNER);
    addMessage('游戏开始！初级难度');
  }, []);

  /**
   * 处理格子点击
   */
  const handleCellClick = (row: number, col: number) => {
    if (!gameState) return;

    // 如果已选择卡牌，尝试部署
    if (selectedCard !== null) {
      const result = deployCard(selectedCard, row, col);
      if (result.success) {
        addMessage(`成功部署卡牌到 (${row}, ${col})`);
        setSelectedCard(null);
      } else {
        addMessage(`部署失败: ${result.message || '无法部署'}`);
      }
    } else {
      // 否则尝试揭示格子
      const result = revealCell(row, col);
      if (result.success) {
        if (result.monsterTriggered) {
          addMessage(`触发怪物！战力: ${result.monsterTriggered.power}`);
        } else if (result.taskRevealed) {
          addMessage('发现任务格子！');
        } else {
          addMessage(`揭示格子 (${row}, ${col})`);
        }
      }
    }
  };

  /**
   * 处理卡牌点击
   */
  const handleCardClick = (cardIndex: number) => {
    if (!gameState) return;

    if (selectedCard === cardIndex) {
      // 取消选择
      setSelectedCard(null);
      addMessage('取消选择卡牌');
    } else {
      // 选择卡牌
      setSelectedCard(cardIndex);
      const card = gameState.hand[cardIndex];
      addMessage(`选择卡牌: ${card.name} (战力: ${card.power})`);
    }
  };

  /**
   * 添加消息
   */
  const addMessage = (message: string) => {
    setGameMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
    // 保持最近10条消息
    setGameMessages(prev => prev.slice(-10));
  };

  /**
   * 结束回合
   */
  const handleEndTurn = () => {
    endTurn();
    addMessage('回合结束，发新牌...');
    setSelectedCard(null);
  };

  /**
   * 确认任务
   */
  const handleConfirmTask = () => {
    if (!gameState || !gameState.taskCell) return;

    const success = confirmTask();
    if (success) {
      addMessage('🎉 任务完成！游戏胜利！');
    } else {
      addMessage('任务未完成，无法确认');
    }
  };

  if (!gameState) {
    return (
      <div className="flex items-center justify-center" style={{ backgroundColor: '#1a1a2e', color: '#f1f1f1', height: '100vh' }}>
        <div>加载中...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center p-8" style={{ backgroundColor: '#1a1a2e', color: '#f1f1f1', minHeight: '100vh' }}>
      <h1 className="text-3xl font-bold mb-4" style={{ color: '#e94560' }}>
        魔法军团：地雷战场
      </h1>

      <div className="flex gap-8 mb-4">
        {/* 游戏区域 */}
        <div className="rounded-lg p-4" style={{ backgroundColor: '#16213e' }}>
          <PixiStage
            width={800}
            height={600}
            gameState={gameState}
            onCellClick={handleCellClick}
            onCardClick={handleCardClick}
          />
        </div>

        {/* 信息面板 */}
        <div className="flex flex-col gap-4">
          {/* 操作按钮 */}
          <div className="rounded-lg p-4" style={{ backgroundColor: '#16213e' }}>
            <h3 className="text-lg font-semibold mb-3">操作</h3>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => endTurn()}
                className="px-4 py-2 rounded font-semibold transition-colors"
                style={{ backgroundColor: '#0f3460', color: '#f1f1f1' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e94560'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#0f3460'}
              >
                结束回合
              </button>
              <button
                onClick={() => initGame(Difficulty.BEGINNER)}
                className="px-4 py-2 rounded font-semibold transition-colors"
                style={{ backgroundColor: '#0f3460', color: '#f1f1f1' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e94560'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#0f3460'}
              >
                重新开始
              </button>
              {gameState.taskCell && gameState.taskCell.completed && (
                <button
                  onClick={handleConfirmTask}
                  className="px-4 py-2 rounded font-semibold transition-colors"
                  style={{ backgroundColor: '#4ecdc4', color: '#f1f1f1' }}
                >
                  确认任务
                </button>
              )}
            </div>
          </div>

          {/* 当前选择 */}
          <div className="rounded-lg p-4" style={{ backgroundColor: '#16213e' }}>
            <h3 className="text-lg font-semibold mb-3">当前选择</h3>
            {selectedCard !== null ? (
              <div>
                <p>已选卡牌: {gameState.hand[selectedCard]?.name}</p>
                <p className="text-sm" style={{ color: '#a2a8d3' }}>点击格子进行部署</p>
              </div>
            ) : (
              <p className="text-sm" style={{ color: '#a2a8d3' }}>点击卡牌选择，点击格子揭示</p>
            )}
          </div>

          {/* 游戏消息 */}
          <div className="rounded-lg p-4" style={{ backgroundColor: '#16213e' }}>
            <h3 className="text-lg font-semibold mb-3">游戏日志</h3>
            <div className="text-sm font-mono" style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {gameMessages.map((msg, index) => (
                <div key={index} className="mb-1" style={{ color: '#a2a8d3' }}>
                  {msg}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 游戏结束提示 */}
      {gameState.status.gameOver && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="rounded-lg p-8 text-center" style={{ backgroundColor: '#16213e' }}>
            <h2 className="text-3xl font-bold mb-4">
              {gameState.status.gameWon ? '🎉 胜利！' : '💀 失败！'}
            </h2>
            <p className="mb-6">
              {gameState.status.gameWon ? '恭喜你完成了任务！' : '生命值耗尽，游戏结束。'}
            </p>
            <button
              onClick={() => initGame(Difficulty.BEGINNER)}
              className="px-6 py-3 rounded font-semibold"
              style={{ backgroundColor: '#e94560', color: '#f1f1f1' }}
            >
              重新开始
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameScreen;
