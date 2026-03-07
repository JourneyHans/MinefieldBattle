import { CellEntity } from './Cell';
import { CellType, TaskCell as TaskCellType, TaskType } from '../../types';

/**
 * 任务格子 - 通关任务
 */
export class TaskCellEntity extends CellEntity implements TaskCellType {
  readonly type = CellType.TASK;
  taskType: TaskType;
  completed: boolean;       // 任务是否完成
  confirmed: boolean;       // 任务是否已确认

  constructor(row: number, col: number, taskType: TaskType) {
    super(row, col, CellType.TASK);
    this.taskType = taskType;
    this.completed = false;
    this.confirmed = false;
  }

  // 检查任务是否完成
  isCompleted(): boolean {
    return this.completed;
  }

  // 检查任务是否已确认
  isConfirmed(): boolean {
    return this.confirmed;
  }

  // 完成任务
  complete(): void {
    this.completed = true;
  }

  // 确认任务
  confirm(): void {
    if (this.completed) {
      this.confirmed = true;
    }
  }

  // 检查是否可以确认
  canConfirm(): boolean {
    return this.completed && !this.confirmed;
  }

  // 重置任务状态
  reset(): void {
    this.completed = false;
    this.confirmed = false;
  }

  // 克隆任务格子
  clone(): TaskCellEntity {
    const cloned = new TaskCellEntity(this.row, this.col, this.taskType);
    cloned.state = this.state;
    cloned.unit = this.unit ? { ...this.unit } : null;
    cloned.completed = this.completed;
    cloned.confirmed = this.confirmed;
    return cloned;
  }

  // 转换为DTO
  toDTO(): TaskCellType {
    return {
      row: this.row,
      col: this.col,
      type: this.type,
      state: this.state,
      taskType: this.taskType,
      completed: this.completed,
      confirmed: this.confirmed,
      unit: this.unit,
    };
  }
}
