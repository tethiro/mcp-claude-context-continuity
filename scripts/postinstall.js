const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('📦 Installing Python dependencies...');

// requirements.txtのパス
const requirementsPath = path.join(__dirname, '..', 'requirements.txt');

if (!fs.existsSync(requirementsPath)) {
    console.error('❌ requirements.txt not found');
    process.exit(1);
}

try {
    // pip installを実行
    execSync(`pip install -r "${requirementsPath}"`, {
        stdio: 'inherit'
    });
    console.log('✅ Python dependencies installed successfully');
} catch (error) {
    console.error('❌ Failed to install Python dependencies');
    console.error('Please run: pip install -r requirements.txt');
    // エラーでも続行（警告のみ）
}