#!/usr/bin/env node

const { spawn, execSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

// デバッグログ（stderr経由でMCPに影響しない）
function debug(msg) {
    if (process.env.DEBUG) {
        console.error(`[DEBUG] ${msg}`);
    }
}

// Pythonスクリプトのパス
const scriptPath = path.join(__dirname, '..', 'src', 'claude_cli_server.py');

// Windows環境かどうか
const isWindows = os.platform() === 'win32';

// Python実行可能ファイルを探す
function findPython() {
    debug(`Platform: ${os.platform()}`);
    
    if (isWindows) {
        // Windowsの場合、WSL経由で実行
        try {
            // WSLが利用可能か確認
            execSync('wsl --status', { stdio: 'ignore' });
            debug('WSL is available');
            
            // WSL内のPythonを確認
            try {
                execSync('wsl -e python3 --version', { stdio: 'ignore' });
                return ['wsl', '-e', 'python3'];
            } catch (e) {
                debug('python3 not found in WSL, trying python');
                execSync('wsl -e python --version', { stdio: 'ignore' });
                return ['wsl', '-e', 'python'];
            }
        } catch (e) {
            debug('WSL not available, trying native Python');
            // WSLが使えない場合は通常のPythonを試す
        }
    }
    
    // Unix系またはWSLが使えないWindows
    const pythonCommands = ['python3', 'python'];
    
    for (const cmd of pythonCommands) {
        try {
            execSync(`${cmd} --version`, { stdio: 'ignore' });
            debug(`Found Python: ${cmd}`);
            return [cmd];
        } catch (e) {
            // Continue to next option
        }
    }
    
    throw new Error('Python not found. Please install Python 3.8 or later.');
}

// Windowsパスを WSLパスに変換
function toWSLPath(winPath) {
    if (!isWindows) return winPath;
    
    // C:\path\to\file -> /mnt/c/path/to/file
    const normalized = winPath.replace(/\\/g, '/');
    const match = normalized.match(/^([A-Za-z]):/);
    if (match) {
        return `/mnt/${match[1].toLowerCase()}${normalized.substring(2)}`;
    }
    return normalized;
}

// メイン処理
function main() {
    try {
        const pythonCmd = findPython();
        debug(`Python command: ${pythonCmd.join(' ')}`);
        
        // WSL経由の場合はパスを変換
        let effectiveScriptPath = scriptPath;
        if (pythonCmd[0] === 'wsl') {
            effectiveScriptPath = toWSLPath(scriptPath);
            debug(`Converted path: ${effectiveScriptPath}`);
        }
        
        // スクリプトの存在確認
        if (!fs.existsSync(scriptPath)) {
            throw new Error(`Script not found: ${scriptPath}`);
        }
        
        // MCPサーバーを起動
        const args = [...pythonCmd.slice(1), effectiveScriptPath];
        const cmd = pythonCmd[0];
        
        debug(`Spawning: ${cmd} ${args.join(' ')}`);
        
        const proc = spawn(cmd, args, {
            stdio: 'inherit',
            env: { 
                ...process.env, 
                PYTHONUNBUFFERED: '1',
                // WSL経由の場合、必要な環境変数を設定
                ...(pythonCmd[0] === 'wsl' ? { WSLENV: 'PYTHONUNBUFFERED/u' } : {})
            }
        });
        
        proc.on('error', (err) => {
            console.error('Failed to start MCP server:', err.message);
            if (err.code === 'ENOENT') {
                console.error(`Command not found: ${cmd}`);
                if (isWindows) {
                    console.error('Make sure WSL is installed and Python is available in WSL');
                }
            }
            process.exit(1);
        });
        
        proc.on('exit', (code) => {
            debug(`Process exited with code: ${code}`);
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
        console.error('Stack:', err.stack);
        process.exit(1);
    }
}

// 起動
main();