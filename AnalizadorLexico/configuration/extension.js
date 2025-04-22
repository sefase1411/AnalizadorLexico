const vscode = require("vscode");
const path = require("path");

function activate(context) {
    let disposable = vscode.commands.registerCommand("extension.runFactorize", () => {
        const pythonPath = vscode.workspace.getConfiguration("python").get("pythonPath") || "python";

        const editor = vscode.window.activeTextEditor;
        if (!editor || !editor.document.fileName.endsWith(".gox")) {
            vscode.window.showErrorMessage("Abre un archivo .gox para ejecutarlo.");
            return;
        }

        // Ruta fija al main.py
        const mainScriptPath = "C:\\Users\\sefas\\OneDrive\\Documents\\compiladores\\AnalizadorLexico\\AnalizadorLexico\\main.py";

        // Archivo .gox actualmente abierto
        const fileToAnalyze = editor.document.fileName;

        const terminal = vscode.window.createTerminal("GOX Terminal");
        terminal.show(true);

        // Ejecuta en PowerShell: ir a la carpeta del main.py y lanzar Python con ambos paths
        const fullCommand = `cd "${path.dirname(mainScriptPath)}"; & "${pythonPath}" "${mainScriptPath}" "${fileToAnalyze}"`;

        terminal.sendText(fullCommand);
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
