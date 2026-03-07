import * as PIXI from 'pixi.js';
import { Cell, CellState, CellType } from '../../types';
import { UI_CONFIG } from '../../config/gameConfig';

/**
 * 格子渲染器
 */
export class CellRenderer {
  private cellSize: number;
  private padding: number;

  constructor(cellSize: number = UI_CONFIG.CELL_SIZE, padding: number = UI_CONFIG.CELL_PADDING) {
    this.cellSize = cellSize;
    this.padding = padding;
  }

  /**
   * 创建格子精灵
   */
  createCellSprite(cell: Cell, interactive: boolean = true): PIXI.Graphics {
    const graphics = new PIXI.Graphics();

    // 绘制格子背景
    graphics.roundRect(0, 0, this.cellSize, this.cellSize, 8);

    if (cell.state === CellState.HIDDEN) {
      this.drawHiddenCell(graphics);
    } else if (cell.state === CellState.REVEALED) {
      this.drawRevealedCell(graphics, cell);
    } else if (cell.state === CellState.DEPLOYED) {
      this.drawDeployedCell(graphics, cell);
    }

    graphics.stroke({ width: 2, color: 0x0f3460 });

    // 设置交互性
    if (interactive) {
      graphics.eventMode = 'static';
      graphics.cursor = 'pointer';
    }

    return graphics;
  }

  /**
   * 绘制隐藏格子
   */
  private drawHiddenCell(graphics: PIXI.Graphics): void {
    graphics.fill({ color: 0x16213e });

    // 添加纹理效果
    const overlay = new PIXI.Graphics();
    overlay.roundRect(2, 2, this.cellSize - 4, this.cellSize - 4, 6);
    overlay.fill({
      color: 0x1e3a5f,
      alpha: 0.3,
    });
    graphics.addChild(overlay);
  }

  /**
   * 绘制已揭示格子
   */
  private drawRevealedCell(graphics: PIXI.Graphics, cell: Cell): void {
    if (cell.type === CellType.NUMBER) {
      this.drawNumberCell(graphics, cell);
    } else if (cell.type === CellType.MONSTER) {
      this.drawMonsterCell(graphics, cell);
    } else if (cell.type === CellType.TASK) {
      this.drawTaskCell(graphics, cell);
    }
  }

  /**
   * 绘制数字格子
   */
  private drawNumberCell(graphics: PIXI.Graphics, cell: Cell): void {
    const numberCell = cell as any;

    if (numberCell.number === 0) {
      // 空白格子
      graphics.fill({ color: 0x1e3a5f });
    } else {
      // 数字格子 - 根据数字显示不同颜色
      const colors = [
        0x1e3a5f, // 0
        0x4ecdc4, // 1
        0x95e1d3, // 2
        0xf38181, // 3
        0xaa96da, // 4
        0xfcbad3, // 5
        0xffd700, // 6
        0xff8c00, // 7
        0xff4500, // 8
      ];
      const color = colors[Math.min(numberCell.number, 8)];
      graphics.fill({ color });

      // 绘制数字
      const text = new PIXI.Text({
        text: numberCell.number.toString(),
        style: {
          fontSize: 28,
          fill: 0xffffff,
          fontWeight: 'bold',
        }
      });
      text.anchor.set(0.5);
      text.x = this.cellSize / 2;
      text.y = this.cellSize / 2;
      graphics.addChild(text);
    }
  }

