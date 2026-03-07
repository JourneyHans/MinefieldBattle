import * as PIXI from 'pixi.js';
import { Card } from '../../types';
import { UI_CONFIG } from '../../config/gameConfig';

/**
 * 卡牌渲染器
 */
export class CardRenderer {
  private cardWidth: number;
  private cardHeight: number;
  private padding: number;

  constructor(
    cardWidth: number = UI_CONFIG.CARD_WIDTH,
    cardHeight: number = UI_CONFIG.CARD_HEIGHT,
    padding: number = UI_CONFIG.HAND_PADDING
  ) {
    this.cardWidth = cardWidth;
    this.cardHeight = cardHeight;
    this.padding = padding;
  }

  /**
   * 创建卡牌精灵
   */
  createCardSprite(card: Card, interactive: boolean = true): PIXI.Container {
    const container = new PIXI.Container();

    // 创建卡牌背景
    const background = new PIXI.Graphics();
    background.roundRect(0, 0, this.cardWidth, this.cardHeight, 8);
    background.fill({ color: card.color });
    background.stroke({ width: 2, color: 0xffffff });

    // 创建卡牌内容
    const cardContent = this.createCardContent(card);

    container.addChild(background);
    container.addChild(cardContent);

    // 设置交互性
    if (interactive) {
      container.eventMode = 'static';
      container.cursor = 'pointer';

      // 添加悬停效果
      container.on('pointerover', () => {
        background.alpha = 0.8;
        container.scale.set(1.05);
      });

      container.on('pointerout', () => {
        background.alpha = 1;
        container.scale.set(1);
      });
    }

    return container;
  }

  /**
   * 创建卡牌内容
   */
  private createCardContent(card: Card): PIXI.Container {
    const content = new PIXI.Container();

    // 卡牌名称
    const nameText = new PIXI.Text({
      text: card.name,
      style: {
        fontSize: 14,
        fill: 0xffffff,
        fontWeight: 'bold',
        align: 'center',
      }
    });
    nameText.anchor.set(0.5);
    nameText.x = this.cardWidth / 2;
    nameText.y = 20;
    content.addChild(nameText);

    // 战力显示
    const powerLabel = new PIXI.Text({
      text: '战力',
      style: {
        fontSize: 12,
        fill: 0xffffff,
        align: 'center',
      }
    });
    powerLabel.anchor.set(0.5);
    powerLabel.x = this.cardWidth / 2;
    powerLabel.y = 45;
    content.addChild(powerLabel);

    const powerText = new PIXI.Text({
      text: card.power.toString(),
      style: {
        fontSize: 24,
        fill: 0xffd700,
        fontWeight: 'bold',
        align: 'center',
      }
    });
    powerText.anchor.set(0.5);
    powerText.x = this.cardWidth / 2;
    powerText.y = 70;
    content.addChild(powerText);

    // 兵种图标（简单几何图形表示）
    const icon = this.createUnitIcon(card.unitType);
    icon.x = this.cardWidth / 2;
    icon.y = this.cardHeight - 20;
    content.addChild(icon);

    return content;
  }

  /**
   * 创建兵种图标
   */
  private createUnitIcon(unitType: string): PIXI.Graphics {
    const graphics = new PIXI.Graphics();

    // 根据兵种类型绘制不同图标
    switch (unitType) {
      case 'WARRIOR': // 战士 - 剑
        graphics.moveTo(0, -10);
        graphics.lineTo(8, 5);
        graphics.lineTo(-8, 5);
        graphics.closePath();
        graphics.fill({ color: 0xffffff });
        break;

      case 'ARCHER': // 弓箭手 - 弓
        graphics.moveTo(-10, 0);
        graphics.quadraticCurveTo(0, -10, 10, 0);
        graphics.quadraticCurveTo(0, 10, -10, 0);
        graphics.stroke({ width: 2, color: 0xffffff });
        break;

      case 'MAGE': // 法师 - 法杖
        graphics.moveTo(0, -10);
        graphics.lineTo(0, 5);
        graphics.stroke({ width: 2, color: 0xffffff });
        graphics.circle(0, -10, 3);
        graphics.fill({ color: 0xffffff });
        break;

      default: // 其他 - 星形
        for (let i = 0; i < 5; i++) {
          const angle = (i * 72 - 90) * Math.PI / 180;
          const x = Math.cos(angle) * 8;
          const y = Math.sin(angle) * 8;
          if (i === 0) {
            graphics.moveTo(x, y);
          } else {
            graphics.lineTo(x, y);
          }
        }
        graphics.closePath();
        graphics.fill({ color: 0xffffff });
    }

    return graphics;
  }

  /**
   * 创建手牌区域
   */
  createHandArea(cards: Card[], onClick?: (index: number) => void): PIXI.Container {
    const container = new PIXI.Container();

    cards.forEach((card, index) => {
      const cardSprite = this.createCardSprite(card, true);

      // 计算位置
      cardSprite.x = index * (this.cardWidth + this.padding);
      cardSprite.y = 0;

      // 添加点击事件
      if (onClick) {
        cardSprite.on('pointerdown', () => {
          onClick(index);
        });
      }

      // 添加卡牌索引（使用属性存储）
      (cardSprite as any).userData = { index };

      container.addChild(cardSprite);
    });

    return container;
  }

  /**
   * 获取手牌区域尺寸
   */
  getHandAreaSize(cardCount: number): { width: number; height: number } {
    const width = cardCount * this.cardWidth + (cardCount - 1) * this.padding;
    const height = this.cardHeight;
    return { width, height };
  }
}
