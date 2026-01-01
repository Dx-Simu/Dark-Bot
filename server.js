const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const kill = require('tree-kill');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static('public'));

const PROJECTS_DIR = path.join(__dirname, 'projects');
const LOGS_DIR = path.join(__dirname, 'logs');
[PROJECTS_DIR, LOGS_DIR].forEach(dir => { if (!fs.existsSync(dir)) fs.mkdirSync(dir); });

let activeProcesses = {};

// লগে ডেটা সেভ করার ফাংশন
function saveToLog(filename, data) {
    const logPath = path.join(LOGS_DIR, `${filename}.log`);
    fs.appendFileSync(logPath, `[${new Date().toLocaleString()}] ${data}\n`);
}

io.on('connection', (socket) => {
    // ১. স্ক্রিপ্ট রান এবং অটো-রিস্টার্ট লজিক
    const startScript = (filename) => {
        if (activeProcesses[filename]) kill(activeProcesses[filename].pid);

        const child = spawn('python', ['-u', path.join(PROJECTS_DIR, filename)]);
        activeProcesses[filename] = { pid: child.pid, startTime: Date.now() };

        io.emit('status-change', { filename, status: 'Running' });

        child.stdout.on('data', (data) => {
            const out = data.toString();
            saveToLog(filename, out);
            io.emit('terminal-data', { filename, data: out });
        });

        child.stderr.on('data', (data) => {
            const err = data.toString();
            saveToLog(filename, `ERROR: ${err}`);
            io.emit('terminal-data', { filename, data: err, type: 'error' });
        });

        child.on('close', (code) => {
            if (activeProcesses[filename]) {
                delete activeProcesses[filename];
                io.emit('status-change', { filename, status: 'Crashed' });
                if (code !== 0 && code !== null) {
                    setTimeout(() => startScript(filename), 5000); // Auto-Restart
                }
            }
        });
    };

    socket.on('run-script', ({ filename }) => startScript(filename));

    socket.on('stop-script', ({ filename }) => {
        if (activeProcesses[filename]) {
            const pid = activeProcesses[filename].pid;
            delete activeProcesses[filename];
            kill(pid);
            io.emit('status-change', { filename, status: 'Stopped' });
        }
    });

    // ২. ইন্টারঅ্যাকটিভ টার্মিনাল কমান্ড
    socket.on('terminal-input', (command) => {
        exec(command, { cwd: PROJECTS_DIR }, (err, stdout, stderr) => {
            socket.emit('terminal-data', { data: stdout || stderr, type: err ? 'error' : 'system' });
        });
    });

    // ৩. গিটহাব সিঙ্ক
    socket.on('github-sync', ({ repoUrl }) => {
        const folderName = `repo_${Date.now()}`;
        exec(`git clone ${repoUrl} ${folderName} && cp -r ${folderName}/* . && rm -rf ${folderName}`, { cwd: PROJECTS_DIR }, (err) => {
            socket.emit('terminal-data', { data: err ? "Sync Failed" : "GitHub Sync Success!", type: err ? 'error' : 'system' });
        });
    });
});

// API Routes
app.get('/api/projects', (req, res) => {
    const files = fs.readdirSync(PROJECTS_DIR).filter(f => f.endsWith('.py'));
    res.json(files.map(f => ({ name: f, status: activeProcesses[f] ? 'Running' : 'Idle' })));
});

app.post('/api/save', (req, res) => {
    fs.writeFileSync(path.join(PROJECTS_DIR, req.body.filename), req.body.content);
    res.json({ success: true });
});

app.get('/api/read/:name', (req, res) => {
    res.send(fs.readFileSync(path.join(PROJECTS_DIR, req.params.name), 'utf-8'));
});

server.listen(3000, () => console.log('Master Server Running on Port 3000'));
