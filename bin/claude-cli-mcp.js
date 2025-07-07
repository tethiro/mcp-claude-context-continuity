#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

// Pythonスクリプトのパス
const scriptPath = path.join(__dirname, '..', 'src', 'claude_cli_server.py');

// Python実行可能ファイルを探す
function findPython() {
    const pythonCommands = ['python3', 'python'];
    
    for (const cmd of pythonCommands) {
        try {
            const result = require('child_process').execSync(`which ${cmd} 2>/dev/null || where ${cmd} 2>nul`, {
                encoding: 'utf8',
                stdio: ['pipe', 'pipe', 'ignore']
            });
            if (result.trim()) {
                return cmd;
            }
        } catch (e) {
            // Continue to next option
        }
    }
    
    throw new Error('Python not found. Please install Python 3.8 or later.');
}

// メイン処理
function main() {
    try {
        const python = findPython();
        console.error(`Using Python: ${python}`);
        
        // MCPサーバーを起動
        const proc = spawn(python, [scriptPath], {
            stdio: 'inherit',
            env: { ...process.env, PYTHONUNBUFFERED: '1' }
        });
        
        proc.on('error', (err) => {
            console.error('Failed to start MCP server:', err.message);
            process.exit(1);
        });
        
        proc.on('exit', (code) => {
            process.exit(code || 0);
        });
        
        // シグナルハンドリング
        process.on('SIGINT', () => {
            proc.kill('SIGINT');
        });
        
        process.on('SIGTERM', () => {
            proc.kill('SIGTERM');
        });
        
    } catch (err) {
        console.error('Error:', err.message);
        process.exit(1);
    }
}

main();