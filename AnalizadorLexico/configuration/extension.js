const vscode = require("vscode");
const path = require("path");

function activate(context) {
    let disposable = vscode.commands.registerCommand("extension.runFactorize", () => {
        vscode.window.showInformationMessage("Ejecutando factorize.gox...");

        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage("¡No se encontró una carpeta de trabajo!");
            return;
        }

        const projectPath = workspaceFolders[0].uri.fsPath;
        const lexerPath = path.join(projectPath, "main.py");
        const fileToAnalyze = path.join(projectPath, "factorize.gox");

        // Crear o reutilizar una terminal
        const terminal = vscode.window.createTerminal(`GOX Terminal`);
        terminal.show(true);
        terminal.sendText(`python "${lexerPath}" "${fileToAnalyze}"`);
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
