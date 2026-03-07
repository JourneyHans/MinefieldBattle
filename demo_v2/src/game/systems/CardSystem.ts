import { Card, UnitType } from '../../types';
import { CardEntity } from '../entities';
import { CARD_CONFIG, CARD_DEAL_WEIGHTS } from '../../config/gameConfig';
import { weightedRandomString, generateId } from '../utils/WeightedRandom';

/**
 * 卡牌系统
 */
export class CardSystem {
  /**
   * 发牌 - 生成随机卡牌
   */
  dealCards(count: number): Card[] {
    const cards: Card[] = [];

    for (let i = 0; i < count; i++) {
      const unitType = this.generateRandomUnitType();
      const card = new CardEntity(unitType);
      cards.push(card.toDTO());
    }

    return cards;
  }

  /**
   * 生成随机兵种类型（使用加权随机）
   */
  private generateRandomUnitType(): UnitType {
    return weightedRandomString(CARD_DEAL_WEIGHTS);
  }

  /**
   * 检查卡牌是否可以部署到指定格子
   */
  canDeployCard(card: Card, cellNumber: number): boolean {
    return card.power >= cellNumber;
  }

  /**
   * 获取卡牌部署后的实际战力
   */
  getDeployedPower(card: Card, cellNumber: number): number {
    if (!this.canDeployCard(card, cellNumber)) {
      return 0;
    }

    // 如果卡牌战力大于格子数字，实际战力等于格子数字
    return Math.min(card.power, cellNumber);
  }

  /**
   * 创建卡牌实体
   */
  createCard(unitType: UnitType): Card {
    const cardEntity = new CardEntity(unitType);
    return cardEntity.toDTO();
  }

  /**
   * 生成完整的卡组（用于测试）
   */
  generateFullDeck(): Card[] {
    const cards: Card[] = [];

    // 每种兵种生成多张卡牌
    const unitTypes = Object.values(UnitType);
    for (const unitType of unitTypes) {
      for (let i = 0; i < 5; i++) {
        cards.push(this.createCard(unitType));
      }
    }

    // 洗牌
    return this.shuffleCards(cards);
  }

  /**
   * 洗牌
   */
  shuffleCards(cards: Card[]): Card[] {
    const shuffled = [...cards];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * 从手牌中移除卡牌
   */
  removeCardFromHand(hand: Card[], cardIndex: number): Card[] {
    if (cardIndex < 0 || cardIndex >= hand.length) {
      return hand;
    }

    const newHand = [...hand];
    newHand.splice(cardIndex, 1);
    return newHand;
  }

  /**
   * 检查手牌是否已满
   */
  isHandFull(hand: Card[]): boolean {
    return hand.length >= CARD_CONFIG.MAX_HAND_SIZE;
  }
}
