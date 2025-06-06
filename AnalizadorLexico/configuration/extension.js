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

        // DEBUGGING: Mostrar rutas
        const goxFilePath = editor.document.fileName;
        const projectDir = path.dirname(goxFilePath);
        const mainScriptPath = path.join(projectDir, "main.py");
        
        console.log("GOX File:", goxFilePath);
        console.log("Project Dir:", projectDir);
        console.log("Main Script:", mainScriptPath);
        
        // Mostrar mensaje con las rutas para debugging
        vscode.window.showInformationMessage(`Ejecutando desde: ${projectDir}`);

        // Verificar que main.py existe
        const fs = require('fs');
        if (!fs.existsSync(mainScriptPath)) {
            vscode.window.showErrorMessage(`No se encontró main.py en: ${projectDir}\nBuscando: ${mainScriptPath}`);
            return;
        }

        const terminal = vscode.window.createTerminal("GOX Terminal");
        terminal.show(true);

        // Enviar comandos por separado para mejor compatibilidad
        terminal.sendText(`cd "${projectDir}"`);
        terminal.sendText(`python main.py "${path.basename(goxFilePath)}" --execute`);


    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};