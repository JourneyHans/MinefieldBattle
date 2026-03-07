import React, { useRef, useEffect, useState } from 'react';
import * as PIXI from 'pixi.js';
import { Application, Container } from 'pixi.js';
import { CellRenderer } from './renderers/CellRenderer';
import { CardRenderer } from './renderers/CardRenderer';
import { Cell } from '../types';

interface PixiStageProps {
  width: number;
  height: number;
  gameState: any;
  onCellClick?: (row: number, col: number) => void;
  onCardClick?: (cardIndex: number) => void;
}

/**
 * PixiJS舞台组件
 */
export const PixiStage: React.FC<PixiStageProps> = ({
  width,
  height,
  gameState,
  onCellClick,
  onCardClick
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pixiAppRef = useRef<Application | null>(null);
  const cellRendererRef = useRef(new CellRenderer());
  const cardRendererRef = useRef(new CardRenderer());
  const [isReady, setIsReady] = useState(false);

  // 初始化PixiJS应用
  useEffect(() => {
    if (!canvasRef.current) return;

    const initPixi = async () => {
      try {
        // 创建PixiJS应用
        const app = new Application();

        await app.init({
          width,
          height,
          canvas: canvasRef.current!,
          backgroundColor: 0x1a1a2e,
          antialias: true,
          resolution: window.devicePixelRatio || 1,
          autoDensity: true,
        });

        pixiAppRef.current = app;
        setIsReady(true);

        // 创建主容器
        const mainContainer = new Container();
        app.stage.addChild(mainContainer);

      } catch (error) {
        console.error('Failed to initialize PixiJS:', error);
      }
    };

    initPixi();

    // 清理函数
    return () => {
      if (pixiAppRef.current) {
        pixiAppRef.current.destroy(true, { children: true, texture: true });
        pixiAppRef.current = null;
      }
    };
  }, [width, height]);

  // 当游戏状态变化时重新渲染
  useEffect(() => {
    if (isReady && pixiAppRef.current && gameState) {
      try {
        const mainContainer = pixiAppRef.current.stage.children[0] as Container;
        if (mainContainer) {
          mainContainer.removeChildren();
          renderGameScene(pixiAppRef.current, mainContainer, gameState);
        }
      } catch (error) {
        console.error('Failed to render game scene:', error);
      }
    }
  }, [isReady, gameState]);

  /**
   * 渲染游戏场景
   */
  const renderGameScene = (app: Application, container: Container, gameState: any) => {
    if (!gameState || !gameState.grid) return;

    const grid = gameState.grid;
    const cellSize = 60;
    const padding = 6;
    const offsetX = 20;
    const offsetY = 20;
    const gridWidth = grid[0].length * (cellSize + padding);
    const gridHeight = grid.length * (cellSize + padding);

    // 创建地图容器
    const mapContainer = new Container();
    mapContainer.x = offsetX;
    mapContainer.y = offsetY;

    // 渲染地图格子
    grid.forEach((row: Cell[], rowIndex: number) => {
      row.forEach((cell: Cell, colIndex: number) => {
        const cellSprite = cellRendererRef.current.createCellSprite(cell, true);

        // 设置位置
        cellSprite.x = colIndex * (cellSize + padding);
        cellSprite.y = rowIndex * (cellSize + padding);

        // 添加点击事件
        cellSprite.on('pointerdown', () => {
          if (onCellClick) {
            onCellClick(rowIndex, colIndex);
          }
        });

        // 添加悬停效果
        cellSprite.on('pointerover', () => {
          cellSprite.alpha = 0.8;
        });

        cellSprite.on('pointerout', () => {
          cellSprite.alpha = 1;
        });

        mapContainer.addChild(cellSprite);
      });
    });

    container.addChild(mapContainer);

    // 渲染手牌
    if (gameState.hand && gameState.hand.length > 0) {
      const handY = offsetY + gridHeight + 20;

      // 创建手牌标题
      const handTitle = new PIXI.Text({
        text: '手牌',
        style: {
          fontSize: 16,
          fill: 0xf1f1f1,
          fontWeight: 'bold',
        }
      });
      handTitle.x = offsetX;
      handTitle.y = handY - 25;
      container.addChild(handTitle);

      // 创建手牌区域
      const handContainer = cardRendererRef.current.createHandArea(
        gameState.hand,
        (index: number) => {
          if (onCardClick) {
            onCardClick(index);
          }
        }
      );

      handContainer.x = offsetX;
      handContainer.y = handY;
      container.addChild(handContainer);
    }

    // 渲染游戏信息
    renderGameInfo(container, gameState, offsetX, offsetY, gridWidth);
  };

  /**
   * 渲染游戏信息
   */
  const renderGameInfo = (
    container: Container,
    gameState: any,
    x: number,
    y: number,
    gridWidth: number
  ) => {
    const infoX = x + gridWidth + 40;
    const infoY = y;
    const lineHeight = 30;

    // 生命值
    const healthText = new PIXI.Text({
      text: `❤ 生命值: ${gameState.status.health}`,
      style: {
        fontSize: 16,
        fill: 0xe94560,
        fontWeight: 'bold',
      }
    });
    healthText.x = infoX;
    healthText.y = infoY;
    container.addChild(healthText);

    // 回合数
    const turnText = new PIXI.Text({
      text: `🔄 回合: ${gameState.status.currentTurn}`,
      style: {
        fontSize: 16,
        fill: 0x4ecdc4,
        fontWeight: 'bold',
      }
    });
    turnText.x = infoX;
    turnText.y = infoY + lineHeight;
    container.addChild(turnText);

    // 难度
    const difficultyNames: Record<string, string> = {
      'BEGINNER': '初级',
      'INTERMEDIATE': '中级',
      'EXPERT': '高级'
    };
    const difficultyText = new PIXI.Text({
      text: `⚔ 难度: ${difficultyNames[gameState.status.difficulty] || '未知'}`,
      style: {
        fontSize: 16,
        fill: 0xf1f1f1,
        fontWeight: 'bold',
      }
    });
    difficultyText.x = infoX;
    difficultyText.y = infoY + lineHeight * 2;
    container.addChild(difficultyText);

    // 游戏状态
    if (gameState.status.gameOver) {
      const statusText = new PIXI.Text({
        text: gameState.status.gameWon ? '🎉 胜利!' : '💀 失败!',
        style: {
          fontSize: 24,
          fill: gameState.status.gameWon ? 0x4ecdc4 : 0xe94560,
          fontWeight: 'bold',
        }
      });
      statusText.x = infoX;
      statusText.y = infoY + lineHeight * 3;
      container.addChild(statusText);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <canvas
        ref={canvasRef}
        style={{
          border: '2px solid #0f3460',
          borderRadius: '8px',
          display: 'block',
        }}
      />
      {!isReady && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#f1f1f1',
            fontSize: '18px',
          }}
        >
          加载中...
        </div>
      )}
    </div>
  );
};

export default PixiStage;