  /**
   * 绘制怪物格子
   */
  private drawMonsterCell(graphics: PIXI.Graphics, cell: any): void {
    if (cell.triggered && !cell.battled) {
      // 已触发但未战斗 - 橙色
      graphics.fill({ color: 0xff8c00 });

      // 绘制怪物战力
      const powerText = new PIXI.Text({
        text: `⚔${cell.power}`,
        style: {
          fontSize: 20,
          fill: 0xffffff,
          fontWeight: 'bold',
        }
      });
      powerText.anchor.set(0.5);
      powerText.x = this.cellSize / 2;
      powerText.y = this.cellSize / 2;
      graphics.addChild(powerText);
    } else if (cell.battled) {
      // 已战斗 - 显示战斗结果
      if (cell.battleResult === 'VICTORY') {
        graphics.fill({ color: 0x4ecdc4 }); // 胜利 - 青色
        const victoryText = new PIXI.Text({
          text: '✓',
          style: {
            fontSize: 32,
            fill: 0xffffff,
            fontWeight: 'bold',
          }
        });
        victoryText.anchor.set(0.5);
        victoryText.x = this.cellSize / 2;
        victoryText.y = this.cellSize / 2;
        graphics.addChild(victoryText);
      } else {
        graphics.fill({ color: 0x8b0000 }); // 失败 - 深红色
        const defeatText = new PIXI.Text({
          text: '✗',
          style: {
            fontSize: 32,
            fill: 0xffffff,
            fontWeight: 'bold',
          }
        });
        defeatText.anchor.set(0.5);
        defeatText.x = this.cellSize / 2;
        defeatText.y = this.cellSize / 2;
        graphics.addChild(defeatText);
      }
    } else {
      // 未触发 - 深红色
      graphics.fill({ color: 0x8b0000 });

      // 绘制问号
      const questionText = new PIXI.Text({
        text: '?',
        style: {
          fontSize: 28,
          fill: 0xffffff,
          fontWeight: 'bold',
        }
      });
      questionText.anchor.set(0.5);
      questionText.x = this.cellSize / 2;
      questionText.y = this.cellSize / 2;
      graphics.addChild(questionText);
    }
  }

  /**
   * 绘制任务格子
   */
  private drawTaskCell(graphics: PIXI.Graphics, cell: any): void {
    if (cell.completed) {
      if (cell.confirmed) {
        // 已确认 - 金色
        graphics.fill({ color: 0xffd700 });

        const checkText = new PIXI.Text({
          text: '★',
          style: {
            fontSize: 32,
            fill: 0x000000,
            fontWeight: 'bold',
          }
        });
        checkText.anchor.set(0.5);
        checkText.x = this.cellSize / 2;
        checkText.y = this.cellSize / 2;
        graphics.addChild(checkText);
      } else {
        // 已完成但未确认 - 浅金色
        graphics.fill({ color: 0xffec8b });

        const infoText = new PIXI.Text({
          text: '!',
          style: {
            fontSize: 32,
            fill: 0x000000,
            fontWeight: 'bold',
          }
        });
        infoText.anchor.set(0.5);
        infoText.x = this.cellSize / 2;
        infoText.y = this.cellSize / 2;
        graphics.addChild(infoText);
      }
    } else {
      // 未完成 - 紫色
      graphics.fill({ color: 0x4a3f6b });

      // 绘制任务图标
      const taskText = new PIXI.Text({
        text: '⚑',
        style: {
          fontSize: 28,
          fill: 0xffffff,
          fontWeight: 'bold',
        }
      });
      taskText.anchor.set(0.5);
      taskText.x = this.cellSize / 2;
      taskText.y = this.cellSize / 2;
      graphics.addChild(taskText);
    }
  }

  /**
   * 绘制已部署格子
   */
  private drawDeployedCell(graphics: PIXI.Graphics, cell: Cell): void {
    // 先绘制基础格子
    this.drawRevealedCell(graphics, cell);

    // 然后绘制兵种
    if (cell.unit) {
      this.drawUnit(graphics, cell.unit);
    }
  }

  /**
   * 绘制兵种
   */
  private drawUnit(graphics: PIXI.Graphics, unit: any): void {
    // 绘制兵种背景圆
    const unitGraphics = new PIXI.Graphics();
    unitGraphics.circle(this.cellSize / 2, this.cellSize / 2, this.cellSize / 3);
    unitGraphics.fill({ color: unit.color, alpha: 0.7 });
    unitGraphics.stroke({ width: 2, color: 0xffffff });

    // 绘制兵种名称首字母
    const firstChar = unit.name.charAt(0);
    const unitText = new PIXI.Text({
      text: firstChar,
      style: {
        fontSize: 20,
        fill: 0xffffff,
        fontWeight: 'bold',
      }
    });
    unitText.anchor.set(0.5);
    unitText.x = this.cellSize / 2;
    unitText.y = this.cellSize / 2;
    unitGraphics.addChild(unitText);

    graphics.addChild(unitGraphics);

    // 如果有团结一致效果，绘制效果指示器
    if (unit.unityBonusCount > 0) {
      const bonusText = new PIXI.Text({
        text: unit.unityBonusCount === 1 ? '2x' : '4x',
        style: {
          fontSize: 12,
          fill: 0xffd700,
          fontWeight: 'bold',
        }
      });
      bonusText.anchor.set(0.5);
      bonusText.x = this.cellSize - 10;
      bonusText.y = 10;
      graphics.addChild(bonusText);
    }
  }
}
