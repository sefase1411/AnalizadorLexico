const vscode = require("vscode");
const path = require("path");

function activate(context) {
    let disposable = vscode.commands.registerCommand("extension.runFactorize", () => {
        const pythonPath = vscode.workspace.getConfiguration("python").get("pythonPath") || "python";

        // Carpeta de trabajo deseada (exacta):
        const workingDir = "C:\\Users\\sefas\\OneDrive\\Documents\\compiladores\\AnalizadorLexico\\AnalizadorLexico";

        const lexerPath = path.join(workingDir, "main.py");
        const fileToAnalyze = path.join(workingDir, "factorize.gox");

        const terminal = vscode.window.createTerminal("GOX Terminal");
        terminal.show(true);

        // 🔑 Comando unido en una sola línea con ";" para PowerShell:
        const fullCommand = `cd "${workingDir}"; & "${pythonPath}" "${lexerPath}" "${fileToAnalyze}"`;

        terminal.sendText(fullCommand);
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
