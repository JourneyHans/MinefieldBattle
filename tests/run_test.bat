@echo off
REM 运行怪物战力分布测试
cd /d %~dp0\..
python tests\test_monster_power_distribution.py
pause

