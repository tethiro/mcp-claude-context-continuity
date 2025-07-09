# Security Policy

## Supported Versions

Currently supported versions for security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in MCP Claude Context Continuity, please report it responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to: tethiro@gmail.com
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Resolution Timeline**: Depending on severity:
  - Critical: 1-2 weeks
  - High: 2-4 weeks
  - Medium/Low: 4-8 weeks

### Security Considerations

This project interacts with:
- Claude CLI (external process)
- File system (for context files)
- MCP protocol (stdio communication)

Please ensure:
- Claude CLI is from official sources
- File paths are properly validated
- Sensitive information is not logged

## Security Best Practices for Users

1. **Environment Variables**: Never commit `CLAUDE_PATH` with sensitive paths
2. **Session IDs**: Treat session IDs as sensitive information
3. **File Permissions**: Ensure proper permissions on configuration files
4. **Logging**: Review and clean `claude_command_debug.log` regularly

## Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and announced via:
- NPM package updates
- GitHub releases
- Security advisory (for critical issues)

---

# セキュリティポリシー

## サポートされているバージョン

セキュリティアップデートが提供されるバージョン：

| バージョン | サポート状況        |
| --------- | ------------------ |
| 1.0.x     | :white_check_mark: |
| < 1.0     | :x:                |

## 脆弱性の報告

MCP Claude Context Continuityで脆弱性を発見した場合は、責任を持って報告してください。

### 報告方法

1. セキュリティ脆弱性について**公開のGitHub Issue を作成しないでください**
2. 以下にメールを送信: tethiro@gmail.com
3. 以下の情報を含めてください：
   - 脆弱性の説明
   - 再現手順
   - 潜在的な影響
   - 修正案（もしあれば）

### 対応について

- **受領確認**: 48時間以内
- **初期評価**: 1週間以内
- **解決スケジュール**: 深刻度に応じて
  - 緊急: 1-2週間
  - 高: 2-4週間
  - 中/低: 4-8週間

### セキュリティ上の考慮事項

このプロジェクトは以下と連携します：
- Claude CLI（外部プロセス）
- ファイルシステム（コンテキストファイル用）
- MCPプロトコル（stdio通信）

以下を確認してください：
- Claude CLIが公式ソースからのものであること
- ファイルパスが適切に検証されていること
- 機密情報がログに記録されていないこと

## ユーザー向けセキュリティベストプラクティス

1. **環境変数**: 機密性の高いパスを含む`CLAUDE_PATH`をコミットしない
2. **セッションID**: セッションIDを機密情報として扱う
3. **ファイル権限**: 設定ファイルに適切な権限を設定
4. **ログ**: `claude_command_debug.log`を定期的に確認・削除

## アップデート

セキュリティアップデートはパッチバージョン（例: 1.0.1, 1.0.2）としてリリースされ、以下で通知されます：
- NPMパッケージ更新
- GitHubリリース
- セキュリティアドバイザリ（重大な問題の場合）