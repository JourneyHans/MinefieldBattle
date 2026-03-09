# 部署说明

## 方法1：GitHub Actions自动部署（推荐）

如果GitHub Actions配置正确，每次推送到 `feat/demo_v2` 分支会自动部署。

## 方法2：本地手动部署

如果GitHub Actions无法工作，可以手动部署：

```bash
# 1. 构建项目
npm run build

# 2. 部署到GitHub Pages
npm run deploy
```

这会自动将 `dist` 目录推送到 `gh-pages` 分支。

## 方法3：使用脚本部署

创建部署脚本 `deploy.sh`:

```bash
#!/bin/bash
cd demo_v2
npm run build
npm run deploy
```

运行:
```bash
bash deploy.sh
```

## 访问地址

部署成功后访问: https://journeyhans.github.io/MinefieldBattle/demo_v2/

## 故障排查

如果部署失败，检查：

1. GitHub仓库设置 > Actions > General > Workflow permissions
   - 确保 "Read and write permissions" 已启用
   - 如果有 "Allow GitHub Actions to create and approve pull requests"，也启用它

2. GitHub仓库设置 > Pages
   - Source: Deploy from a branch
   - Branch: gh-pages + /demo_v2

3. 仓库是否为public（private仓库的GitHub Pages需要付费账户）
